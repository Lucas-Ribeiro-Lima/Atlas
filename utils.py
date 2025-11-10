import csv
import tkinter as tk

from os import path
from data_var import data_var
from tkinter import filedialog


def to_csv(kvp_dict):
    """Salva o dicionário de dados no CSV, criando cabeçalho se necessário."""
    csv_path = data_var["OUTPUT_CSV"]
    is_new_file = not path.exists(csv_path)

    with open(csv_path, 'a', newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=kvp_dict.keys(), skipinitialspace=True)
        if is_new_file:
            writer.writeheader()
        writer.writerow(kvp_dict)

def set_configuration_filename(entry, label):
    selected = filedialog.askopenfilename(
        title="Selecione o PDF",
        defaultextension=".pdf"
    )
    if selected:
        data_var[label] = selected
        entry.delete(0, tk.END)
        entry.insert(0, data_var[label])

def set_configuration_directory(entry, label):
    path_dir = filedialog.askdirectory()
    if path_dir:
        data_var[label] = path_dir
        entry.delete(0, tk.END)
        entry.insert(0, path_dir)


def set_configuration_save_file(entry, label, message, file_type):
    path_file = filedialog.asksaveasfilename(
        title=message,
        defaultextension=file_type,
        filetypes=[("", file_type)]
    )
    if path_file:
        data_var[label] = path_file
        entry.delete(0, tk.END)
        entry.insert(0, path_file)

