import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import yaml
import os

CONFIG_PATH = "config/app_conf.yaml"

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def save_config(data):
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(data, f)

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def rgb_to_bgr(rgb):
    return [int(rgb[2]), int(rgb[1]), int(rgb[0])]

def configure():
    config = load_config()
    window = tk.Toplevel()
    window.title("Konfigurator")
    window.geometry("400x500")
    window.resizable(False, False)

    notebook = ttk.Notebook(window)
    notebook.pack(pady=10, expand=True)

    def create_section_frame(title, section_data):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title.capitalize())

        draw_var = tk.BooleanVar(value=section_data['draw_boxes'])
        ttk.Checkbutton(frame, text="Rysuj ramki", variable=draw_var).pack(pady=5)

        color_label = ttk.Label(frame, text="Kolor ramki:")
        color_label.pack(pady=5)

        def choose_color():
            initial_color = rgb_to_hex(section_data['box_color'])
            color = colorchooser.askcolor(color=initial_color)[0]
            if color:
                rgb = [int(c) for c in color]
                section_data['box_color'] = rgb
                color_label.config(text="Kolor ramki:")

        ttk.Button(frame, text="Wybierz kolor", command=choose_color, width=15).pack(pady=5)

        ttk.Label(frame, text="Grubość ramki:").pack(pady=5)
        thickness_spin = ttk.Spinbox(frame, from_=1, to=10, width=5)
        thickness_spin.set(section_data['box_thickness'])
        thickness_spin.pack(pady=5)

        extra_widgets = {}

        if title == 'recognition':
            show_score_var = tk.BooleanVar(value=section_data['show_score'])
            ttk.Checkbutton(frame, text="Pokaż wynik dopasowania", variable=show_score_var).pack(pady=5)
            extra_widgets['show_score_var'] = show_score_var

            ttk.Label(frame, text="Skala czcionki:").pack(pady=5)
            font_scale_spin = ttk.Spinbox(frame, from_=0.1, to=2.0, increment=0.1, width=5)
            font_scale_spin.set(section_data['font_scale'])
            font_scale_spin.pack(pady=5)

            font_color_label = ttk.Label(frame, text="Kolor czcionki:")
            font_color_label.pack(pady=5)

            def choose_font_color():
                initial_color = rgb_to_hex(section_data['font_color'])
                color = colorchooser.askcolor(color=initial_color)[0]
                if color:
                    rgb = [int(c) for c in color]
                    section_data['font_color'] = rgb
                    font_color_label.config(text="Kolor czcionki:")

            ttk.Button(frame, text="Wybierz kolor czcionki", command=choose_font_color, width=20).pack(pady=5)

            extra_widgets.update({
                'font_scale_spin': font_scale_spin
            })

        return {
            'draw_var': draw_var,
            'thickness_spin': thickness_spin,
            **extra_widgets
        }

    detection_widgets = create_section_frame('detection', config['detection'])
    recognition_widgets = create_section_frame('recognition', config['recognition'])

    def save_and_close():
        try:
            config['detection']['draw_boxes'] = detection_widgets['draw_var'].get()
            config['detection']['box_color'] = rgb_to_bgr(config['detection']['box_color'])
            config['detection']['box_thickness'] = int(detection_widgets['thickness_spin'].get())

            config['recognition']['draw_boxes'] = recognition_widgets['draw_var'].get()
            config['recognition']['box_color'] = rgb_to_bgr(config['recognition']['box_color'])
            config['recognition']['box_thickness'] = int(recognition_widgets['thickness_spin'].get())
            config['recognition']['show_score'] = recognition_widgets['show_score_var'].get()
            config['recognition']['font_scale'] = float(recognition_widgets['font_scale_spin'].get())
            config['recognition']['font_color'] = rgb_to_bgr(config['recognition']['font_color'])

            save_config(config)
            messagebox.showinfo("Sukces", "Konfiguracja została zapisana.")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd zapisu konfiguracji: {e}")

    ttk.Button(window, text="Zapisz konfigurację", command=save_and_close, width=20).pack(pady=10)

if __name__ == "__main__":
    configure()
