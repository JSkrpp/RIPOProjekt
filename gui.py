import tkinter as tk
from tkinter import ttk

from recognition import recognize_camera, recognize_video
from detection import detect_camera, detect_video
from configurator import configure

def return_to_main(frame, root):
    for widget in frame.winfo_children():
        widget.destroy()

    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 12), padding=10)

    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(side=tk.TOP, padx=20, pady=20, expand=True)

    lbl_title = tk.Label(frame, text="RiPO", font=("Arial", 16, "bold"), bg="#f0f0f0")
    lbl_title.pack(pady=15)
    btn_train = ttk.Button(frame, text="Dodaj wzorzec", command=lambda: detect_page(root))
    btn_train.pack(pady=10, padx=20, fill=tk.X)

    btn_recognize = ttk.Button(frame, text="Rozpoznaj twarz", command=lambda: recognize_page(root))
    btn_recognize.pack(pady=10, padx=20, fill=tk.X)

    btn_config = ttk.Button(frame, text="Konfigurator", command=configure)
    btn_config.pack(pady=10, padx=20, fill=tk.X)


def detect_page(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    lbl_prompt = tk.Label(frame, text="Wybierz źródło detekcji obrazu", font=("Arial", 14), bg="#f0f0f0")
    lbl_prompt.pack(pady=20)

    lbl_pattern = tk.Label(frame, text="Wpisz nazwę wzorca", font=("Arial", 12), bg="#f0f0f0")
    lbl_pattern.pack(pady=10)

    entry_text = tk.StringVar()
    entry_field = ttk.Entry(frame, textvariable=entry_text)
    entry_field.pack(pady=10, padx=20, fill=tk.X)

    btn_camera = ttk.Button(frame, text="Kamera", command=lambda: detect_camera(entry_text.get()))
    btn_camera.pack(pady=10, padx=20, fill=tk.X)

    btn_video = ttk.Button(frame, text="Wideo", command=lambda: detect_video(entry_text.get()))
    btn_video.pack(pady=10, padx=20, fill=tk.X)

    btn_back = ttk.Button(frame, text="Powrót", command=lambda: return_to_main(frame, frame))
    btn_back.pack(pady=10, padx=20, fill=tk.X)



def recognize_page(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    lbl_prompt = tk.Label(frame, text="Wybierz źródło rozpoznania obrazu", font=("Arial", 14), bg="#f0f0f0")
    lbl_prompt.pack(pady=20)

    btn_camera = ttk.Button(frame, text="Kamera", command=lambda: recognize_camera())
    btn_camera.pack(pady=10, padx=20, fill=tk.X)

    btn_video = ttk.Button(frame, text="Wideo", command=lambda: recognize_video())
    btn_video.pack(pady=10, padx=20, fill=tk.X)

    btn_video = ttk.Button(frame, text="Powrót", command=lambda: return_to_main(frame, frame))
    btn_video.pack(pady=10, padx=20, fill=tk.X)