import re
import time
from os import path, listdir
from abc import ABC, abstractmethod

from cnn_ai_model import CnnAiModel, Pytesseract
from pdf_parser import PdfParser, Pdf2Image
from csv_writter import CsvWriter, DefaultCsvWriter
from tkinter import messagebox

class OcrParser(ABC):
    @abstractmethod
    def process(self, dir_path: str):
        pass

class DefaultOcrParser(OcrParser):
    _RE_KVP = re.compile(
        r"Data\s+de\s+Emissao\s+(?P<DAT_EMISS>\d{2}/\d{2}/\d{4}).*"
        r"Data\s+do\s+Vencimento\s+(?P<DAT_VENC>\d{2}/\d{2}/\d{4}).*"
        r"N\s*Auto\s+de\s+Infracao:?\s+(?P<AI>\w{6,7}).*"
        r"Concessionaria:?\s+(?P<CONC>[\w\s\-]+?)\s+Lancamento.*"
        r"Linha:[\s](?P<LINHA>[\w\s/\-|]+?)\s+Veiculo:(?:[\s]+(?P<VEIC>\d{4,6}))?\s+"
        r"Placa:(?:[\s]+(?P<PLACA>[A-Z0-9]{7}))?\s+"
        r"Data:[\s]+(?P<DAT_OCC>\d{2}/\d{2}/\d{4})\s+"
        r"Hora:[\s]+(?P<HORA_OCC>\d{2}:\d{2})\s+"
        r"Local?:[\s]+(?P<LOCAL>.*)\sBase\slegal.*"
        r"Descricao\s+da\s+infracao:\s+(?P<DESC>[^.]+).*"
        r"Valor:[\s]+R\$\s*(?P<VALOR>[\d.,]+)"
        , re.DOTALL | re.IGNORECASE | re.MULTILINE | re.UNICODE)

    _estimative_per_file = 120
    _total_estimative = 120
    _total_pages = 0
    _total_files = 0
    _successful_pages = 0

    def __init__(self,
                 feedback: dict[str, dict[str, str]],
                 cnn_ai_model: CnnAiModel = Pytesseract(),
                 pdf_parser: PdfParser = Pdf2Image(),
                 csv_writer: CsvWriter = DefaultCsvWriter()):
        self._feedback = feedback
        self._pdf_parser = pdf_parser
        self._cnn_ai_model = cnn_ai_model
        self._csv_writer = csv_writer

    def process(self, dir_path):
        _verify_path(dir_path)
        files = listdir(dir_path)
        self._total_files = len(files)
        self._successful_pages = 0

        for file_index, file in enumerate(files):
            start_time = time.perf_counter()
            self._actualize_timer_info(file_index)

            file_path = path.join(dir_path, file)
            self._process_file(file_path)

            self._actualize_gui_info(file_index)
            self._estimative_per_file = time.perf_counter() - start_time

        self._display_conclude_message()

    def _process_file(self, file_path):
        self._display_message_on_label("status_file",
                                       "    Convertendo arquivo para imagens...")
        images = self._pdf_parser.pdf_to_image(file_path)

        file_total_pages = len(images)
        self._total_pages += file_total_pages

        for i, image in enumerate(images, start=1):
            page_text = self._cnn_ai_model.process_image(image)
            self._display_message_on_label("status_file",
                                           f"    Processando página {i}/{file_total_pages}...")
            self._successful_pages += self._process_page(page_text, i)

    def _process_page(self, page_text, page_number):
        try:
            page_dict = self._parse_page(page_text)
            self._csv_writer.write(page_dict)
            return 1
        except ValueError:
            print(f"Error on page: {page_number}")
            return 0

    def _parse_page(self, page_text):
        text_pos_processed = _pos_processing_text(page_text)
        match = re.search(self._RE_KVP, text_pos_processed)
        if not match:
            raise ValueError("Invalid page")

        return match.groupdict()

    def _actualize_timer_info(self, file_index):
        self._display_message_on_label("timer_label",
                                       f"Tempo estimado: {self._calculate_time_estimative(file_index)} segundos")
        self._display_message_on_label("status_label",
                                       f"Processando arquivo {file_index}/{self._total_files}...")

    def _calculate_time_estimative(self, file_index):
        self._recalculate_total_time_estimative()
        return round(self._total_estimative - (file_index * self._estimative_per_file))

    def _recalculate_total_time_estimative(self):
        self._total_estimative = self._total_files * self._estimative_per_file

    def _actualize_gui_info(self, actual_file):
        self._display_message_on_label("extracted_pages", self._successful_pages)
        self._display_message_on_label("error_pages", self._total_pages - self._successful_pages)
        self._actualize_value_on_label("progress_bar", (actual_file / self._total_files) * 100)

    def _display_conclude_message(self):
        self._display_message_on_label("status_label", "✅ Processamento concluído!")
        self._display_message_on_label("time_label", "")
        _display_dialog_warn("Concluído",
                             f"Conversão finalizada e CSV gerado.\n"
                             f"Páginas extraidas: {self._successful_pages}\n"
                             f"Páginas com erro: {self._total_pages - self._successful_pages}\n")

    def _display_message_on_label(self, label, message):
        self._feedback[label]["text"] = message

    def _actualize_value_on_label(self, label, value):
        self._feedback[label]["value"] = value
        self._feedback[label].update()


def _display_dialog_warn(title, message):
    messagebox.showinfo(title, message)


def _pos_processing_text(text):
    p1 = re.sub(r"[-—|°º]", " ", text)
    p2 = (p1
          .replace("ç", "c")
          .replace("ã", "a")
          .replace("í", "i")
          .replace("á", "a"))
    return p2

def _verify_path(dir_path):
    if not path.exists(dir_path):
        messagebox.showerror("Erro", "Diretório especificado não existe")
        raise Exception("Diretório especificado não existe")