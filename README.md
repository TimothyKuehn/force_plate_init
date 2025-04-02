#  WiFi HTTP Request Sender

This is a simple Python GUI tool for sending HTTP POST requests over a local network, built with:

- `tkinter` + `ttkbootstrap` (modern themed widgets)
- `requests` for HTTP
- Packaged via `PyInstaller` for distribution

---

##  Requirements

Make sure you have Python 3.7+ installed.

### 1. Install dependencies:

```bash
pip install ttkbootstrap requests
```

---

##  Running the App (During Development)

```bash
python main.py
```

>  Make sure `icon.png` exists in the same folder as `main.py` — it's used for the window icon.

---

## 🛠Building with PyInstaller

### 1. Install PyInstaller:

```bash
pip install pyinstaller
```

### 2. Build the executable:

```bash
pyinstaller --noconfirm --onefile --windowed \
    --add-data "icon.png:." \
    main.py
```

- `--onefile`: Creates a single executable
- `--windowed`: Hides the terminal window (for GUI apps)
- `--add-data`: Ensures resources like icons are included  
  Format:
  - **Windows**: `"icon.png;."`

---

## Running the Built App

After building, the output executable is in the `dist/` folder:

```bash
./dist/main
```


---

## Linux Notes

- `icon.ico` is **Windows-only**  Comment out any lines related to it if you want to run on Linux

## Project Structure

```
your_project/
│
├── main.py
├── icon.png
└── README.md
```
