from utils import *
from tkinter import ttk, messagebox
from data_var import data_var


class Config(tk.Toplevel):
    def __init__(self, cb):
        super().__init__()
        self.title("Configurações")
        self.geometry("480x240")
        self.resizable(False, False)
        self._on_close_cb = cb
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.render()

    def render(self):
        frm = ttk.Frame(self, padding=15)
        frm.pack(fill="both", expand=True)

        self.trained_data_render(frm)
        self.output_csv_render(frm)
        self.save_button_render(frm)

    def trained_data_render(self, parent):
        # === TRAINED DATA ===
        ttk.Label(parent, text="Pasta de dados treinados (Tesseract):").grid(row=0, column=0, sticky="w")
        trained_entry = ttk.Entry(parent, width=65)
        trained_entry.insert(0, data_var["TRAINED_DATA_DIR"])
        trained_entry.grid(row=1, column=0, pady=5, sticky="w")
        trained_btn = tk.Button(parent,
                                text="📁",
                                width=3,
                                command=lambda: set_configuration_directory(trained_entry,
                                                                            "TRAINED_DATA_DIR"))
        trained_btn.grid(row=1, column=1)

        return trained_entry

    def output_csv_render(self, parent):
        # === OUTPUT CSV ===
        ttk.Label(parent, text="Caminho do CSV de saída:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        csv_entry = ttk.Entry(parent, width=65)
        csv_entry.insert(0, data_var["OUTPUT_CSV"])
        csv_entry.grid(row=3, column=0, padx=(0, 10), pady=5, sticky="w")
        csv_btn = ttk.Button(parent,
                             text="📁",
                             width=3,
                             command=lambda: set_configuration_save_file(csv_entry,
                                                                         "OUTPUT_CSV",
                                                                         "Selecione o arquivo CSV de saída",
                                                                         ".csv"))
        csv_btn.grid(row=3, column=1)
        return csv_entry

    def save_button_render(self, parent):
        # === SAVE BUTTON ===
        def save_config():
            messagebox.showinfo("Configurações", "Configurações salvas com sucesso.")
            self.on_close()

        ttk.Button(parent, text="Salvar", command=save_config).grid(row=4, column=0, columnspan=2, pady=15, sticky="e")

    def on_close(self):
        self._on_close_cb()
        self.destroy()
