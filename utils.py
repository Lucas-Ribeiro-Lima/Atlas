import tkinter as tk
from tkinter import filedialog

from data_var import data_var

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

