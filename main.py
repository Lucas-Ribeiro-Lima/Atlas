import csv

from os import listdir, path
from parser import parse_pdf
from pdf2image import convert_from_path
import pytesseract


BASE_PATH = r"C:\Users\lucas\Downloads\Multas\Cobrança de multas - 803 - 09-12-24.pdf"
TRAINED_DATA_DIR = r"C:\Users\lucas\Downloads\traineddata"
OUTPUT_CSV = r"C:\Users\lucas\Downloads\test.csv"

is_new_file = not path.exists(OUTPUT_CSV)

def to_csv(kvp_dict):
    global is_new_file
    with open(OUTPUT_CSV, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=kvp_dict.keys(), skipinitialspace=True)
        if is_new_file:
            writer.writeheader()
            is_new_file = False
        writer.writerow(kvp_dict)

def process(images):
    for image in images:
        config = f'--oem 1 --tessdata-dir {TRAINED_DATA_DIR}'
        text_pdf = pytesseract.image_to_string(image, lang='por', config=config)
        to_csv(parse_pdf(text_pdf))

def main():
    try:
        images = convert_from_path(BASE_PATH)
        process(images)

    except Exception as e:
        print(e)
    return

main()