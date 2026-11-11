import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time


def ensure_ccw(poly):
    n = len(poly)
    area = 0
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    if area < 0:
        return list(reversed(poly))
    return list(poly)


class ClipApp:
    def __init__(self, root):
        self.root = root
        root.title("ЛР4. Отсечение отрезков и многоугольников")
        root.geometry("1400x800")

        self.segments = []
        self.clipped_segments = []

        left = ttk.Frame(root, padding=5)
        left.pack(side=tk.LEFT, fill=tk.Y)
        right = ttk.Frame(root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(left, text="Алгоритм:").grid(row=0, column=0, sticky="w")
        self.algo = tk.StringVar(value="Сазерленд-Коэн")
        ttk.Combobox(
            left, textvariable=self.algo,
            values=["Сазерленд-Коэн", "Кирус-Бек"],
            state="readonly", width=32
        ).grid(row=0, column=1, columnspan=2, sticky="we", pady=2)

        ttk.Button(left, text="Загрузить файл", command=self.load_file).grid(
            row=1, column=0, columnspan=3, sticky="we", pady=2
        )

        ttk.Label(left, text="Прямоугольное окно:").grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )
        rf = ttk.Frame(left)
        rf.grid(row=3, column=0, columnspan=3, sticky="we")

        self.xmin = tk.DoubleVar(value=0)
        self.ymin = tk.DoubleVar(value=0)
        self.xmax = tk.DoubleVar(value=10)
        self.ymax = tk.DoubleVar(value=10)

        for i, (lbl, var) in enumerate([
            ("xmin", self.xmin), ("ymin", self.ymin),
            ("xmax", self.xmax), ("ymax", self.ymax)
        ]):
            ttk.Label(rf, text=lbl).grid(row=i // 2, column=(i % 2) * 2, sticky="e")
            ttk.Entry(rf, textvariable=var, width=6).grid(
                row=i // 2, column=(i % 2) * 2 + 1, sticky="w"
            )

        ttk.Label(left, text="Выпуклый многоугольник:").grid(
            row=4, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )
        self.poly_text = tk.Text(left, height=8, width=30, wrap="word")
        self.poly_text.grid(row=5, column=0, columnspan=3, sticky="we")
        self.poly_text.insert(
            "1.0",
            "2 2\n8 2\n9 6\n5 9\n1 6"
        )

        ttk.Label(left, text="Масштаб (px/ед.):").grid(
            row=6, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )
        self.scale = tk.IntVar(value=30)
        ttk.Scale(
            left, from_=5, to=60, variable=self.scale,
            orient="horizontal", command=lambda *a: self.redraw()
        ).grid(row=7, column=0, columnspan=3, sticky="we")

        ttk.Button(left, text="Отсечь", command=self.perform_clip).grid(
            row=8, column=0, columnspan=3, sticky="we", pady=(10, 2)
        )
        ttk.Button(left, text="Очистить", command=self.clear).grid(
            row=9, column=0, columnspan=3, sticky="we", pady=2
        )
        ttk.Button(left, text="Пример", command=self.load_sample).grid(
            row=10, column=0, columnspan=3, sticky="we", pady=2
        )

        self.info = tk.Text(left, height=14, width=38, wrap="word")
        self.info.grid(row=11, column=0, columnspan=3, sticky="we", pady=(10, 0))

        self.canvas = tk.Canvas(right, bg="white", width=1000, height=750)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        self.ox = 500
        self.oy = 375

        self.draw_grid()

    # файл и пример

    def load_file(self):
        path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r") as f:
                lines = [l.strip() for l in f if l.strip()]
            n = int(lines[0])
            segments = []
            for i in range(1, n + 1):
                x1, y1, x2, y2 = map(float, lines[i].split())
                segments.append((x1, y1, x2, y2))
            xmin, ymin, xmax, ymax = map(float, lines[n + 1].split())
            self.segments = segments
            self.xmin.set(xmin)
            self.ymin.set(ymin)
            self.xmax.set(xmax)
            self.ymax.set(ymax)
            self.clipped_segments = []
            self.redraw()
            self.info.delete("1.0", tk.END)
            self.info.insert(tk.END, f"Загружено {n} отрезков\n")
            self.info.insert(tk.END, f"Окно: ({xmin}, {ymin}) - ({xmax}, {ymax})\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def load_sample(self):
        self.segments = [
            (-5, -2, 15, 8),
            (0, 0, 12, 5),
            (-8, 5, 5, -3),
            (2, 2, 8, 8),
            (-2, -5, 15, 12),
            (12, 0, 12, 10),
        ]
        self.xmin.set(0)
        self.ymin.set(0)
        self.xmax.set(10)
        self.ymax.set(10)
        self.clipped_segments = []
        self.redraw()
        self.info.delete("1.0", tk.END)
        self.info.insert(tk.END, "Загружен пример: 6 отрезков\n")
        self.info.insert(tk.END, "Окно: (0, 0) - (10, 10)\n")

    # отсечение

    def perform_clip(self):
        if not self.segments:
            messagebox.showinfo("Информация", "Сначала загрузите файл или нажмите «Пример»")
            return

        algo = self.algo.get()

        try:
            xmin = self.xmin.get()
            ymin = self.ymin.get()
            xmax = self.xmax.get()
            ymax = self.ymax.get()
        except Exception:
            messagebox.showerror("Ошибка", "Неверные координаты окна")
            return

        if xmin >= xmax or ymin >= ymax:
            messagebox.showerror("Ошибка", "xmin < xmax, ymin < ymax")
            return

        rect = (xmin, ymin, xmax, ymax)

        if algo == "Сазерленд-Коэн":
            N = 1000
            t0 = time.perf_counter()
            for _ in range(N):
                res = self.clip_sc_batch(self.segments, rect)
            t1 = time.perf_counter()
            avg = (t1 - t0) / N * 1e6
            self.clipped_segments = res
        else:
            poly = self.parse_polygon()
            if not poly or len(poly) < 3:
                messagebox.showerror("Ошибка", "Многоугольник: минимум 3 вершины")
                return
            poly = ensure_ccw(poly)
            N = 1000
            t0 = time.perf_counter()
            for _ in range(N):
                res = self.clip_cb_batch(self.segments, poly)
            t1 = time.perf_counter()
            avg = (t1 - t0) / N * 1e6
            self.clipped_segments = res

        self.redraw()

        self.info.delete("1.0", tk.END)
        self.info.insert(tk.END, f"Алгоритм: {algo}\n")
        self.info.insert(tk.END, f"Исходных отрезков: {len(self.segments)}\n")
        visible = sum(1 for s in self.clipped_segments if s is not None)
        self.info.insert(tk.END, f"Видимых: {visible} из {len(self.segments)}\n")
        self.info.insert(tk.END, f"Время (среднее за {N}): {avg:.2f} мкс\n\n")
        self.info.insert(tk.END, "Результаты отсечения:\n")
        for i, (orig, clipped) in enumerate(zip(self.segments, self.clipped_segments)):
            if clipped:
                x1, y1, x2, y2 = clipped
                self.info.insert(
                    tk.END,
                    f"{i+1}: ({x1:.3f}, {y1:.3f}) - ({x2:.3f}, {y2:.3f})\n"
                )
            else:
                self.info.insert(tk.END, f"{i+1}: не видим\n")

    def clip_sc_batch(self, segments, rect):
        xmin, ymin, xmax, ymax = rect
        return [self.clip_sc(*s, xmin, ymin, xmax, ymax) for s in segments]

    def clip_cb_batch(self, segments, poly):
        return [self.clip_cyrus_beck(*s, poly) for s in segments]

    # алгоритмы

    def compute_outcode(self, x, y, xmin, ymin, xmax, ymax):
        code = 0
        if x < xmin:
            code |= 1
        elif x > xmax:
            code |= 2
        if y < ymin:
            code |= 4
        elif y > ymax:
            code |= 8
        return code

    def clip_sc(self, x1, y1, x2, y2, xmin, ymin, xmax, ymax):
        o1 = self.compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
        o2 = self.compute_outcode(x2, y2, xmin, ymin, xmax, ymax)

        while True:
            if not (o1 | o2):
                return (x1, y1, x2, y2)
            if o1 & o2:
                return None

            code = o1 if o1 else o2

            if code & 8:
                y = ymax
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1) if y2 != y1 else x1
            elif code & 4:
                y = ymin
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1) if y2 != y1 else x1
            elif code & 2:
                x = xmax
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1) if x2 != x1 else y1
            else:
                x = xmin
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1) if x2 != x1 else y1

            if code == o1:
                x1, y1 = x, y
                o1 = self.compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x, y
                o2 = self.compute_outcode(x2, y2, xmin, ymin, xmax, ymax)

    def clip_cyrus_beck(self, x1, y1, x2, y2, polygon):
        n = len(polygon)
        t_enter = 0.0
        t_exit = 1.0
        dx = x2 - x1
        dy = y2 - y1

        for i in range(n):
            xp, yp = polygon[i]
            xq, yq = polygon[(i + 1) % n]
            ex = xq - xp
            ey = yq - yp
            nx = -ey
            ny = ex

            num = (x1 - xp) * nx + (y1 - yp) * ny
            den = dx * nx + dy * ny

            if abs(den) < 1e-12:
                if num < 0:
                    return None
            else:
                t = -num / den
                if den > 0:
                    if t > t_enter:
                        t_enter = t
                else:
                    if t < t_exit:
                        t_exit = t

        if t_enter > t_exit:
            return None

        return (
            x1 + t_enter * dx, y1 + t_enter * dy,
            x1 + t_exit * dx, y1 + t_exit * dy
        )

    def parse_polygon(self, silent=False):
        try:
            text = self.poly_text.get("1.0", tk.END).strip()
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            poly = []
            for line in lines:
                parts = line.split()
                poly.append((float(parts[0]), float(parts[1])))
            return poly
        except Exception as e:
            if not silent:
                messagebox.showerror("Ошибка", f"Неверный многоугольник: {e}")
            return None

    # отрисовка

    def draw_grid(self):
        c = self.canvas
        c.delete("all")

        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10:
            w, h = 1000, 750

        s = self.scale.get()
        ox = w // 2
        oy = h // 2
        self.ox, self.oy = ox, oy

        x_min = -ox // s - 1
        x_max = (w - ox) // s + 1
        y_min = -(h - oy) // s - 1
        y_max = oy // s + 1

        for x in range(x_min, x_max + 1):
            sx = ox + x * s
            color = "black" if x == 0 else "#e0e0e0"
            c.create_line(sx, 0, sx, h, fill=color)
        for y in range(y_min, y_max + 1):
            sy = oy - y * s
            color = "black" if y == 0 else "#e0e0e0"
            c.create_line(0, sy, w, sy, fill=color)

        step = 5 if s >= 20 else 10
        for x in range(x_min, x_max + 1, step):
            c.create_text(ox + x * s, oy + 12, text=str(x), font=("Arial", 8))
        for y in range(y_min, y_max + 1, step):
            c.create_text(ox + 20, oy - y * s, text=str(y), font=("Arial", 8))

        c.create_line(0, oy, w, oy, arrow=tk.LAST, fill="black", width=2)
        c.create_line(ox, h, ox, 0, arrow=tk.LAST, fill="black", width=2)
        c.create_text(w - 20, oy - 10, text="X", font=("Arial", 12, "bold"))
        c.create_text(ox + 15, 15, text="Y", font=("Arial", 12, "bold"))
        c.create_text(ox + 5, oy + 5, text="0", anchor="nw", font=("Arial", 8))

    def to_canvas(self, x, y):
        s = self.scale.get()
        return self.ox + x * s, self.oy - y * s

    def redraw(self):
        self.draw_grid()
        c = self.canvas

        try:
            xmin = self.xmin.get()
            ymin = self.ymin.get()
            xmax = self.xmax.get()
            ymax = self.ymax.get()
            cx1, cy1 = self.to_canvas(xmin, ymax)
            cx2, cy2 = self.to_canvas(xmax, ymin)
            c.create_rectangle(cx1, cy1, cx2, cy2,
                               outline="darkred", width=2, dash=(5, 3))
        except Exception:
            pass

        if self.algo.get().startswith("Кирус"):
            poly = self.parse_polygon(silent=True)
            if poly and len(poly) >= 3:
                coords = []
                for (x, y) in poly:
                    cx, cy = self.to_canvas(x, y)
                    coords.extend([cx, cy])
                c.create_polygon(coords, outline="darkgreen",
                                 width=2, fill="", dash=(3, 3))
                for (x, y) in poly:
                    cx, cy = self.to_canvas(x, y)
                    c.create_oval(cx - 3, cy - 3, cx + 3, cy + 3,
                                  fill="darkgreen", outline="")

        for (x1, y1, x2, y2) in self.segments:
            cx1, cy1 = self.to_canvas(x1, y1)
            cx2, cy2 = self.to_canvas(x2, y2)
            c.create_line(cx1, cy1, cx2, cy2, fill="#87CEEB", width=2)

        for seg in self.clipped_segments:
            if seg is None:
                continue
            x1, y1, x2, y2 = seg
            cx1, cy1 = self.to_canvas(x1, y1)
            cx2, cy2 = self.to_canvas(x2, y2)
            c.create_line(cx1, cy1, cx2, cy2, fill="blue", width=3)

    def clear(self):
        self.segments = []
        self.clipped_segments = []
        self.info.delete("1.0", tk.END)
        self.redraw()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClipApp(root)
    root.mainloop()