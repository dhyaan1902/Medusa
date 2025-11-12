import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import threading
import os
import platform
from medusa_core import load_config, save_config, run_downloads, DEFAULT_WALLDIR

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class MedusaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Medusa v3.1 - New GUI")
        self.geometry("1200x800")

        self.cfg = load_config()
        self.query_rows = []

        self.build_ui()

    def build_ui(self):
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(expand=True, fill="both")
        self.tabs.add("Home")
        self.tabs.add("Settings")

        self.home_tab = self.tabs.tab("Home")
        self.settings_tab = self.tabs.tab("Settings")

        self.build_home_tab()
        self.build_settings_tab()

    # ==================== HOME TAB ====================
    def build_home_tab(self):
        top_frame = ctk.CTkFrame(self.home_tab, fg_color="transparent")
        top_frame.pack(fill="x", pady=8, padx=8)
        self.download_btn = ctk.CTkButton(top_frame, text="DOWNLOAD NOW", command=self.download_now, width=180)
        self.download_btn.pack(side="left", padx=8)
        self.progress_var = ctk.DoubleVar(value=0)
        self.progress_bar = ctk.CTkProgressBar(top_frame, variable=self.progress_var)
        self.progress_bar.pack(fill="x", expand=True, side="left", padx=8)

        self.query_container = ctk.CTkFrame(self.home_tab)
        self.query_container.pack(fill="x", padx=8, pady=6)
        self.query_rows_frame = ctk.CTkFrame(self.query_container, fg_color="transparent")
        self.query_rows_frame.pack(fill="x", pady=4)

        self.add_query_button = ctk.CTkButton(self.query_container, text="+ Add Query", command=self.add_query_row)
        self.add_query_button.pack(pady=4)

        for q in self.cfg.get("queries", []):
            self.add_query_row(q.get("query", ""), str(q.get("count",1)), q.get("api", "Pexels"))

        gallery_wrap = ctk.CTkFrame(self.home_tab, fg_color="transparent")
        gallery_wrap.pack(fill="both", expand=True, padx=8, pady=8)
        self.gallery_canvas = ctk.CTkScrollableFrame(gallery_wrap, corner_radius=12)
        self.gallery_canvas.pack(fill="both", expand=True)
        self.load_gallery()

    def add_query_row(self, query="", count="1", api="Pexels"):
        row = ctk.CTkFrame(self.query_rows_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)
        qvar = ctk.StringVar(value=query)
        cvar = ctk.StringVar(value=count)
        avar = ctk.StringVar(value=api)

        ctk.CTkEntry(row, textvariable=qvar, placeholder_text="Query", width=380).pack(side="left", padx=4)
        ctk.CTkEntry(row, textvariable=cvar, width=70).pack(side="left", padx=4)
        ctk.CTkOptionMenu(row, values=["Unsplash","Pixabay","Pexels","NASA","ImageSearch"], variable=avar, width=120).pack(side="left", padx=4)
        remove_btn = ctk.CTkButton(row, text="−", width=36, fg_color="#ff3b30", hover_color="#ff6b62", command=lambda r=row: self.remove_query_row(r))
        remove_btn.pack(side="right", padx=4)

        self.query_rows.append((row, qvar, cvar, avar))

    def remove_query_row(self, row):
        for t in list(self.query_rows):
            if t[0] == row:
                t[0].destroy()
                self.query_rows.remove(t)
                break

    def download_now(self):
        self.save_settings()
        self.progress_var.set(0)
        threading.Thread(target=self._download_thread, daemon=True).start()

    def _download_thread(self):
        total_images = sum(int(cv.get()) for (_, _, cv, _) in self.query_rows)
        downloaded_count = 0

        def show_progress(path):
            nonlocal downloaded_count
            downloaded_count += 1
            self.after(0, lambda: self.progress_var.set(downloaded_count/total_images))
            self.after(0, lambda: self.add_thumb(path))

        run_downloads(self.cfg, show_progress=show_progress)

    def load_gallery(self):
        # Clear previous widgets
        for w in self.gallery_canvas.winfo_children():
            w.destroy()

        wall_dir = self.cfg.get("wall_dir", DEFAULT_WALLDIR)
        try:
            files = sorted([os.path.join(wall_dir, f) for f in os.listdir(wall_dir)], reverse=True)
        except Exception:
            files = []

        col, r = 0, 0
        for p in files:
            try:
                img = Image.open(p)
                img.thumbnail((360, 240))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(360, 240))

                # Frame wraps image + delete button
                frame = ctk.CTkFrame(self.gallery_canvas, corner_radius=12)
                frame.grid(row=r, column=col, padx=6, pady=6)

                # Image button: click to set wallpaper
                btn = ctk.CTkButton(
                    frame,
                    image=ctk_img,
                    text="",
                    width=360,
                    height=240,
                    corner_radius=12,
                    command=lambda pp=p: self.set_wallpaper(pp)
                )
                btn.image = ctk_img
                btn.pack()

                # Delete button
                del_btn = ctk.CTkButton(
                    frame,
                    text="🗑 Delete",
                    fg_color="#b91c1c",
                    hover_color="#ef4444",
                    command=lambda pp=p, fr=frame: self.delete_image(pp, fr)
                )
                del_btn.pack(pady=4)

                col += 1
                if col >= 3:
                    col = 0
                    r += 1
            except Exception:
                pass


    def add_thumb(self, path):
        self.load_gallery()

    def set_wallpaper(self, path):
        system = platform.system()
        if system == "Windows":
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(20,0,path,3)
        elif system == "Darwin":
            os.system(f'osascript -e \'tell app "Finder" to set desktop picture to POSIX file "{path}"\'')
        else:
            os.system(f"gsettings set org.gnome.desktop.background picture-uri 'file://{path}'")
    
    def delete_image(self, path, frame):
    # Confirmation popup
        if messagebox.askyesno("Delete Image", f"Delete '{os.path.basename(path)}'?"):
            try:
                os.remove(path)        # remove file from disk
                frame.destroy()        # remove frame from GUI
                print(f"[Medusa] Deleted {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete image:\n{e}")

    # ==================== SETTINGS TAB ====================
    def build_settings_tab(self):
        pad = dict(padx=12, pady=8)
        folder_frame = ctk.CTkFrame(self.settings_tab, corner_radius=12)
        folder_frame.pack(fill="x", **pad)
        ctk.CTkLabel(folder_frame, text="Wallpaper Directory", font=("Helvetica",12,"bold")).pack(anchor="w", padx=8, pady=6)
        self.wall_dir_var = ctk.StringVar(value=self.cfg.get("wall_dir"))
        ctk.CTkLabel(folder_frame, textvariable=self.wall_dir_var).pack(anchor="w", padx=8)
        ctk.CTkButton(folder_frame, text="Change...", command=self.change_folder, width=120).pack(anchor="e", padx=8, pady=6)

        api_frame = ctk.CTkFrame(self.settings_tab, corner_radius=12)
        api_frame.pack(fill="x", **pad)
        ctk.CTkLabel(api_frame, text="API Keys", font=("Helvetica",12,"bold")).pack(anchor="w", padx=8, pady=6)
        self.api_vars = {}
        for name in ["Unsplash","Pixabay","Pexels","NASA"]:
            row = ctk.CTkFrame(api_frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=4)
            ctk.CTkLabel(row, text=f"{name}:", width=90).pack(side="left")
            v = ctk.StringVar(value=self.cfg.get("apis", {}).get(name, ""))
            self.api_vars[name] = v
            ctk.CTkEntry(row, textvariable=v, width=460).pack(side="left", padx=8)

        auto_frame = ctk.CTkFrame(self.settings_tab, corner_radius=12)
        auto_frame.pack(fill="x", **pad)
        self.auto_var = ctk.BooleanVar(value=self.cfg.get("auto_refresh", False))
        self.preserve_var = ctk.BooleanVar(value=True)
        self.refresh_var = ctk.StringVar(value=str(self.cfg.get("refresh_hours",24)))

        ctk.CTkCheckBox(auto_frame, text="Enable Auto Refresh", variable=self.auto_var).pack(anchor="w", padx=8, pady=4)
        row = ctk.CTkFrame(auto_frame, fg_color="transparent")
        row.pack(anchor="w", padx=8, pady=4)
        ctk.CTkLabel(row, text="Every").pack(side="left")
        ctk.CTkEntry(row, textvariable=self.refresh_var, width=70).pack(side="left", padx=4)
        ctk.CTkLabel(row, text="hours").pack(side="left")
        ctk.CTkCheckBox(auto_frame, text="Preserve Pictures on Auto Refresh", variable=self.preserve_var).pack(anchor="w", padx=8, pady=4)

        ctk.CTkButton(self.settings_tab, text="Save Settings", command=self.save_settings, width=160).pack(padx=12, pady=12, anchor="e")

    def change_folder(self):
        path = filedialog.askdirectory(initialdir=self.cfg.get("wall_dir", DEFAULT_WALLDIR))
        if path:
            self.wall_dir_var.set(path)
            self.cfg["wall_dir"] = path

    def save_settings(self):
        self.cfg["wall_dir"] = self.wall_dir_var.get()
        self.cfg["apis"] = {k:v.get() for k,v in self.api_vars.items()}
        qs = []
        for (_, qv, cv, avar) in self.query_rows:
            try:
                cnt = int(cv.get())
            except Exception:
                cnt = 1
            qs.append({"query": qv.get().strip(), "count": cnt, "api": avar.get()})
        self.cfg["queries"] = qs
        self.cfg["auto_refresh"] = self.auto_var.get()
        try:
            self.cfg["refresh_hours"] = float(self.refresh_var.get())
        except Exception:
            self.cfg["refresh_hours"] = 24.0
        save_config(self.cfg)
        messagebox.showinfo("Medusa","Settings saved")

if __name__ == "__main__":
    app = MedusaApp()
    app.mainloop()
