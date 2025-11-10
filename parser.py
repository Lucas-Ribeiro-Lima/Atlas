import re
import pytesseract
import threading
import time

from os import path
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
            process(data_var["BASE_PATH"], feedback)
        except Exception as e:
            feedback["status_label"]["text"] = f"❌ Erro: {e}"
            feedback["progress_bar"]['value'] = 0
        finally:
            feedback["process_button"]["state"] = "normal"
            feedback["process_button"]["text"] = "Processar"
            feedback["cancel_button"]["state"] = "disabled"
            feedback["info"]()

    threading.Thread(target=worker, daemon=True).start()

estimative_per_page = 10


def process(path, feedback):
    global estimative_per_page

    feedback["status_label"]["text"] = "Convertendo PDF para imagens..."
    images = convert_from_path(path, dpi=300)

    total = len(images)
    success_pages = 0
    for i, image in enumerate(images, start=1):
        start_time = time.perf_counter()
        total_estimative = total * estimative_per_page

        feedback["timer_label"][
            "text"] = f"Tempo estimado: {round(total_estimative - (i * estimative_per_page))} segundos"
        feedback["status_label"].config(text=f"Processando página {i}/{total}")

        config = f'--oem 1 --psm 6 --tessdata-dir {data_var["TRAINED_DATA_DIR"]}'
        page_text = pytesseract.image_to_string(image, lang='por', config=config)

        try:
            parsed_paged = parse_page(page_text)
            to_csv(parsed_paged)
            success_pages += 1
        except Exception:
            print(f"Error on page: {i}")
        finally:
            feedback["extracted_pages"]["text"] = success_pages
            feedback["error_pages"]["text"] = i - success_pages

        feedback["progress_bar"]['value'] = (i / total) * 100
        feedback["progress_bar"].update()
        estimative_per_page = time.perf_counter() - start_time

    feedback["status_label"].config(text="✅ Processamento concluído!")
    feedback["timer_label"]["text"] = ""
    messagebox.showinfo("Concluído",
                        f"Conversão finalizada e CSV gerado.\n"
                        f"Páginas extraidas: {success_pages}\n"
                        f"Páginas com erro: {total - success_pages}\n")


def parse_page(page_text):
    text_pos_processed = pos_processing_text(page_text)
    match = re.search(RE_KVP, text_pos_processed)
    if not match:
        raise Exception("Invalid page")

    return match.groupdict()


def pos_processing_text(text):
    p1 = re.sub(r"[-—|°º]", " ", text)
    p2 = p1.replace("ç", "c").replace("ã", "a").replace("í", "i").replace("á", "a")
    return p2
