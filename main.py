import csv

from os import listdir, path
from parser import parse_pdf
from pdf2image import convert_from_path
import pytesseract

BASE_PATH = r"C:\Users\lucas.lima\Downloads\multas"
OUTPUT_CSV = r"C:\Users\lucas.lima\Downloads\test.csv"

is_new_file = not path.exists(OUTPUT_CSV)

def to_csv(kvp_dict):
    global is_new_file
    with open(OUTPUT_CSV, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=kvp_dict.keys())
        if is_new_file:
            writer.writeheader()
        writer.writerow(kvp_dict)

def main():
    try:
        for file in listdir(BASE_PATH):
            images = convert_from_path(path.join(BASE_PATH, file))
            for image in images:
                text_pdf = pytesseract.image_to_string(image)
                to_csv(parse_pdf(text_pdf))
    except Exception as e:
        print(e)
    return

main()