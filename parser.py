import re

RE_KVP = re.compile(
    r"Data\s+de\s+Emiss[aã]o\s+(?P<DAT_EMISS>\d{2}/\d{2}/\d{4}).*"
    r"Data\s+do\s+Vencimento\s+(?P<DAT_VENC>\d{2}/\d{2}/\d{4}).*"
    r"N[°º]?\s*Auto\s+de\s+Infra[cç][aã]o:?\s+(?P<AI>[\w$-]{5,8}).*"
    r"Concession[aá]ria:?\s+(?P<CONC>[\w\s\-]+?)\s+Lan[cç]amento.*"
    r"Linha:[-—\s](?P<LINHA>[\w\s/\-|]+?)\s+Ve[ií]culo:(?:[-—\s]+(?P<VEIC>\d{4,6}))?\s+"
    r"Placa:(?:[-—\s]+(?P<PLACA>[A-Z0-9]{7}))?\s+"
    r"Data:[-—\s]+(?P<DAT_OCC>\d{2}/\d{2}/\d{4})\s+"
    r"Hora:[-—\s]+(?P<HORA_OCC>\d{2}:\d{2})\s+"
    r"Local?:[-—\s]+(?P<LOCAL>.*)\sBase\slegal.*"
    r"Descri[cç][aã]o\s+da\s+infra[cç][aã]o:\s+(?P<DESC>[^.]+).*"
    r"Valor:[-—\s]+R\$\s*(?P<VALOR>[\d.,]+)"
    , re.DOTALL | re.IGNORECASE | re.MULTILINE | re.UNICODE)


def parse_pdf(pdf_data):
    match = re.search(RE_KVP, pdf_data)
    if not match:
        raise Exception("Invalid PDF")

    return match.groupdict()
