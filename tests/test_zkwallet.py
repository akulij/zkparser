import sys
from pytest import raises, mark
sys.path.append("..")

from zkparser.zk import *
from zkparser.parser import *


pytest_plugins = ('pytest_asyncio',)


def test_urlgen():
    url = "https://www.10kdrop.com/starknetresults?walletAddress=WALLET&proCode=PROCODE"
    assert gen_url("WALLET", "PROCODE", Chain.STARKNET) == url
    with raises(WrongChainException) as execinfo:
        gen_url("", "", "WRONG")

@mark.asyncio
async def test_wallet_era():
    wallet = "0x686D64EDf5532912C2a1cd3a249b0e9363f81baD"
    pro_code = "elemgmU13"
    eraw = await get_wallet_era(wallet, pro_code)
    # print(eraw)

@mark.asyncio
async def test_wallet_linea():
    wallet = "0x686D64EDf5532912C2a1cd3a249b0e9363f81baD"
    pro_code = "elemgmU13"
    eraw = await get_wallet_linea_mainnet(wallet, pro_code)
    print(eraw)

@mark.asyncio
async def test_wallet_scrool():
    wallet = "0xd83690Cb555FCA66FD572f9b7A27dE79bF5D9B06"
    pro_code = "elemgmU13"
    info = await get_wallet_scroll(wallet, pro_code)
    print(info)

@mark.asyncio
async def test_wallet_zero():
    wallet = "0xa3f7FE5f82eA5DB2e8F163AfB99494b3f0c278a6"
    pro_code = "elemgmU13"
    info = await get_wallet_zero(wallet, pro_code)
    print(info)
