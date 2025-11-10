from configs import configs
from os import path
import csv

def to_csv(kvp_dict):
    """Salva o dicionário de dados no CSV, criando cabeçalho se necessário."""
    csv_path = configs["OUTPUT_CSV"]
    is_new_file = not path.exists(csv_path)

    with open(csv_path, 'a', newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=kvp_dict.keys(), skipinitialspace=True)
        if is_new_file:
            writer.writeheader()
        writer.writerow(kvp_dict)