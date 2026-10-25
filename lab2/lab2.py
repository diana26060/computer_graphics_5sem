import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw

class GraphicsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР2 Вариант 4: Сегментация + Гистограммы")
        self.root.geometry("1300x900")
        self.image = None
        self.gray = None
        self.setup_ui()

    def setup_ui(self):
        top = ttk.Frame(self.root, padding=5)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(top, text="Загрузить изображение", command=self.load_image).pack(side=tk.LEFT, padx=5)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab_seg = ttk.Frame(self.notebook)
        self.tab_hist = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_seg, text="1. Сегментация (точки, линии, границы)")
        self.notebook.add(self.tab_hist, text="2. Гистограммы и контрастирование")

        self.setup_seg_ui(self.tab_seg)
        self.setup_hist_ui(self.tab_hist)

    def setup_seg_ui(self, parent):
        top = ttk.Frame(parent, padding=5)
        top.pack(side=tk.TOP, fill=tk.X)

        self.method_var = tk.StringVar(value="points")
        for text, value in [("Точки", "points"), ("Линии", "lines"), ("Границы", "edges")]:
            ttk.Radiobutton(top, text=text, variable=self.method_var, value=value, command=self.on_method_change).pack(side=tk.LEFT, padx=5)

        ttk.Label(top, text="Порог:").pack(side=tk.LEFT, padx=(20, 5))
        self.threshold_var = tk.IntVar(value=50)
        ttk.Scale(top, from_=0, to=255, variable=self.threshold_var, orient=tk.HORIZONTAL, length=200).pack(side=tk.LEFT, padx=5)
        ttk.Label(top, textvariable=self.threshold_var, width=4).pack(side=tk.LEFT)

        self.dir_label = ttk.Label(top, text="Направление:")
        self.dir_var = tk.StringVar(value="all")
        self.dir_combo = ttk.Combobox(top, textvariable=self.dir_var, values=["all", "horizontal", "vertical", "+45", "-45"], state="readonly", width=10)

        ttk.Button(top, text="Применить", command=self.apply_seg).pack(side=tk.LEFT, padx=10)
        ttk.Button(top, text="Сравнить все 3", command=self.compare_all_seg).pack(side=tk.LEFT, padx=5)

        main = ttk.Frame(parent)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(main, text="Исходное", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5)
        ttk.Label(main, text="Результат", font=("Arial", 12, "bold")).grid(row=0, column=1, pady=5)
        self.orig_canvas_seg = tk.Label(main, bg="gray", relief=tk.SUNKEN)
        self.orig_canvas_seg.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.res_canvas_seg = tk.Label(main, bg="gray", relief=tk.SUNKEN)
        self.res_canvas_seg.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

    def setup_hist_ui(self, parent):
        top = ttk.Frame(parent, padding=5)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(top, text="Построить гистограмму", command=self.show_hist).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Линейное контрастирование", command=self.apply_contrast).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Эквализация гистограммы", command=self.apply_equalize).pack(side=tk.LEFT, padx=5)

        main = ttk.Frame(parent)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(main, text="Исходное", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5)
        ttk.Label(main, text="Гистограмма / Результат", font=("Arial", 12, "bold")).grid(row=0, column=1, pady=5)
        self.orig_canvas_hist = tk.Label(main, bg="gray", relief=tk.SUNKEN)
        self.orig_canvas_hist.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.res_canvas_hist = tk.Label(main, bg="gray", relief=tk.SUNKEN)
        self.res_canvas_hist.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

    def on_method_change(self):
        if self.method_var.get() == "lines":
            self.dir_label.pack(side=tk.LEFT, padx=(15, 5))
            self.dir_combo.pack(side=tk.LEFT, padx=5)
        else:
            self.dir_label.pack_forget()
            self.dir_combo.pack_forget()

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp")])
        if not path: return
        buf = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if img is None:
            messagebox.showerror("Ошибка", "Не удалось загрузить изображение")
            return
        self.image = img
        self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.show(self.image, self.orig_canvas_seg)
        self.show(self.image, self.orig_canvas_hist)
        self.res_canvas_seg.config(image="")
        self.res_canvas_hist.config(image="")

    def show(self, img, canvas, max_size=500):
        if len(img.shape) == 2:
            img_disp = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            img_disp = img
        h, w = img_disp.shape[:2]
        scale = min(max_size / w, max_size / h, 1.0)
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        resized = cv2.resize(img_disp, (nw, nh), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        tkimg = ImageTk.PhotoImage(pil)
        canvas.config(image=tkimg)
        canvas.image = tkimg

    def point_detection(self, img, t):
        k = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32)
        r = cv2.filter2D(img.astype(np.float32), -1, k)
        out = np.zeros_like(img)
        out[np.abs(r) > t] = 255
        return out

    def line_detection(self, img, t, direction):
        ks = {
            "horizontal": np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]], dtype=np.float32),
            "vertical":   np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]], dtype=np.float32),
            "+45":        np.array([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]], dtype=np.float32),
            "-45":        np.array([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]], dtype=np.float32),
        }
        rs = {n: cv2.filter2D(img.astype(np.float32), -1, k) for n, k in ks.items()}
        out = np.zeros_like(img)
        if direction == "all":
            for n in rs: out[rs[n] > t] = 255
        else:
            out[rs[direction] > t] = 255
        return out

    def edge_detection(self, img, t):
        gx = cv2.Sobel(img.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(img.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
        mag = np.abs(gx) + np.abs(gy)
        out = np.zeros_like(img)
        out[mag > t] = 255
        return out

    def apply_seg(self):
        if self.gray is None: return
        t = self.threshold_var.get()
        m = self.method_var.get()
        if m == "points": res = self.point_detection(self.gray, t)
        elif m == "lines": res = self.line_detection(self.gray, t, self.dir_var.get())
        else: res = self.edge_detection(self.gray, t)
        self.show(res, self.res_canvas_seg)

    def compare_all_seg(self):
        if self.gray is None: return
        t = self.threshold_var.get()
        win = tk.Toplevel(self.root)
        win.title("Сравнение методов сегментации")
        ww, wh = min(1500, win.winfo_screenwidth() - 100), min(700, win.winfo_screenheight() - 120)
        win.geometry(f"{ww}x{wh}+50+50")
        results = [("Точки", self.point_detection(self.gray, t)),
                   ("Линии", self.line_detection(self.gray, t, "all")),
                   ("Границы", self.edge_detection(self.gray, t))]
        max_size = max(200, (ww - 100) // 3)
        for i, (title, img) in enumerate(results):
            frame = ttk.Frame(win); frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            win.grid_columnconfigure(i, weight=1)
            ttk.Label(frame, text=title, font=("Arial", 11, "bold")).pack()
            canvas = tk.Label(frame, bg="gray", relief=tk.SUNKEN); canvas.pack()
            self.show(img, canvas, max_size=max_size)

    def draw_histogram(self, img):
        hist = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_img = np.zeros((400, 512, 3), dtype=np.uint8)
        cv2.normalize(hist, hist, 0, 380, cv2.NORM_MINMAX)
        for i in range(256):
            cv2.line(hist_img, (i*2, 400), (i*2, 400 - int(hist[i])), (255, 255, 255), 1)
        return hist_img

    def show_hist(self):
        if self.gray is None: return
        hist_img = self.draw_histogram(self.gray)
        self.show(hist_img, self.res_canvas_hist)

    def apply_contrast(self):
        if self.gray is None: return
        f_min, f_max = np.min(self.gray), np.max(self.gray)
        if f_max == f_min: return
        result = (self.gray.astype(np.float32) - f_min) * (255.0 / (f_max - f_min))
        result = np.clip(result, 0, 255).astype(np.uint8)
        self.show(result, self.res_canvas_hist)

    def apply_equalize(self):
        if self.gray is None: return
        result = cv2.equalizeHist(self.gray)
        self.show(result, self.res_canvas_hist)

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphicsApp(root)
    root.mainloop()