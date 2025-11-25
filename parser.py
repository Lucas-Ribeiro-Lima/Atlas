import re
import pytesseract
import threading
import time

from os import path, listdir
from data_var import data_var
from utils import to_csv
from tkinter import messagebox
from pdf2image import convert_from_path

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


def handle_process(feedback):
    if not path.exists(data_var["BASE_PATH"]):
        messagebox.showerror("Erro", "Caminho do PDF inválido.")
        return

    feedback["process_button"]["text"] = "Processando..."
    feedback["process_button"]["state"] = "disabled"
    feedback["cancel_button"]["state"] = "normal"
    feedback["progress_bar"]['value'] = 0

    def worker():
        try:
            feedback["info"]()
            _process(data_var["BASE_PATH"], feedback)
        except Exception as e:
            feedback["status_label"]["text"] = f"❌ Erro: {e}"
            feedback["progress_bar"]['value'] = 0
        finally:
            feedback["process_button"]["state"] = "normal"
            feedback["process_button"]["text"] = "Processar"
            feedback["cancel_button"]["state"] = "disabled"
            feedback["info"]()

    threading.Thread(target=worker, daemon=True).start()

estimative_per_file = 120


def _process(dir_path, feedback):
    global estimative_per_file

    files = listdir(dir_path)
    total_files = len(files)
    success_pages = 0
    total_pages = 0

    for i, file in enumerate(files):
        start_time = time.perf_counter()
        total_estimative = total_files * estimative_per_file

        feedback["timer_label"][
            "text"] = f"Tempo estimado: {round(total_estimative - (i * estimative_per_file))} segundos"
        feedback["status_label"].config(text=f"Processando arquivo {i}/{total_files}")

        file_path = path.join(dir_path, file)
        [ success, total ] = _process_file(file_path, feedback)

        success_pages += success
        total_pages += total

        feedback["extracted_pages"]["text"] = success_pages
        feedback["error_pages"]["text"] = total_pages - success_pages

        feedback["progress_bar"]['value'] = (i / total_files) * 100
        feedback["progress_bar"].update()

        estimative_per_file = time.perf_counter() - start_time


    feedback["status_label"].config(text="✅ Processamento concluído!")
    feedback["timer_label"]["text"] = ""
    messagebox.showinfo("Concluído",
                        f"Conversão finalizada e CSV gerado.\n"
                        f"Páginas extraidas: {success_pages}\n"
                        f"Páginas com erro: {total_pages - success_pages}\n")


def _process_file(file, feedback):
    feedback["status_file"].config(text=f"   ======    Convertendo arquivo para imagens")
    images = convert_from_path(file, dpi=300)

    total_pages = len(images)
    success_pages = 0
    for i, image in enumerate(images, start=1):
        config = f'--oem 1 --psm 6 --tessdata-dir {data_var["TRAINED_DATA_DIR"]}'
        page_text = pytesseract.image_to_string(image, lang='por', config=config)

        feedback["status_file"].config(text=f"   ======    Processando página {i}/{total_pages}")
        success_pages += _process_page(page_text, i)

    return [ success_pages, total_pages ]


def _process_page(page_text, page_number):
    try:
        parsed_paged = _parse_page(page_text)
        to_csv(parsed_paged)
        return 1
    except Exception:
        print(f"Error on page: {page_number}")
        return 0


def _parse_page(page_text):
    text_pos_processed = _pos_processing_text(page_text)
    match = re.search(_RE_KVP, text_pos_processed)
    if not match:
         raise Exception("Invalid page")
    to_csv(match.group())

    return match.groupdict()


def _pos_processing_text(text):
    p1 = re.sub(r"[-—|°º]", " ", text)
    p2 = p1.replace("ç", "c").replace("ã", "a").replace("í", "i").replace("á", "a")
    return p2
