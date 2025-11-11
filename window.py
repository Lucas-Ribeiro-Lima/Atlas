import tkinter as tk
import threading
from os import path
from tkinter import ttk, filedialog, messagebox
from data_var import data_var
from parser import process

class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Atlas")
        self.root.geometry("480x240")
        self.root.resizable(False, False)
        self.config_window = None
        self.config_window_is_open = False

        # ======= Topbar com botão de config =======
        topbar = ttk.Frame(self.root, padding=5)
        topbar.pack(fill="both", expand=True)
        ttk.Label(topbar, text="Atlas OCR PDF → CSV", font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Button(topbar, text="⚙️", command=self.open_config).pack(side="right")

        # ======= Área principal =======
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill="both", expand=True)

        # ==========  Arquivo de entrada ==========
        pdf_entry = ttk.Entry(main, width=55)
        pdf_entry.insert(0, data_var["BASE_PATH"])
        pdf_entry.grid(row=0, column=0, pady=5, sticky="w")

        # ============ Botão de selecionar o arquivo ===========
        select_btn = ttk.Button(main, text="Selecionar PDF's",
                                command=lambda: set_configuration(pdf_entry, "BASE_PATH"), width=15)
        select_btn.grid(row=0, column=1, padx=5, pady=10)

        # ========== Botão de processamento ========
        process_button = ttk.Button(main, text="Processar", width=15)
        process_button.grid(row=1, column=1, pady=10, padx=5)

        cancel_button = ttk.Button(main, text="Cancelar", width=15)
        cancel_button.grid(row=1, column=0, pady=10, padx=5, sticky="e")
        cancel_button["state"] = "disabled"

        # ========== Informações gerais ==============
        info = ttk.Frame(self.root, padding=5)

        ttk.Label(info, text="Páginas extraidas: ").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        extracted_pages = ttk.Label(info, text=" ").grid(row=0, column=1, pady=5, padx=5, sticky="w")

        ttk.Label(info, text="Páginas com erro: ").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        error_pages = ttk.Label(info, text=" ").grid(row=1, column=1, pady=5, padx=5, sticky="w")

        # ======= Barra de progresso =======
        progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        progress_bar.pack(fill="x", side="bottom")

        # ======= Status =======
        status_label = ttk.Label(self.root, text="", relief="flat", anchor="w")
        status_label.pack(fill="x", side="bottom")

        timer_label = ttk.Label(self.root, text="Time remaining: ", relief="flat", anchor="e")
        timer_label.pack(fill="x", side="bottom")

        timer_value = ttk.Label(self.root, text="", relief="flat", anchor="e")
        timer_value.pack(fill="x", side="bottom")

        feedback = {
            "process_button": process_button,
            "cancel_button": cancel_button,
            "progress_bar": progress_bar,
            "status_label": status_label,
            "extracted_pages": extracted_pages,
            "error_pages": error_pages
        }

        process_button.config(command=lambda: handle_process(feedback))

    def open_config(self):
        if self.config_window_is_open:
            return

        self.config_window_is_open = True
        self.config_window = tk.Toplevel()
        self.config_window.title("Configurações")
        self.config_window.geometry("480x240")
        self.config_window.resizable(False, False)
        self.config_window.protocol("WM_DELETE_WINDOW", self.close_config_window)

        frm = ttk.Frame(self.config_window, padding=15)
        frm.pack(fill="both", expand=True)

        # === TRAINED DATA ===
        ttk.Label(frm, text="Pasta de dados treinados (Tesseract):").grid(row=0, column=0, sticky="w")
        trained_entry = ttk.Entry(frm, width=65)
        trained_entry.insert(0, data_var["TRAINED_DATA_DIR"])
        trained_entry.grid(row=1, column=0, pady=5, sticky="w")
        trained_btn = tk.Button(frm,
                                text="📁",
                                width=3,
                                command=lambda: set_directory(trained_entry,
                                                              "Selecione a pasta de dados treinados (Tesseract)"))
        trained_btn.grid(row=1, column=1)

        # === OUTPUT CSV ===
        ttk.Label(frm, text="Caminho do CSV de saída:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        csv_entry = ttk.Entry(frm, width=65)
        csv_entry.insert(0, data_var["OUTPUT_CSV"])
        csv_entry.grid(row=3, column=0, padx=(0, 10), pady=5, sticky="w")
        csv_btn = ttk.Button(frm,
                             text="📁",
                             width=3,
                             command=lambda: set_save_file(csv_entry,
                                                      "Selecione o arquivo CSV de saída", ".csv"))
        csv_btn.grid(row=3, column=1)

        # === SAVE BUTTON ===
        def save_config():
            data_var["TRAINED_DATA_DIR"] = trained_entry.get()
            data_var["OUTPUT_CSV"] = csv_entry.get()
            messagebox.showinfo("Configurações", "Configurações salvas com sucesso.")
            self.close_config_window()

        ttk.Button(frm, text="Salvar", command=save_config).grid(row=4, column=0, columnspan=2, pady=15, sticky="e")

    def close_config_window(self):
        self.config_window_is_open = False
        self.config_window.destroy()

    def render(self):
        self.root.mainloop()


def set_configuration(entry, label):
    selected = filedialog.askopenfilename(
        title="Selecione o PDF",
        defaultextension=".pdf"
    )
    if selected:
        data_var[label] = selected
        entry.delete(0, tk.END)
        entry.insert(0, data_var[label])


def set_directory(entry, message):
    path_dir = filedialog.askdirectory(title=message)
    if path_dir:
        entry.delete(0, tk.END)
        entry.insert(0, path_dir)


def set_save_file(entry, message, type):
    path_file = filedialog.asksaveasfilename(
        title=message,
        defaultextension=type,
        filetypes=[("", type)]
    )
    if path_file:
        entry.delete(0, tk.END)
        entry.insert(0, path_file)


def handle_process(feedback):
    if not path.exists(data_var["BASE_PATH"]):
        messagebox.showerror("Erro", "Caminho do PDF inválido.")
        return

    feedback["process_button"]["text"] = "Processando"
    feedback["process_button"]["state"] = "disabled"
    feedback["cancel_button"]["state"] = "normal"
    feedback["status_label"]["text"] = "Convertendo PDF para imagens..."
    feedback["progress_bar"]['value'] = 0

    def worker():
        try:
            process(data_var["BASE_PATH"], feedback)
        except Exception as e:
            feedback["status_label"]["text"] = f"❌ Erro: {e}"
            feedback["progress_bar"]['value'] = 100
        finally:
            feedback["process_button"]["state"] = "normal"
            feedback["cancel_button"]["state"] = "disabled"

    threading.Thread(target=worker, daemon=True).start()
