from abc import ABC, abstractmethod
from pdf2image import convert_from_path

class PdfParser(ABC):
    @abstractmethod
    def process(self, pdf_file):
        pass


class Pdf2Image(PdfParser):
    def process(self, pdf_path):
        return convert_from_path(pdf_path, dpi=300, thread_count=5)