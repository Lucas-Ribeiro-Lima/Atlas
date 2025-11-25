import tkinter as tk

from tkinter import ttk
from data_var import data_var
from parser import handle_process
from utils import set_configuration_directory
from config import Config

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        super().title("Atlas")
        super().geometry("640x280")
        super().resizable(False, False)
        self.main = None
        self.feedback = {}
        self.sub_windows_status = {}

    def render(self):
        self._top_bar_render()
        self._main_render()
        self._pdf_entry_render()
        self._actions_render()
        self._general_info_render()
        self._status_bar_render()
        self.mainloop()


    def _main_render(self):
        """Área principal"""
        self.main = ttk.Frame(self, padding=15)
        self.main.pack(fill="both", expand=True)

    def _top_bar_render(self):
        """Top bar rendering function."""
        topbar = ttk.Frame(self, padding=5)
        topbar.pack(fill="both", expand=True)
        ttk.Label(topbar,
                  text="Atlas OCR PDF → CSV",
                  font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Button(topbar, text="⚙️", command=lambda: self._open_sub_window(Config)).pack(side="right")

    def _pdf_entry_render(self):
        # ==========  Arquivo de entrada ==========
        pdf_entry = ttk.Entry(self.main, width=55)
        pdf_entry.insert(0, data_var["BASE_PATH"])
        pdf_entry.grid(row=0, column=0, pady=5, sticky="w")

        # ============ Botão de selecionar o arquivo ===========
        select_btn = ttk.Button(self.main, text="Selecionar diretório",
                                command=lambda: set_configuration_directory(pdf_entry, "BASE_PATH"), width=25)
        select_btn.grid(row=0, column=1, padx=5, pady=10)

    def _actions_render(self):
        # ========== Botão de processamento ========
        process_button = ttk.Button(self.main, text="Processar", width=15)
        process_button.grid(row=1, column=1, pady=10, padx=5)
        process_button.config(command=lambda: handle_process(self.feedback))

        cancel_button = ttk.Button(self.main, text="Cancelar", width=15)
        cancel_button.grid(row=1, column=0, pady=10, padx=5, sticky="e")
        cancel_button["state"] = "disabled"

        self.feedback["process_button"] = process_button
        self.feedback["cancel_button"] = cancel_button

    def _general_info_render(self):
        # ========== Informações gerais ==============
        info = ttk.Frame(self.main, padding=5)
        self.sub_windows_status["info"] = False

        ttk.Label(info, text="Páginas extraídas: ").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        extracted_pages = ttk.Label(info, text="0")
        extracted_pages.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        ttk.Label(info, text="Páginas com erro: ").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        error_pages = ttk.Label(info, text="0")
        error_pages.grid(row=1, column=1, pady=5, padx=5, sticky="w")

        def toggle_info():
            if self.sub_windows_status["info"]:
                info.pack_forget()
                self.sub_windows_status["info"] = False
            else:
                info.grid(row=2, column=0, pady=5, sticky="w")
                self.sub_windows_status["info"] = True

        self.feedback["info"] = toggle_info
        self.feedback["extracted_pages"] = extracted_pages
        self.feedback["error_pages"] = error_pages

    def _status_bar_render(self):
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, side="bottom")

        # ======= Barra de progresso =======
        progress_bar = ttk.Progressbar(frm, orient="horizontal", length=400, mode="determinate")
        progress_bar.pack(side="bottom", fill="x")

        # ======= Status =======
        status_label = ttk.Label(frm, text="", relief="flat")
        status_label.pack(side="left", anchor="w")

        # ========== File status =========
        status_file = ttk.Label(frm, text="", relief="flat")
        status_file.pack(side="left", anchor="e")

        timer_label = ttk.Label(frm, text="", relief="flat")
        timer_label.pack(side="right", anchor="w")

        self.feedback["progress_bar"] = progress_bar
        self.feedback["status_label"] = status_label
        self.feedback["status_file"] = status_file
        self.feedback["timer_label"] = timer_label


    def _open_sub_window(self, sub_window):
        if self.sub_windows_status.get(sub_window):
            return

        def on_close_cb():
            self.sub_windows_status[sub_window] = False

        self.sub_windows_status[sub_window] = True
        sub_window(on_close_cb)

