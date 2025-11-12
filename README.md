
# Medusa – Smart Wallpaper Downloader

Medusa is a powerful, easy-to-use Python GUI application to fetch high-quality wallpapers from multiple sources. It provides a smooth and modern interface for managing your desktop backgrounds and supports advanced image search without the need for API keys.

---

## Features

- **Multiple Sources Support:** Download wallpapers from Unsplash, Pexels, NASA, and other popular platforms.
- **ImageSearch Integration:** The recommended method to fetch wallpapers. Works without any API keys and provides higher-quality images than most sources.
- **Pixabay Support:** Available but **does not work** due to API restrictions.
- **Simple GUI:** Built with **CustomTkinter** for a modern look and feel.
- **Gallery View:** View downloaded wallpapers directly in the app.
- **Direct Delete Option:** Delete wallpapers directly from the app with a single click.
- **Download Progress:** Shows a progress bar during downloads with a "Download has started" message for better feedback.
- **Auto-Refresh & Preserve Pictures:** Automatically fetch new wallpapers while preserving previously downloaded ones.
- **Cross-Platform Path Support:** Works on Linux and Windows. Default download folder:
  - Linux/macOS: `~/Medusa/Wallpapers`
  - Windows: `C:\Medusa\Wallpapers`
  - You can change the download path in the settings.
- **Future Features in Development:**
  - Resolution selection for wallpapers
  - More advanced filtering options
  - Additional source integrations

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/medusa.git
   cd medusa
````

2. **Install requirements:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create default wallpaper folder:**

   ```bash
   mkdir -p Medusa/Wallpapers
   ```

   (Windows users can create `C:\Medusa\Wallpapers` or change the path in settings)

4. **Run the GUI:**

   ```bash
   python medusa_gui.py
   ```

---

## Usage Recommendations

* **Best Quality:** Use the **ImageSearch** option – it requires **no API key** and fetches wallpapers in high resolutions.
* **Unsplash:** Works well with an API key.
* **Pixabay:** Not recommended as it often fails due to API limitations.

---

## How It Works

1. Enter your search query (e.g., `nature`, `space`, `anime`) in the app.
2. Choose your preferred source or use **ImageSearch**.
3. Set the number of images to download.
4. Click **Download Now**. Progress will be shown.
5. Access your downloaded images in the **Gallery** tab.
6. Delete any unwanted wallpapers directly from the gallery.

---

## Notes

* **Image Quality:** ImageSearch prioritizes high-resolution wallpapers with keywords like `4K`, `1920x1080`, `wallpaper`, and `wide`.
* **Cross-platform:** Works on Linux, Windows, and macOS (requires Python 3.12+).
* **API Keys:** If using sources like Unsplash or Pexels, ensure you provide valid API keys in settings tab
* **Preserving Wallpapers:** Use the **Preserve Pictures** option to avoid overwriting previous downloads during auto-refresh.

---

## Requirements

* Python 3.12+
* CustomTkinter
* Pillow
* Requests
* BeautifulSoup4
* lxml

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## Contributing

We are actively developing Medusa. Future features include resolution selection, additional sources, and improved filtering options. Contributions are welcome!

---

## License

Medusa is currently open-source under the MIT License.

```
```
