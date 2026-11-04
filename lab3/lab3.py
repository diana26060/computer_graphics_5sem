import tkinter as tk
from tkinter import ttk, messagebox
import time


class RasterApp:
    def __init__(self, root):
        self.root = root
        root.title("ЛР3. Базовые растровые алгоритмы")
        root.geometry("1300x750")

        left = ttk.Frame(root, padding=5)
        left.pack(side=tk.LEFT, fill=tk.Y)

        right = ttk.Frame(root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(left, text="Алгоритм:").grid(row=0, column=0, sticky="w")
        self.algo = tk.StringVar(value="Брезенхем (отрезок)")
        self.combo = ttk.Combobox(
            left,
            textvariable=self.algo,
            values=[
                "Пошаговый",
                "ЦДА",
                "Брезенхем (отрезок)",
                "Брезенхем (окружность)",
                "Сглаженная окружность (Ву)"
            ],
            state="readonly",
            width=25
        )
        self.combo.grid(row=0, column=1, columnspan=2, sticky="we", pady=2)

        ttk.Label(left, text="Отрезок:").grid(row=1, column=0, columnspan=3, sticky="w", pady=(8, 0))

        ttk.Label(left, text="x1").grid(row=2, column=0, sticky="e")
        self.x1 = tk.IntVar(value=1)
        ttk.Entry(left, textvariable=self.x1, width=6).grid(row=2, column=1, sticky="w")

        ttk.Label(left, text="y1").grid(row=3, column=0, sticky="e")
        self.y1 = tk.IntVar(value=1)
        ttk.Entry(left, textvariable=self.y1, width=6).grid(row=3, column=1, sticky="w")

        ttk.Label(left, text="x2").grid(row=4, column=0, sticky="e")
        self.x2 = tk.IntVar(value=8)
        ttk.Entry(left, textvariable=self.x2, width=6).grid(row=4, column=1, sticky="w")

        ttk.Label(left, text="y2").grid(row=5, column=0, sticky="e")
        self.y2 = tk.IntVar(value=4)
        ttk.Entry(left, textvariable=self.y2, width=6).grid(row=5, column=1, sticky="w")

        ttk.Label(left, text="Окружность:").grid(row=6, column=0, columnspan=3, sticky="w", pady=(8, 0))

        ttk.Label(left, text="cx").grid(row=7, column=0, sticky="e")
        self.cx = tk.IntVar(value=0)
        ttk.Entry(left, textvariable=self.cx, width=6).grid(row=7, column=1, sticky="w")

        ttk.Label(left, text="cy").grid(row=8, column=0, sticky="e")
        self.cy = tk.IntVar(value=0)
        ttk.Entry(left, textvariable=self.cy, width=6).grid(row=8, column=1, sticky="w")

        ttk.Label(left, text="R").grid(row=9, column=0, sticky="e")
        self.R = tk.IntVar(value=5)
        ttk.Entry(left, textvariable=self.R, width=6).grid(row=9, column=1, sticky="w")

        ttk.Label(left, text="Масштаб (px/ед.):").grid(row=10, column=0, columnspan=3, sticky="w", pady=(8, 0))
        self.scale = tk.IntVar(value=30)
        self.scale_slider = ttk.Scale(
            left,
            from_=10,
            to=60,
            variable=self.scale,
            command=lambda *args: self.redraw()
        )
        self.scale_slider.grid(row=11, column=0, columnspan=3, sticky="we")

        ttk.Button(left, text="Построить", command=self.build).grid(
            row=12, column=0, columnspan=3, sticky="we", pady=(10, 2)
        )
        ttk.Button(left, text="Очистить", command=self.clear).grid(
            row=13, column=0, columnspan=3, sticky="we", pady=2
        )

        self.info = tk.Text(left, height=14, width=38, wrap="word")
        self.info.grid(row=14, column=0, columnspan=3, sticky="we", pady=(10, 0))

        self.canvas = tk.Canvas(right, bg="white", width=1000, height=700)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.last_result = None
        self.ox = 500
        self.oy = 350

        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.draw_grid()

    def draw_grid(self):
        c = self.canvas
        c.delete("all")

        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10:
            w, h = 1000, 700

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

        label_step = 5 if s >= 20 else 10

        for x in range(x_min, x_max + 1, label_step):
            sx = ox + x * s
            c.create_text(sx, oy + 12, text=str(x), fill="black", font=("Arial", 8))

        for y in range(y_min, y_max + 1, label_step):
            sy = oy - y * s
            c.create_text(ox + 20, sy, text=str(y), fill="black", font=("Arial", 8))

        c.create_line(0, oy, w, oy, arrow=tk.LAST, fill="black", width=2)
        c.create_line(ox, h, ox, 0, arrow=tk.LAST, fill="black", width=2)

        c.create_text(w - 20, oy - 10, text="X", font=("Arial", 12, "bold"))
        c.create_text(ox + 15, 15, text="Y", font=("Arial", 12, "bold"))
        c.create_text(ox + 5, oy + 5, text="0", anchor="nw", font=("Arial", 8))

    def cell_rect(self, x, y):
        s = self.scale.get()
        left = self.ox + x * s
        top = self.oy - (y + 1) * s
        return left, top, left + s, top + s

    def draw_points(self, points, color="blue", outline="black"):
        for (x, y) in points:
            l, t, r, b = self.cell_rect(x, y)
            self.canvas.create_rectangle(l, t, r, b, fill=color, outline=outline)

    def draw_antialiased_points(self, points):
        base_color = (0, 0, 255)
        bg_color = (255, 255, 255)
        
        for (x, y, alpha) in points:
            r = int(base_color[0] * alpha + bg_color[0] * (1 - alpha))
            g = int(base_color[1] * alpha + bg_color[1] * (1 - alpha))
            b = int(base_color[2] * alpha + bg_color[2] * (1 - alpha))
            color_hex = f"#{r:02x}{g:02x}{b:02x}"
            
            l, t, r_rect, b_rect = self.cell_rect(x, y)
            self.canvas.create_rectangle(l, t, r_rect, b_rect, fill=color_hex, outline="")

    def redraw(self):
        self.draw_grid()
        if self.last_result:
            pts, color = self.last_result
            self.draw_points(pts, color)

    def clear(self):
        self.last_result = None
        self.info.delete("1.0", tk.END)
        self.draw_grid()

    def build(self):
        algo = self.algo.get()
        self.info.delete("1.0", tk.END)

        try:
            if algo in ["Пошаговый", "ЦДА", "Брезенхем (отрезок)"]:
                x1, y1 = self.x1.get(), self.y1.get()
                x2, y2 = self.x2.get(), self.y2.get()

                if algo == "Пошаговый":
                    pts = self.step_line(x1, y1, x2, y2)
                    func = lambda: self.step_line(x1, y1, x2, y2)
                elif algo == "ЦДА":
                    pts = self.dda_line(x1, y1, x2, y2)
                    func = lambda: self.dda_line(x1, y1, x2, y2)
                else:
                    pts = self.bresenham_line(x1, y1, x2, y2)
                    func = lambda: self.bresenham_line(x1, y1, x2, y2)

                N = 1000
                t0 = time.perf_counter()
                for _ in range(N):
                    func()
                t1 = time.perf_counter()
                avg_us = (t1 - t0) / N * 1e6

                self.last_result = (pts, "blue")
                self.redraw()

                self.info.insert(tk.END, f"Алгоритм: {algo}\n")
                self.info.insert(tk.END, f"Отрезок: ({x1},{y1}) - ({x2},{y2})\n")
                self.info.insert(tk.END, f"Пикселей (уникальных): {len(set(pts))}\n")
                self.info.insert(tk.END, f"Время (среднее за {N} запусков): {avg_us:.3f} мкс\n\n")
                self.info.insert(tk.END, "Координаты пикселей:\n")
                self.info.insert(tk.END, ", ".join(f"({x},{y})" for x, y in pts))

            else:
                cx, cy = self.cx.get(), self.cy.get()
                R = self.R.get()

                if R < 0:
                    messagebox.showerror("Ошибка", "Радиус не может быть отрицательным")
                    return

                if algo == "Брезенхем (окружность)":
                    pts = self.bresenham_circle(cx, cy, R)
                    
                    N = 1000
                    t0 = time.perf_counter()
                    for _ in range(N):
                        self.bresenham_circle(cx, cy, R)
                    t1 = time.perf_counter()
                    avg_us = (t1 - t0) / N * 1e6

                    self.last_result = (pts, "green")
                    self.redraw()

                    self.info.insert(tk.END, "Алгоритм: Брезенхем (окружность)\n")
                    self.info.insert(tk.END, f"Центр: ({cx},{cy}), R={R}\n")
                    self.info.insert(tk.END, f"Пикселей (уникальных): {len(set(pts))}\n")
                    self.info.insert(tk.END, f"Время (среднее за {N} запусков): {avg_us:.3f} мкс\n\n")
                    self.info.insert(tk.END, "Координаты пикселей:\n")
                    self.info.insert(tk.END, ", ".join(f"({x},{y})" for x, y in sorted(set(pts))))

                else:
                    pts_with_alpha = self.wu_circle(cx, cy, R)
                    
                    N = 1000
                    t0 = time.perf_counter()
                    for _ in range(N):
                        self.wu_circle(cx, cy, R)
                    t1 = time.perf_counter()
                    avg_us = (t1 - t0) / N * 1e6

                    self.last_result = None
                    self.draw_grid()
                    self.draw_antialiased_points(pts_with_alpha)

                    self.info.insert(tk.END, "Алгоритм: Сглаженная окружность (Ву)\n")
                    self.info.insert(tk.END, f"Центр: ({cx},{cy}), R={R}\n")
                    self.info.insert(tk.END, f"Время (среднее за {N} запусков): {avg_us:.3f} мкс\n\n")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def step_line(self, x1, y1, x2, y2):
        points = []
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return [(x1, y1)]

        if abs(dx) >= abs(dy):
            step = 1 if dx > 0 else -1
            for x in range(x1, x2 + step, step):
                y = y1 + dy * (x - x1) / dx
                points.append((x, int(round(y))))
        else:
            step = 1 if dy > 0 else -1
            for y in range(y1, y2 + step, step):
                x = x1 + dx * (y - y1) / dy
                points.append((int(round(x)), y))

        return points

    def dda_line(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            return [(x1, y1)]

        x_inc = dx / steps
        y_inc = dy / steps

        x = float(x1)
        y = float(y1)
        points = []

        for _ in range(steps + 1):
            points.append((int(x), int(y)))
            x += x_inc
            y += y_inc

        return points

    def bresenham_line(self, x1, y1, x2, y2):
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        err = dx - dy
        x, y = x1, y1

        while True:
            points.append((x, y))
            if x == x2 and y == y2:
                break

            e2 = 2 * err

            if e2 > -dy:
                err -= dy
                x += sx

            if e2 < dx:
                err += dx
                y += sy

        return points

    def bresenham_circle(self, cx, cy, R):
        if R < 0:
            return []

        points = []

        def add8(x, y):
            points.append((cx + x, cy + y))
            points.append((cx + x, cy - y))
            points.append((cx - x, cy + y))
            points.append((cx - x, cy - y))
            points.append((cx + y, cy + x))
            points.append((cx + y, cy - x))
            points.append((cx - y, cy + x))
            points.append((cx - y, cy - x))

        x = 0
        y = R
        d = 3 - 2 * R

        while x <= y:
            add8(x, y)

            if d < 0:
                d = d + 4 * x + 6
            else:
                d = d + 4 * (x - y) + 10
                y -= 1

            x += 1

        return points

    def wu_circle(self, cx, cy, R):
        points = []

        def add8(x, y, intensity):
            if intensity > 0.001:
                points.append((cx + x, cy + y, intensity))
                points.append((cx + x, cy - y, intensity))
                points.append((cx - x, cy + y, intensity))
                points.append((cx - x, cy - y, intensity))
                points.append((cx + y, cy + x, intensity))
                points.append((cx + y, cy - x, intensity))
                points.append((cx - y, cy + x, intensity))
                points.append((cx - y, cy - x, intensity))

        x = 0
        y = float(R)
        
        while x <= y:
            exact_y = (R**2 - x**2)**0.5
            frac = exact_y - int(exact_y)
            add8(x, int(exact_y), 1.0 - frac)
            add8(x, int(exact_y) + 1, frac)
            x += 1
            
        return points


if __name__ == "__main__":
    root = tk.Tk()
    app = RasterApp(root)
    root.mainloop()