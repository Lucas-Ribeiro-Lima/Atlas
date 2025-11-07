import re

RE_EMISSAO = re.compile(
    r"Data\s+de\s+Emiss[aã]o\s+(?P<DAT_EMISS>\d{2}/\d{2}/\d{4})",
    re.IGNORECASE
)

RE_VENC = re.compile(
    r"Data\s+do\s+Vencimento\s+(?P<DAT_VENC>\d{2}/\d{2}/\d{4})",
    re.IGNORECASE
)

RE_AI = re.compile(
    r"N[°º]?\s*Auto\s+de\s+Infra[cçgs][aã]o[:\s]*?(?P<AI>[\w$-]{5,8})",
    re.IGNORECASE
)

RE_CONC = re.compile(
    r"Concession[aá]ria[:\s]+(?P<CONC>[\w\s\-]+?)\s+Lan[cçgs]amento",
    re.IGNORECASE
)

RE_LINHA = re.compile(
    r"Linha[:\s]+(?P<LINHA>[\w\s/\-]+?)\s+Ve[ií]culo",
    re.IGNORECASE
)

RE_VEIC = re.compile(
    r"Ve[ií]culo[:\s]+(?P<VEIC>\d{4,6})",
    re.IGNORECASE
)

RE_PLACA = re.compile(
    r"Placa[:\s]+(?P<PLACA>[A-Z0-9]{7})",
    re.IGNORECASE
)

RE_DATA_OCC = re.compile(
    r"Data[:\s]+(?P<DAT_OCC>\d{2}/\d{2}/\d{4})",
    re.IGNORECASE
)

RE_HORA_OCC = re.compile(
    r"Hora[:\s]+(?P<HORA_OCC>\d{2}:\d{2})",
    re.IGNORECASE
)

RE_LOCAL = re.compile(
    r"Local[:\s]+(?P<LOCAL>[\w\s\-]{1,3})",
    re.IGNORECASE
)

RE_DESC = re.compile(
    r"Descri[cçgs][aã]o\s+da\s+infra[cçgs]ao[:\s]+(?P<DESC>[^.]+)",
    re.IGNORECASE | re.DOTALL
)

# Valor
RE_VALOR = re.compile(
    r"Valor[:\s]+R\$\s*(?P<VALOR>[\d.,]+)",
    re.IGNORECASE
)

def parse_pdf(pdf_data):
    campos = {}
    for regex in [
        RE_EMISSAO, RE_VENC, RE_AI, RE_CONC, RE_LINHA, RE_VEIC,
        RE_PLACA, RE_DATA_OCC, RE_HORA_OCC, RE_LOCAL, RE_DESC, RE_VALOR
    ]:
        match = regex.search(pdf_data)
        if match:
            campos.update(match.groupdict())
    return campos

