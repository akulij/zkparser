import re
from enum import Enum
import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag

from .utils import readtimeout_retry


class Chain(Enum):
    ERA = "ERA"
    ZERO = "ZERO"
    STARKNET = "STARKNET"
    SCROLL = "SCROLL"
    LINEA = "LINEA"
    POLYGON = "POLYGON"
    SYBIL = "SYBIL"

class WrongChainException(Exception):
    pass


def gen_url(wallet: str, pro_code: str, chain: Chain) -> str:
    ERA = f"https://www.10kdrop.com/results?walletAddress={wallet}&walletAddress2=&walletAddress3=&walletAddress4=&proCode={pro_code}"
    ZERO = f"https://www.10kdrop.com/layerzeroresults?walletAddress={wallet}&proCode={pro_code}"
    STARKNET = f"https://www.10kdrop.com/starknetresults?walletAddress={wallet}&proCode={pro_code}"
    SCROLL = f"https://www.10kdrop.com/scrollresults?walletAddress={wallet}&proCode={pro_code}"
    LINEA = f"https://www.10kdrop.com/linearesults?walletAddress={wallet}&proCode={pro_code}"
    POLYGON = f"https://www.10kdrop.com/polygonzkevmresults?walletAddress={wallet}&proCode={pro_code}"
    SYBIL = f"https://www.10kdrop.com/sybilcheckresults?walletAddress={wallet}&proCode={pro_code}"

    if chain == Chain.ERA: url = ERA
    elif chain == Chain.ZERO: url = ZERO
    elif chain == Chain.STARKNET: url = STARKNET
    elif chain == Chain.SCROLL: url = SCROLL
    elif chain == Chain.LINEA: url = LINEA
    elif chain == Chain.POLYGON: url = POLYGON
    elif chain == Chain.SYBIL: url = SYBIL
    else: raise WrongChainException

    return url

@readtimeout_retry(5)
async def get_page_content(wallet: str, pro_code: str, chain: Chain) -> str:
    url = gen_url(wallet, pro_code, chain)
    async with httpx.AsyncClient() as client:
        print(f"making request to {url=}")
        r = await client.get(url, timeout=20)

    return str(r.content)

def get_var_declaration_value(content: str, variable_name: str, declaration: str | None = None) -> str:
    var_declaration = f"const {variable_name} = ([a-zA-Z\\d\".;]+)"
    if declaration: var_declaration = declaration
    match = re.search(var_declaration, content)
    value: str = match.group(1)
    val = value.split("//")[0].replace(";", "").replace('"', "").replace("None", "-1")
    if val == "":
        return "0"

    return val

def find_match(content: str, regex: str):
    return re.search(regex, content).group()

def get_eth_price(page: str) -> float:
    value = float(get_var_declaration_value(page, "window.ethusd_price", "window.ethusd_price = ([\\d\".;]+)"))

    return value

def str_array(arr: str) -> list[int]:
    return re.findall(r"\d+", arr)

def get_elem_content(page: str, elem_id: str) -> str | None:
    bs = BeautifulSoup(page, "html.parser")

    elem = bs.select_one(f"#{elem_id}")
    if not elem: return None
    
    return "".join(map(lambda x: str(x), elem.contents))


def get_table_row_value(page: str, row: int) -> str:
    bs = BeautifulSoup(page, "html.parser")

    table = bs.select_one("#walletResults1")

    rows = table.find_all("tr")
    rows: list[Tag] = list(rows)

    r = rows[row]
    column: Tag = list(r.find_all("td"))[-1]

    return "".join(map(lambda x: str(x), column.contents))
