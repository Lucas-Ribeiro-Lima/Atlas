from abc import ABC, abstractmethod
from tkinter import messagebox

class UiNotifier(ABC):
    @abstractmethod
    def info(self, title, message): ...

    @abstractmethod
    def error(self, title, message): ...


class DefaultUiNotifier(UiNotifier):
    def info(self, title, message):
        messagebox.showinfo(title, message)

    def error(self, title, message):
        messagebox.showerror(title, message)