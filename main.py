import tkinter as tk
from tkinter import ttk

from configurator import configure
import gui


def main():
    root = tk.Tk()
    root.title("RiPO")
    root.geometry("300x350")
    root.configure(bg="#f0f0f0")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 300
    window_height = 350
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 12), padding=10)

    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(side=tk.TOP, padx=20, pady=20, expand=True)

    lbl_title = tk.Label(frame, text="RiPO", font=("Segoe UI", 16, "bold"), bg="#f0f0f0")
    lbl_title.pack(pady=15)

    btn_train = ttk.Button(frame, text="Dodaj wzorzec", command=lambda: gui.detect_page(root))
    btn_train.pack(pady=10, padx=20, fill=tk.X)

    btn_recognize = ttk.Button(frame, text="Rozpoznaj twarz", command=lambda: gui.recognize_page(root))
    btn_recognize.pack(pady=10, padx=20, fill=tk.X)

    btn_config = ttk.Button(frame, text="Konfigurator", command=configure)
    btn_config.pack(pady=10, padx=20, fill=tk.X)

    root.mainloop()


if __name__ == "__main__":
    main()