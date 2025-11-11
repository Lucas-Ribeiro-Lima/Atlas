import re
import pytesseract
from data_var import data_var
from utils import to_csv
from tkinter import messagebox
from pdf2image import convert_from_path

RE_KVP = re.compile(
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

def process(path, feedback):
    images = convert_from_path(path, dpi=300)
    total = len(images)
    for i, image in enumerate(images, start=1):
        feedback["status_label"].config(text=f"Processando página {i}/{total}...")
        config = f'--oem 1 --psm 6 --tessdata-dir {data_var["TRAINED_DATA_DIR"]}'
        text_pdf = pytesseract.image_to_string(image, lang='por', config=config)
        parsed_pdf = parse_pdf(text_pdf)
        to_csv(parsed_pdf)
        feedback["progress_bar"]['value'] = (i / total) * 100
        feedback["progress_bar"].update()

    feedback["status_label"].config(text="✅ Processamento concluído!")
    messagebox.showinfo("Concluído", "Conversão finalizada e CSV gerado.")


def parse_pdf(pdf_data):
    text_pos_processed = pos_processing_text(pdf_data)
    match = re.search(RE_KVP, text_pos_processed)
    if not match:
        raise Exception("Invalid PDF")

    return match.groupdict()

def pos_processing_text(text):
    p1 = re.sub(r"[-—|°º]", " ", text)
    p2 = p1.replace("ç", "c").replace("ã", "a").replace("í", "i").replace("á", "a")
    return p2

