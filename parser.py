import re

RE_KVP = re.compile(
    r"Data\s+de\s+Emiss[aãsd4]o\s+(?P<DAT_EMISS>\d{2}/\d{2}/\d{4}).*"
    r"Data\s+do\s+Vencimento\s+(?P<DAT_VENC>\d{2}/\d{2}/\d{4}).*"
    r"N[°º]?\s*Auto\s+de\s+Infra[cçgs][aãsd4]o:?\s+(?P<AI>[\w$-]{5,8}).*"
    r"Concession[aád4]ria:?\s+(?P<CONC>[\w\s\-]+?)\s+Lan[cçgsd4]amento.*"
    r"Linha:?\s+(?P<LINHA>[\w\s/\-]+?)\s+Ve[ií]culo:?\s+(?P<VEIC>\d{4,6})\s+"
    r"Placa:?\s+(?P<PLACA>[A-Z0-9]{7})\s+"
    r"Data:?\s+(?P<DAT_OCC>\d{2}/\d{2}/\d{4})\s+"
    r"Hora:[^.]*?(?P<HORA_OCC>\d{2}:\d{2})\s+"
    r"Local:?\s+(?P<LOCAL>[^.]*?)\sBase\slegal.*"
    r"Descri[cçgs][aãsd4]o\s+da\s+infra[cçgs]ao:\s+(?P<DESC>[^.]+).*"
    r"Valor:?\s+R\$\s*(?P<VALOR>[\d.,]+)"
    , re.DOTALL | re.IGNORECASE | re.MULTILINE)


def parse_pdf(pdf_data):
    match = re.search(RE_KVP, pdf_data)
    if not match:
        raise Exception("Invalid PDF")

    return match.groupdict()
