#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WebServer.h>
#include <EEPROM.h>
#include "HX711.h"

// ---------------- Configuration ----------------

#define BUTTON_PIN 0               // GPIO pin for the config button
#define EEPROM_SIZE 512
#define INIT_HOLD_TIME 3000       // 3 seconds
#define AP_SSID "ESP32_Config"
#define AP_PASSWORD "password"

const int LOADCELL_DOUT_PIN = D4;
const int LOADCELL_SCK_PIN = D5;
const float calibration_factor = -9950;
boolean Debug_Mode = true;

HX711 scale;
WebServer server(8080);

// Stored credentials
String stored_ssid = "";
String stored_password = "";
String stored_hash = "";

// Button hold tracking
unsigned long buttonPressStart = 0;
bool buttonHeld = false;

// ---------------- Function Declarations ----------------

void setup_wifi();
void enterInitializationMode();
void handleConfigPost();
void sendData(float weight);

// ---------------- Setup ----------------

void setup() {
  Serial.begin(115200);
  EEPROM.begin(EEPROM_SIZE);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  // Read stored WiFi and hash
  stored_ssid = EEPROM.readString(0);
  stored_password = EEPROM.readString(100);
  stored_hash = EEPROM.readString(200);

  if (stored_ssid.length() == 0 || stored_password.length() == 0) {
    Serial.println("No WiFi credentials found. Entering setup mode.");
    enterInitializationMode();
    return;
  }

  setup_wifi();

  Serial.println("Initializing scale...");
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale(calibration_factor);
  scale.tare();

  Serial.println("Setup complete!");
}

// ---------------- Loop ----------------

void loop() {
  // ---- Button Hold Detection in loop() ----
  if (Debug_Mode == true || digitalRead(BUTTON_PIN) == LOW) {
    if (buttonPressStart == 0) {
      buttonPressStart = millis();
    } else if (Debug_Mode == true || (!buttonHeld && millis() - buttonPressStart >= INIT_HOLD_TIME)) {
      buttonHeld = true;
      Serial.println("Long press detected. Entering Initialization Mode...");
      enterInitializationMode(); // will not return
    }
  } else {
    buttonPressStart = 0;
    buttonHeld = false;
  }

  // ---- Main Task ----
  if (WiFi.status() == WL_CONNECTED) {
    float weight = scale.get_units(5);
    Serial.printf("Weight: %.1f lbs\n", weight);
    sendData(weight);
  } else {
    Serial.println("WiFi disconnected. Reconnecting...");
    setup_wifi();
  }

  delay(5000);
}

// ---------------- Setup WiFi ----------------

void setup_wifi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(stored_ssid);
  WiFi.begin(stored_ssid.c_str(), stored_password.c_str());

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected!");
    Serial.println("IP: " + WiFi.localIP().toString());
    Debug_Mode = false;
  } else {
    Debug_Mode = true;
    Serial.println("\nFailed to connect.");
  }
}

// ---------------- Send Data ----------------

void sendData(float weight) {
  HTTPClient http;

  StaticJsonDocument<200> doc;
  doc["sensor_id"] = String("LameScore_") + WiFi.macAddress();
  doc["weight_lbs"] = String(weight, 1);
  doc["timestamp"] = millis();
  doc["hash"] = stored_hash;

  String jsonString;
  serializeJson(doc, jsonString);

  http.begin("https://");  // your endpoint here
  http.addHeader("Content-Type", "application/json");
  http.addHeader("x-api-key", "xxxxxx");  // your API key here

  int httpCode = http.POST(jsonString);

  if (httpCode > 0) {
    Serial.println("HTTP Code: " + String(httpCode));
    Serial.println("Response: " + http.getString());
  } else {
    Serial.println("HTTP Error: " + String(httpCode));
  }

  http.end();
}

// ---------------- Initialization Mode ----------------

void enterInitializationMode() {
  Serial.println("Starting WiFi AP for config...");
  WiFi.disconnect(true);
  WiFi.mode(WIFI_AP);
  delay(1000);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP: ");
  Serial.println(IP);

  server.on("/config", HTTP_POST, handleConfigPost);
  server.begin();
  Serial.println("HTTP server started. POST to /config with SSID, password, hash");

  while (true) {
    server.handleClient();
    delay(10);
  }
}

// ---------------- Handle POST /config ----------------

void handleConfigPost() {
  if (server.hasArg("plain") == false) {
    server.send(400, "text/plain", "Missing body");
    return;
  }

  StaticJsonDocument<300> doc;
  DeserializationError error = deserializeJson(doc, server.arg("plain"));
  if (error) {
    server.send(400, "text/plain", "Invalid JSON");
    return;
  }

  String ssid = doc["SSID"];
  String password = doc["password"];
  String hash = doc["hash"];

  if (ssid.length() == 0 || password.length() == 0 || hash.length() == 0) {
    server.send(400, "text/plain", "Missing fields");
    return;
  }

  // Debug output
  if (Debug_Mode == true) {
    Serial.println("Received configuration:");
    Serial.println("  SSID: " + ssid);
    Serial.println("  Password: " + password);
    Serial.println("  Hash: " + hash);
  }

  EEPROM.writeString(0, ssid);
  EEPROM.writeString(100, password);
  EEPROM.writeString(200, hash);
  EEPROM.commit();

  Debug_Mode = false;
  server.send(200, "text/plain", "Configuration saved. Rebooting...");
  delay(1000);
  ESP.restart();
}

