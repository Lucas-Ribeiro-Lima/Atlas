import re
import time
import unicodedata
from os import path, listdir
from abc import ABC, abstractmethod

from cnn_ai_model import CnnAiModel, Pytesseract
from pdf_parser import PdfParser, Pdf2Image
from csv_writter import CsvWriter, DefaultCsvWriter
from ui_notifier import UiNotifier, DefaultUiNotifier


class OcrParser(ABC):
    @abstractmethod
    def process(self, dir_path: str): ...


class DefaultOcrParser(OcrParser):
    _DATE = r"\d{2}/\d{2}/\d{4}"
    _RE_KVP = re.compile(
        rf"""
        Data\s+de\s+Emissao\s+(?P<DAT_EMISS>{_DATE})
        .*?
        Data\s+do\s+Vencimento\s+(?P<DAT_VENC>{_DATE})
        .*?
        N\s*Auto\s+de\s+Infracao:?\s+(?P<AI>\w{{6,7}})
        .*?
        (Concessionaria:?\s+(?P<CONC>[\w\s\-]+?)\s+Lancamento
        .*?
        Linha:\s+(?P<LINHA>[\w\s/\-|]+?)
        \s+Veiculo:\s*(?P<VEIC>\d{{4,6}})?
        \s+Placa:\s*(?P<PLACA>[A-Z0-9]{{7}})?
        \s+Data:\s+(?P<DAT_OCC>{_DATE})
        \s+Hora:\s+(?P<HORA_OCC>\d{{2}}:\d{{2}})
        \s+Local:\s+(?P<LOCAL>.*)\s+Base\s+legal
        .*?
        Descricao\s+da\s+infracao:\s+(?P<DESC>[^.]+)
        .*?)?
        Valor:\s+R\$\s*(?P<VALOR>[\d.,]+)
        """, re.DOTALL | re.IGNORECASE | re.VERBOSE
    )

    _estimative_acc = 1200
    _estimative_cnt = 1
    _total_estimative = 0
    _total_pages = 0
    _total_files = 0
    _successful_pages = 0

    def __init__(self,
                 feedback: dict[str, dict[str, str]],
                 cnn_ai_model: CnnAiModel = Pytesseract(),
                 pdf_parser: PdfParser = Pdf2Image(),
                 csv_writer: CsvWriter = DefaultCsvWriter(),
                 ui_notifier: UiNotifier = DefaultUiNotifier()):
        self._feedback = feedback
        self._pdf_parser = pdf_parser
        self._cnn_ai_model = cnn_ai_model
        self._csv_writer = csv_writer
        self._ui_notifier = ui_notifier

    def process(self, dir_path):
        self._verify_path(dir_path)
        self._total_pages = 0
        self._successful_pages = 0

        files = listdir(dir_path)
        self._total_files = len(files)
        self._successful_pages = 0

        for file_index, file in enumerate(files):
            start_time = time.perf_counter()
            self._actualize_timer_info(file_index)

            file_path = path.join(dir_path, file)
            self._process_file(file_path)

            self._actualize_gui_info(file_index)
            self._estimative_acc += time.perf_counter() - start_time
            self._estimative_cnt += 1

        self._display_conclude_message()

    def _process_file(self, file_path):
        self._display_message_on_label("status_file",
                                       "    Convertendo PDF...")

        pdf_data = self._pdf_parser.process(file_path)
        file_total_pages = len(pdf_data)
        self._total_pages += file_total_pages

        for i, data in enumerate(pdf_data, start=1):
            page_text = self._cnn_ai_model.process_image(data)
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
                                       f"Tempo estimado: {self._calculate_time_estimative(file_index)} horas")
        self._display_message_on_label("status_label",
                                       f"Processando arquivo {file_index}/{self._total_files}...")

    def _calculate_time_estimative(self, file_index):
        _estimative = round(self._estimative_acc / self._estimative_cnt)
        self._total_estimative = self._total_files * _estimative
        return round((self._total_estimative - (file_index * _estimative)) / (60 * 60), 2)

    def _actualize_gui_info(self, actual_file):
        self._display_message_on_label("extracted_pages", self._successful_pages)
        self._display_message_on_label("error_pages", self._total_pages - self._successful_pages)
        self._actualize_value_on_label("progress_bar", (actual_file / self._total_files) * 100)

    def _display_conclude_message(self):
        self._display_message_on_label("status_label", "✅ Processamento concluído!")
        self._display_message_on_label("time_label", "")
        self._ui_notifier.info("Concluído",
                               f"Conversão finalizada e CSV gerado.\n"
                               f"Páginas extraidas: {self._successful_pages}\n"
                               f"Páginas com erro: {self._total_pages - self._successful_pages}\n")

    def _display_message_on_label(self, label, message):
        self._feedback[label]["text"] = message

    def _actualize_value_on_label(self, label, value):
        self._feedback[label]["value"] = value
        self._feedback[label].update()

    def _verify_path(self, dir_path):
        if not path.exists(dir_path):
            self._ui_notifier.error("Erro", "Diretório especificado não existe")
            raise Exception("Diretório especificado não existe")


def _pos_processing_text(text):
    text = re.sub(r"[-—|°º]", " ", text)
    return unicodedata.normalize("NFD", text) \
        .encode("ascii", "ignore") \
        .decode("ascii")
