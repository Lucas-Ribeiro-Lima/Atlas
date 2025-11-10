import tkinter as tk
import threading
from os import path
from tkinter import ttk, filedialog, messagebox
from configs import configs
from parser import process

# =============================
# GUI PRINCIPAL
# =============================
config_windows_is_open = False

def render():
    root = tk.Tk()
    root.title("Atlas - OCR PDF → CSV")
    root.geometry("480x240")
    root.resizable(False, False)

    # ======= Topbar com botão de config =======
    topbar = ttk.Frame(root, padding=5)
    topbar.pack(fill="x")
    ttk.Label(topbar, text="Atlas OCR → CSV", font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)
    ttk.Button(topbar, text="⚙️", command=open_config).pack(side="right")

    # ======= Área principal =======
    main = ttk.Frame(root, padding=15)
    main.pack(fill="both", expand=True)

    ttk.Button(main, text="Selecionar PDF", command=lambda: set_configuration("BASE_PATH"), width=20).grid(row=0, column=0, padx=5, pady=10)
    process_button = ttk.Button(main, text="Processar PDFs", width=20)
    process_button.grid(row=0, column=1, padx=5, pady=10)

    # ======= Barra de progresso =======
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(fill="x", side="bottom")

    # ======= Status =======
    status_label = ttk.Label(root, text="", relief="flat", anchor="w")
    status_label.pack(fill="x", side="bottom")

    # Conecta o botão de processamento
    process_button.config(command=lambda: handle_process(progress_bar, status_label, process_button))

    root.mainloop()

def set_configuration(label):
    selected = filedialog.askopenfilename(
        title="Selecione o arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    if selected:
        configs[label] = selected
        messagebox.showinfo("Arquivo selecionado", f"{label} definido como:\n{selected}")

def set_trained_data(entry):
    path_dir = filedialog.askdirectory(title="Selecione a pasta de dados treinados (Tesseract)")
    if path_dir:
        entry.delete(0, tk.END)
        entry.insert(0, path_dir)

def set_output_csv(entry):
    path_file = filedialog.asksaveasfilename(
        title="Selecione o arquivo CSV de saída",
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")]
    )
    if path_file:
        entry.delete(0, tk.END)
        entry.insert(0, path_file)

def open_config():
    global config_windows_is_open
    if config_windows_is_open:
        return

    config_windows_is_open = True
    config_win = tk.Toplevel()
    config_win.title("Configurações")
    config_win.geometry("480x240")
    config_win.resizable(False, False)

    config_win.protocol("WM_DELETE_WINDOW", lambda: close_window(config_win))

    frm = ttk.Frame(config_win, padding=15)
    frm.pack(fill="both", expand=True)

    # === TRAINED DATA ===
    ttk.Label(frm, text="Pasta de dados treinados (Tesseract):").grid(row=0, column=0, sticky="w")
    trained_entry = ttk.Entry(frm, width=65)
    trained_entry.insert(0, configs["TRAINED_DATA_DIR"])
    trained_entry.grid(row=1, column=0, pady=5, sticky="w")
    ttk.Button(frm, text="📁", width=3, command=lambda: set_trained_data(trained_entry)).grid(row=1, column=1)

    # === OUTPUT CSV ===
    ttk.Label(frm, text="Caminho do CSV de saída:").grid(row=2, column=0, sticky="w", pady=(10, 0))
    csv_entry = ttk.Entry(frm, width=65)
    csv_entry.insert(0, configs["OUTPUT_CSV"])
    csv_entry.grid(row=3, column=0, padx=(0, 10), pady=5, sticky="w")
    ttk.Button(frm, text="📁", width=3, command=lambda: set_output_csv(csv_entry)).grid(row=3, column=1)

    # === SAVE BUTTON ===
    def save_config():
        configs["TRAINED_DATA_DIR"] = trained_entry.get()
        configs["OUTPUT_CSV"] = csv_entry.get()
        messagebox.showinfo("Configurações", "Configurações salvas com sucesso.")
        config_win.destroy()

    ttk.Button(frm, text="Salvar", command=save_config).grid(row=4, column=0, columnspan=2, pady=15, sticky="e")


def handle_process(progress_bar, status_label, process_button):
    """Dispara o processamento OCR em uma thread separada."""
    pdf_path = configs["BASE_PATH"]
    if not path.exists(pdf_path):
        messagebox.showerror("Erro", "Caminho do PDF inválido.")
        return

    process_button.config(state="disabled")
    status_label.config(text="Convertendo PDF para imagens...")
    progress_bar['value'] = 0

    def worker():
        try:
            process(configs["BASE_PATH"], progress_bar, status_label, process_button)
        except Exception as e:
            status_label.config(text=f"❌ Erro: {e}")
            process_button.config(state="normal")

    threading.Thread(target=worker, daemon=True).start()


def close_window(window):
    global config_windows_is_open
    config_windows_is_open = False
    window.destroy()