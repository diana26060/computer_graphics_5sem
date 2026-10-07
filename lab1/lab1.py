import tkinter as tk
from tkinter import colorchooser, messagebox


class ColorConverterApp:

    def __init__(self, root):
        self.root = root
        self.root.title(
            "Цветовые модели CMYK - RGB - HSV"
        )
        self.root.geometry("1100x480")
        self.root.resizable(False, False)

        self.rgb_values = [0, 0, 255]

        self.is_updating = False

        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.sliders = {}
        self.texts = {}

        self.create_cmyk_panel(main_frame, 0)
        self.create_rgb_panel(main_frame, 1)
        self.create_hsv_panel(main_frame, 2)
        self.create_control_panel(main_frame, 3)

        self.update_all_ui()

    def create_cmyk_panel(self, parent, column):
        frame = tk.LabelFrame(
            parent, text=" Модель CMYK ", font=("Arial", 11, "bold"), padx=10, pady=10
        )
        frame.grid(row=0, column=column, padx=10, sticky="nsew")

        keys = [
            ("Cyan", 100),
            ("Magenta", 100),
            ("Yellow", 100),
            ("Key/Black", 100),
        ]
        self.sliders["cmyk"] = []
        self.texts["cmyk"] = []

        for name, max_val in keys:
            tk.Label(frame, text=f"{name} (0-{max_val}%):").pack(anchor="w")
            slider = tk.Scale(
                frame,
                from_=0,
                to=max_val,
                orient=tk.HORIZONTAL,
                command=self.on_cmyk_slider_changed,
            )
            slider.pack(fill=tk.X)
            self.sliders["cmyk"].append(slider)

            text = tk.Entry(frame, width=15)
            text.pack(pady=5)
            text.bind("<Return>", self.on_cmyk_text_changed)
            self.texts["cmyk"].append(text)

    def create_rgb_panel(self, parent, column):
        frame = tk.LabelFrame(
            parent, text=" Модель RGB ", font=("Arial", 11, "bold"), padx=10, pady=10
        )
        frame.grid(row=0, column=column, padx=10, sticky="nsew")

        keys = [("Red", 255), ("Green", 255), ("Blue", 255)]
        self.sliders["rgb"] = []
        self.texts["rgb"] = []

        for name, max_val in keys:
            tk.Label(frame, text=f"{name} (0-{max_val}):").pack(anchor="w")
            slider = tk.Scale(
                frame,
                from_=0,
                to=max_val,
                orient=tk.HORIZONTAL,
                command=self.on_rgb_slider_changed,
            )
            slider.pack(fill=tk.X)
            self.sliders["rgb"].append(slider)

            text = tk.Entry(frame, width=15)
            text.pack(pady=5)
            text.bind("<Return>", self.on_rgb_text_changed)
            self.texts["rgb"].append(text)

    def create_hsv_panel(self, parent, column):
        frame = tk.LabelFrame(
            parent, text=" Модель HSV ", font=("Arial", 11, "bold"), padx=10, pady=10
        )
        frame.grid(row=0, column=column, padx=10, sticky="nsew")

        keys = [("Hue", 360), ("Saturation", 100), ("Value", 100)]
        self.sliders["hsv"] = []
        self.texts["hsv"] = []

        for name, max_val in keys:
            unit = "°" if max_val == 360 else "%"
            tk.Label(frame, text=f"{name} (0-{max_val}{unit}):").pack(anchor="w")
            slider = tk.Scale(
                frame,
                from_=0,
                to=max_val,
                orient=tk.HORIZONTAL,
                command=self.on_hsv_slider_changed,
            )
            slider.pack(fill=tk.X)
            self.sliders["hsv"].append(slider)

            text = tk.Entry(frame, width=15)
            text.pack(pady=5)
            text.bind("<Return>", self.on_hsv_text_changed)
            self.texts["hsv"].append(text)

    def create_control_panel(self, parent, column):
        frame = tk.LabelFrame(
            parent,
            text=" Управление ",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10,
        )
        frame.grid(row=0, column=column, padx=10, sticky="nsew")

        tk.Button(
            frame,
            text="Выбрать из палитры",
            command=self.pick_color_dialog,
            bg="#e0e0e0",
            font=("Arial", 10),
        ).pack(pady=20, fill=tk.X)

        tk.Label(frame, text="Предпросмотр:").pack(anchor="w", pady=(10, 5))
        self.color_preview = tk.Canvas(
            frame, width=130, height=130, bg="blue", highlightthickness=1
        )
        self.color_preview.pack()



    def rgb_to_cmyk(self, r, g, b):
        r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
        k = 1.0 - max(r_norm, g_norm, b_norm)
        if k == 1.0:
            return 0.0, 0.0, 0.0, 1.0
        c = (1.0 - r_norm - k) / (1.0 - k)
        m = (1.0 - g_norm - k) / (1.0 - k)
        y = (1.0 - b_norm - k) / (1.0 - k)
        return c, m, y, k

    def cmyk_to_rgb(self, c, m, y, k):
        r = 255 * (1.0 - c) * (1.0 - k)
        g = 255 * (1.0 - m) * (1.0 - k)
        b = 255 * (1.0 - y) * (1.0 - k)
        return int(round(r)), int(round(g)), int(round(b))

    def rgb_to_hsv(self, r, g, b):
        r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
        maxc = max(r_norm, g_norm, b_norm)
        minc = min(r_norm, g_norm, b_norm)
        v = maxc
        delta = maxc - minc

        if maxc == 0.0:
            s = 0.0
        else:
            s = delta / maxc

        if delta == 0.0:
            h = 0.0
        elif maxc == r_norm:
            h = 60.0 * (((g_norm - b_norm) / delta) % 6)
        elif maxc == g_norm:
            h = 60.0 * (((b_norm - r_norm) / delta) + 2.0)
        else:
            h = 60.0 * (((r_norm - g_norm) / delta) + 4.0)

        return h, s, v

    def hsv_to_rgb(self, h, s, v):
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        if 0 <= h < 60:
            r_prime, g_prime, b_prime = c, x, 0.0
        elif 60 <= h < 120:
            r_prime, g_prime, b_prime = x, c, 0.0
        elif 120 <= h < 180:
            r_prime, g_prime, b_prime = 0.0, c, x
        elif 180 <= h < 240:
            r_prime, g_prime, b_prime = 0.0, x, c
        elif 240 <= h < 300:
            r_prime, g_prime, b_prime = x, 0.0, c
        else:
            r_prime, g_prime, b_prime = c, 0.0, x

        r = int(round((r_prime + m) * 255))
        g = int(round((g_prime + m) * 255))
        b = int(round((b_prime + m) * 255))
        return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))



    def on_rgb_slider_changed(self, event=None):
        if self.is_updating:
            return
        self.rgb_values[0] = self.sliders["rgb"][0].get()
        self.rgb_values[1] = self.sliders["rgb"][1].get()
        self.rgb_values[2] = self.sliders["rgb"][2].get()
        self.update_all_ui()

    def on_rgb_text_changed(self, event=None):
        try:
            r = int(self.texts["rgb"][0].get())
            g = int(self.texts["rgb"][1].get())
            b = int(self.texts["rgb"][2].get())
            self.rgb_values[0] = max(0, min(255, r))
            self.rgb_values[1] = max(0, min(255, g))
            self.rgb_values[2] = max(0, min(255, b))
            self.update_all_ui()
        except ValueError:
            pass

    def on_cmyk_slider_changed(self, event=None):
        if self.is_updating:
            return
        c = self.sliders["cmyk"][0].get() / 100.0
        m = self.sliders["cmyk"][1].get() / 100.0
        y = self.sliders["cmyk"][2].get() / 100.0
        k = self.sliders["cmyk"][3].get() / 100.0
        r, g, b = self.cmyk_to_rgb(c, m, y, k)
        self.rgb_values = [r, g, b]
        self.update_all_ui()

    def on_cmyk_text_changed(self, event=None):
        try:
            c = float(self.texts["cmyk"][0].get()) / 100.0
            m = float(self.texts["cmyk"][1].get()) / 100.0
            y = float(self.texts["cmyk"][2].get()) / 100.0
            k = float(self.texts["cmyk"][3].get()) / 100.0
            r, g, b = self.cmyk_to_rgb(
                max(0.0, min(1.0, c)),
                max(0.0, min(1.0, m)),
                max(0.0, min(1.0, y)),
                max(0.0, min(1.0, k)),
            )
            self.rgb_values = [r, g, b]
            self.update_all_ui()
        except ValueError:
            pass

    def on_hsv_slider_changed(self, event=None):
        if self.is_updating:
            return
        h = self.sliders["hsv"][0].get()
        s = self.sliders["hsv"][1].get() / 100.0
        v = self.sliders["hsv"][2].get() / 100.0
        r, g, b = self.hsv_to_rgb(h, s, v)
        self.rgb_values = [r, g, b]
        self.update_all_ui()

    def on_hsv_text_changed(self, event=None):
        try:
            h = float(self.texts["hsv"][0].get())
            s = float(self.texts["hsv"][1].get()) / 100.0
            v = float(self.texts["hsv"][2].get()) / 100.0
            r, g, b = self.hsv_to_rgb(
                max(0.0, min(360.0, h)),
                max(0.0, min(1.0, s)),
                max(0.0, min(1.0, v)),
            )
            self.rgb_values = [r, g, b]
            self.update_all_ui()
        except ValueError:
            pass

    def pick_color_dialog(self):
        color_code = colorchooser.askcolor(title="Выберите цвет")
        if color_code[0]:
            rgb = color_code[0]
            self.rgb_values = [int(rgb[0]), int(rgb[1]), int(rgb[2])]
            self.update_all_ui()



    def update_all_ui(self):
        self.is_updating = True

        r, g, b = self.rgb_values

        rgb_vals = [r, g, b]
        for i in range(3):
            self.sliders["rgb"][i].set(rgb_vals[i])
            self.texts["rgb"][i].delete(0, tk.END)
            self.texts["rgb"][i].insert(0, str(rgb_vals[i]))

        c, m, y, k = self.rgb_to_cmyk(r, g, b)
        cmyk_vals = [c * 100, m * 100, y * 100, k * 100]
        for i in range(4):
            self.sliders["cmyk"][i].set(cmyk_vals[i])
            self.texts["cmyk"][i].delete(0, tk.END)
            self.texts["cmyk"][i].insert(0, f"{cmyk_vals[i]:.1f}")

        h, s, v = self.rgb_to_hsv(r, g, b)
        hsv_vals = [h, s * 100, v * 100]
        for i in range(3):
            self.sliders["hsv"][i].set(hsv_vals[i])
            self.texts["hsv"][i].delete(0, tk.END)
            self.texts["hsv"][i].insert(0, f"{hsv_vals[i]:.1f}")

        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.color_preview.config(bg=hex_color)

        self.is_updating = False


if __name__ == "__main__":
    root = tk.Tk()
    app = ColorConverterApp(root)
    root.mainloop()


