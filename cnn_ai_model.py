import pytesseract

from abc import ABC, abstractmethod
from data_var import data_var

class CnnAiModel(ABC):
    @abstractmethod
    def process_image(self, image):
        pass


class Pytesseract(CnnAiModel):
    _env_vars = data_var
    _ocr_pytesseract_config = f'--oem 1 --psm 6 --tessdata-dir {_env_vars["TRAINED_DATA_DIR"]}'
    _language = 'por'

    def __init__(self):
        pass

    def process_image(self, image):
        return pytesseract.image_to_string(image, lang=self._language, config=self._ocr_pytesseract_config)
