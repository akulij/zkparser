from enum import Enum
import httpx


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

async def get_page_content(wallet: str, pro_code: str, chain: Chain) -> str:
    url = gen_url(wallet, pro_code, chain)
    async with httpx.AsyncClient() as client:
        r = await client.get(url)

    return str(r.content)
