import csv
from os import path
from abc import ABC, abstractmethod

from data_var import data_var


class CsvWriter(ABC):
    @abstractmethod
    def write(self, content: dict[str, str]):
        pass


class DefaultCsvWriter(CsvWriter):
    def __init__(self, path_output: str = data_var["OUTPUT_CSV"]):
        self._writer: csv.DictWriter[str] | None = None
        self._path = path_output
        self._is_new_file = False

    def write(self, content: dict[str, str]):
        _is_new_file = not self._file_exists()
        with open(self._path, mode="a", newline="") as csv_file:
            self._writer = csv.DictWriter(csv_file, fieldnames=content.keys(), skipinitialspace=True)

            if self._is_new_file:
                self._write_header()

            self._writer.writerow(content)

    def _write_header(self):
        self._writer.writeheader()

    def _file_exists(self):
        return path.exists(self._path)

    def _is_writer_loaded_or_throw(self):
        if not self._writer:
            raise RuntimeError("CsvWriter has not been opened")
