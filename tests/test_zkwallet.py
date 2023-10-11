import sys
from pytest import raises
sys.path.append("..")

from zk import *
from parser import *


def test_urlgen():
    url = "https://www.10kdrop.com/starknetresults?walletAddress=WALLET&proCode=PROCODE"
    assert gen_url("WALLET", "PROCODE", Chain.STARKNET) == url
    with raises(WrongChainException) as execinfo:
        gen_url("", "", "WRONG")
