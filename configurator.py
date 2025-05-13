import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import yaml

CONFIG_PATH = "config/app_conf.yaml"

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def save_config(data):
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(data, f)

def configure():
    config = load_config()
    window = tk.Toplevel()
    window.title("Konfigurator")
    window.geometry("320x560")
    window.configure(padx=20, pady=20)

    style = ttk.Style()
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10))
    style.configure("TCheckbutton", font=("Segoe UI", 10))
    style.configure("TNotebook", tabmargins=[2, 5, 2, 0])

    ttk.Label(window, text="Urządzenie obliczeniowe (wymaga resetu oprogramowania)").pack(anchor="center", pady=(0, 5))
    device_var = tk.StringVar(value=config['core'].get('device', 'cpu'))
    ttk.Combobox(window, textvariable=device_var, values=["cpu", "cuda"], state="readonly", width=10).pack(anchor="center", pady=(0, 10))

    notebook = ttk.Notebook(window)
    notebook.pack(fill="both", expand=True)

    def create_section(title, section_data):
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text=title.capitalize())

        draw_var = tk.BooleanVar(value=section_data.get('draw_boxes', False))
        ttk.Checkbutton(frame, text="Rysuj ramki", variable=draw_var).pack(anchor="center", pady=(0, 8))

        ttk.Label(frame, text="Kolor ramki:").pack(anchor="center")
        def choose_box_color():
            current_color = "#%02x%02x%02x" % tuple(section_data['box_color'])
            color = colorchooser.askcolor(color=current_color)[0]
            if color:
                section_data['box_color'] = [int(c) for c in color]
        ttk.Button(frame, text="Wybierz kolor ramki", command=choose_box_color).pack(anchor="center", pady=(0, 8))

        ttk.Label(frame, text="Grubość ramki:").pack(anchor="center")
        thickness_spin = ttk.Spinbox(frame, from_=1, to=10, width=5)
        thickness_spin.set(section_data.get('box_thickness', 1))
        thickness_spin.pack(anchor="center", pady=(0, 10))

        show_best_var = tk.BooleanVar(value=section_data.get('show_best', False))
        ttk.Checkbutton(frame, text="Pokaż najlepszy wynik", variable=show_best_var).pack(anchor="center", pady=(0, 8))

        show_score_var = tk.BooleanVar(value=section_data.get('show_score', False))
        ttk.Checkbutton(frame, text="Pokaż wynik dopasowania", variable=show_score_var).pack(anchor="center", pady=(0, 8))

        ttk.Label(frame, text="Skala czcionki:").pack(anchor="center")
        font_scale_spin = ttk.Spinbox(frame, from_=0.1, to=2.0, increment=0.1, width=5)
        font_scale_spin.set(section_data.get('font_scale', 1.0))
        font_scale_spin.pack(anchor="center", pady=(0, 8))

        ttk.Label(frame, text="Kolor czcionki:").pack(anchor="center")
        def choose_font_color():
            current_color = "#%02x%02x%02x" % tuple(section_data['font_color'])
            color = colorchooser.askcolor(color=current_color)[0]
            if color:
                section_data['font_color'] = [int(c) for c in color]
        ttk.Button(frame, text="Wybierz kolor czcionki", command=choose_font_color).pack(anchor="center", pady=(0, 8))

        return {
            'draw_var': draw_var,
            'thickness_spin': thickness_spin,
            'show_best_var': show_best_var,
            'show_score_var': show_score_var,
            'font_scale_spin': font_scale_spin
        }

    detection_widgets = create_section('detekcja', config['detection'])
    recognition_widgets = create_section('rozpoznanie', config['recognition'])

    def save_and_close():
        try:
            config['core']['device'] = device_var.get()

            for key, widgets in [('detection', detection_widgets), ('recognition', recognition_widgets)]:
                section = config[key]
                section['draw_boxes'] = widgets['draw_var'].get()
                section['box_thickness'] = int(widgets['thickness_spin'].get())
                section['show_best'] = widgets['show_best_var'].get()
                section['show_score'] = widgets['show_score_var'].get()
                section['font_scale'] = float(widgets['font_scale_spin'].get())

            save_config(config)
            messagebox.showinfo("Sukces", "Konfiguracja została zapisana.")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd zapisu konfiguracji: {e}")

    ttk.Button(window, text="Zapisz konfigurację", command=save_and_close).pack(pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    configure()
    root.mainloop()
