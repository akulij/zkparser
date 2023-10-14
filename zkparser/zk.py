from typing import Literal
from pydantic import BaseModel

from zkparser.parser import (
        Chain,
        get_page_content,
        get_var_declaration_value,
        find_match,
        get_eth_price,
        str_array,
        get_elem_content,
        get_table_row_value,
                    )


class WalletEra(BaseModel):
    wallet: str
    page: str
    rank: int
    balance: float
    balance_usd: float
    transactions: int
    internal_txdone: int
    last_transaction: str
    total_gas: float
    transaction_months: list[int]
    aggregate_eth: float
    aggregate_usd: float | None # None because it is not currently implemented on site
    protocols_amount: int
    is_native_bridge_used: bool

class WalletEraVerbose(BaseModel):
    wallet: str
    rank: int | Literal["+650'000"]
    balance: float
    transactions: int
    last_transaction: str
    total_gas: float
    transaction_months: list[int]
    aggregate_eth: float
    aggregate_usd: float | None # None because it is not currently implemented on site
    protocols_amount: int
    is_native_bridge_used: bool

class WalletLite(BaseModel):
    wallet: str
    balance: float
    transactions: int
    last_transaction: str 
    total_gas: float
    aggregate_eth: float
    total_investment: float
    total_investment_usd: float
    potential_earning: tuple[int, int]

class WalletZero(BaseModel):
    wallet: str
    rank: int
    transactions: int
    bridged: float
    source_chains: int
    destination_chains: int
    interacted_contracts: int
    active_days: int
    active_weeks: int
    active_months: int
    potential_earning: tuple[int, int] | None

class WalletLinea(BaseModel):
    wallet: str
    balance_eth: float | None
    balance_usdc: float | None
    transactions: float
    is_native_bridge_used: bool
    first_tx_date: str
    tx_months: list[int]
    active_months: int
    active_weeks: int
    active_days: int
    last_tx_date: str

class WalletStarknet(BaseModel):
    wallet: str
    transactions: int
    tx_months: str
    active_months: int
    active_weeks: int
    active_days: int
    did_swap: bool
    did_mint: bool
    did_add_liquidity: bool
    did_remove_liquidity: bool
    total_gas: float
    aggregate_tx: float
    first_transaction: str
    last_transaction: str

class WalletScroll(BaseModel):
    wallet: str
    balance_eth: float
    balance_usdc: float
    transactions: int
    is_native_bridge_used: bool
    first_tx_date: str
    tx_months: list[int]
    last_tx_date: str

class WalletSybil(BaseModel):
    wallet: str
    is_blacklisted: bool


async def get_wallet_era(wallet: str, pro_code: str, page: str | None = None) -> WalletEra | None:
    if not page:
        page = await get_page_content(wallet, pro_code, Chain.ERA)
    ethusd = get_eth_price(page)

    try:
        rank = int(get_var_declaration_value(page, "value1_fixed_erarank"))
        balance = float(get_var_declaration_value(page, "value1"))
        balance_usd = balance * ethusd
        transactions = int(get_var_declaration_value(page, "value2"))
        last_transaction = find_match(page, r"\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d\dZ")
        total_gas = float(get_var_declaration_value(page, "value1_gasfees"))
        transaction_months = str_array(get_table_row_value(page, 7))
        _txdone = int(get_var_declaration_value(page, "value3"))
        aggregate_eth = float(get_var_declaration_value(page, "value4"))
        aggregate_usd = float(get_var_declaration_value(page, "valueUsdcPro1unfixed"))
        aggr_usd_treshold = bool(int(get_var_declaration_value(page, "thresholdUsdcPro1")))
        if not aggr_usd_treshold:
            aggregate_usd = None # disable till not implemented on site
        protocols_amount = int(get_var_declaration_value(page, "valuePro1"))
        is_native_bridge_used = bool(int(get_var_declaration_value(page, "valuePro2")))
    except AttributeError:
        return None

    return WalletEra(
            wallet=wallet,
            page=page,
            rank=rank,
            balance=balance,
            balance_usd=balance_usd,
            transactions=transactions,
            internal_txdone=_txdone,
            last_transaction=last_transaction,
            total_gas=total_gas,
            transaction_months=transaction_months,
            aggregate_eth=aggregate_eth,
            aggregate_usd=aggregate_usd,
            protocols_amount=protocols_amount,
            is_native_bridge_used=is_native_bridge_used
            )

async def get_wallet_era_verbose(wallet: WalletEra) -> WalletEraVerbose | None:
    return WalletEraVerbose(
            wallet=wallet.wallet,
            rank="+650'000" if wallet.rank == 0 else wallet.rank,
            balance=wallet.balance,
            transactions=wallet.transactions,
            last_transaction=wallet.last_transaction,
            total_gas=wallet.total_gas,
            transaction_months=wallet.transaction_months,
            aggregate_eth=wallet.aggregate_eth,
            aggregate_usd=wallet.aggregate_usd,
            protocols_amount=wallet.protocols_amount,
            is_native_bridge_used=wallet.is_native_bridge_used
            )

async def get_wallet_lite(wallet: str, pro_code: str, page: str | None = None) -> WalletLite | None:
    if not page:
        page = await get_page_content(wallet, pro_code, Chain.ERA)
    ethusd = get_eth_price(page)
    try:
        balance = float(get_var_declaration_value(page, "value1_lite_bal"))
        transactions = int(get_var_declaration_value(page, "value5"))
        last_transaction = find_match(page, r"\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d")
        total_gas = float(get_var_declaration_value(page, "value1_gasfees_lite"))
        aggregate_eth = float(get_var_declaration_value(page, "value1_lite_totalamount"))
        total_investment = total_gas + float(get_var_declaration_value(page, "value1_gasfees"))
        total_investment_usd = total_investment * ethusd
    except AttributeError:
        return None
    
    we = await get_wallet_era(wallet, pro_code, page)
    if not we: return None
    wl = WalletLite(
            wallet=wallet,
            balance=balance,
            transactions=transactions,
            last_transaction=last_transaction,
            total_gas=total_gas,
            aggregate_eth=aggregate_eth,
            total_investment=total_investment,
            total_investment_usd=total_investment_usd,
            potential_earning=(0, 0)
            )
    potential_earning = _calc_potential_lite(we, wl)
    wl.potential_earning = potential_earning

    return wl

def _calc_potential_lite(we: WalletEra, wl: WalletLite) -> tuple[int, int]:
    counter = 0
    counter2 = 0
    if we.balance > 0.005: counter += 1
    if we.transactions > 10: counter += 1
    if we.internal_txdone > 2: counter += 1
    if we.aggregate_eth > 1: counter += 1
    if we.protocols_amount > 3: counter2 += 1
    if we.is_native_bridge_used: counter2 += 1

    if wl.transactions > 0: counter += 1

    if counter == 0:
        return (0, 0)
    elif counter == 1:
        if counter2 == 0:
            return (0, 0)
        elif counter2 == 1:
            return (500, 800)
        elif counter2 == 2:
            return (800, 1200)
    elif counter == 2:
        if counter2 == 0:
            return (500, 800)
        elif counter2 == 1:
            return (800, 1200)
        elif counter2 == 2:
            return (1200, 1600)
    elif counter == 3:
        if counter2 == 0:
            return (800, 1200)
        elif counter2 == 1:
            return (1200, 1600)
        elif counter2 == 2:
            return (1600, 3000)
    elif counter == 4:
        if counter2 == 0:
            return (1200, 1600)
        elif counter2 == 1:
            return (1600, 3000)
        elif counter2 == 2:
            return (3000, 6000)
    elif counter == 5:
        if counter2 == 0:
            return (1600, 3000)
        elif counter2 == 1:
            return (3000, 6000)
        elif counter2 == 2:
            return (6000, 8000)

    return (0, 0)

async def get_wallet_zero(wallet: str, pro_code: str) -> WalletZero | None:
    page = await get_page_content(wallet, pro_code, Chain.ZERO)
    try:
        rank = int(get_var_declaration_value(page, "value1_fixed"))
        transactions = int(get_var_declaration_value(page, "valuePro2"))
        bridged = float(get_var_declaration_value(page, "valuePro3"))
        source_chains = int(get_var_declaration_value(page, "valuePro4"))
        destination_chains = int(get_var_declaration_value(page, "valuePro5"))
        interacted_contracts = int(get_var_declaration_value(page, "valuePro6"))
        active_days = int(get_var_declaration_value(page, "valuePro7"))
        active_weeks = int(get_var_declaration_value(page, "valuePro8"))
        active_months = int(get_var_declaration_value(page, "valuePro9"))
        potential_earning: tuple[int, int] | None = None
    except AttributeError:
        return None
    
    return WalletZero(
            wallet=wallet,
            rank=rank,
            transactions=transactions,
            bridged=bridged,
            source_chains=source_chains,
            destination_chains=destination_chains,
            interacted_contracts=interacted_contracts,
            active_days=active_days,
            active_weeks=active_weeks,
            active_months=active_months,
            potential_earning=potential_earning
            )

async def get_wallet_linea_mainnet(wallet: str, pro_code: str) -> WalletLinea | None:
    page = await get_page_content(wallet, pro_code, Chain.LINEA)
    try:
        balance_eth = float(get_var_declaration_value(page, "value1_unfixed_mn"))
        if balance_eth == -1: balance_eth = None
        balance_usdc = float(get_var_declaration_value(page, "valuePro1_mn"))
        if balance_usdc == -1: balance_usdc = None
        transactions = float(get_var_declaration_value(page, "valuePro2_mn"))
        is_native_bridge_used = bool(int(get_var_declaration_value(page, "valuePro3_mn")))
        first_tx_date = get_var_declaration_value(page, "valuePro4_mn")
        tx_months = str_array(get_var_declaration_value(page, "valuePro5_mn"))
        active_months = int(get_var_declaration_value(page, "valuePro51_mn"))
        active_weeks = int(get_var_declaration_value(page, "valuePro52_mn"))
        active_days = int(get_var_declaration_value(page, "valuePro53_mn"))
        last_tx_date = get_var_declaration_value(page, "valuePro6_mn")
    except AttributeError:
        return None
    
    return WalletLinea(
            wallet=wallet,
            balance_eth=balance_eth,
            balance_usdc=balance_usdc,
            transactions=transactions,
            is_native_bridge_used=is_native_bridge_used,
            first_tx_date=first_tx_date,
            tx_months=tx_months,
            active_months=active_months,
            active_weeks=active_weeks,
            active_days=active_days,
            last_tx_date=last_tx_date,
            )

async def get_wallet_linea_testnet(wallet: str, pro_code: str) -> WalletLinea | None:
    page = await get_page_content(wallet, pro_code, Chain.LINEA)
    try:
        balance_eth = float(get_var_declaration_value(page, "value1_unfixed"))
        if balance_eth == -1: balance_eth = None
        balance_usdc = float(get_var_declaration_value(page, "valuePro1"))
        if balance_usdc == -1: balance_usdc = None
        transactions = float(get_var_declaration_value(page, "valuePro2"))
        is_native_bridge_used = bool(int(get_var_declaration_value(page, "valuePro3")))
        first_tx_date = get_var_declaration_value(page, "valuePro4")
        tx_months = str_array(get_var_declaration_value(page, "valuePro5"))
        active_months = int(get_var_declaration_value(page, "valuePro51"))
        active_weeks = int(get_var_declaration_value(page, "valuePro52"))
        active_days = int(get_var_declaration_value(page, "valuePro53"))
        last_tx_date = get_var_declaration_value(page, "valuePro6")
    except AttributeError:
        return None
    
    return WalletLinea(
            wallet=wallet,
            balance_eth=balance_eth,
            balance_usdc=balance_usdc,
            transactions=transactions,
            is_native_bridge_used=is_native_bridge_used,
            first_tx_date=first_tx_date,
            tx_months=tx_months,
            active_months=active_months,
            active_weeks=active_weeks,
            active_days=active_days,
            last_tx_date=last_tx_date,
            )


async def get_wallet_starknet(wallet: str, pro_code: str) -> WalletStarknet | None:
    page = await get_page_content(wallet, pro_code, Chain.STARKNET)
    try:
        transactions = int(get_var_declaration_value(page, "value1_fixed"))
        tx_months = str(get_var_declaration_value(page, "valuePro5"))
        active_months = int(get_var_declaration_value(page, "activeMonthsPro1"))
        active_weeks = int(get_var_declaration_value(page, "activeWeeksPro1"))
        active_days = int(get_var_declaration_value(page, "activeDaysPro1"))
        did_swap = bool(int(get_var_declaration_value(page, "did_swap1Bool")))
        did_mint = bool(int(get_var_declaration_value(page, "did_mint1Bool")))
        did_add_liquidity = bool(int(get_var_declaration_value(page, "did_addLiquidity1Bool")))
        did_remove_liquidity = bool(int(get_var_declaration_value(page, "did_removeLiquidity1Bool")))
        total_gas = float(get_var_declaration_value(page, "totalGasfees1unfixed"))
        aggregate_tx = float(get_var_declaration_value(page, "aggregateValueTxPro1unfixed"))
        first_transaction = get_elem_content(page, "valueFirstTx1")
        last_transaction = str(get_var_declaration_value(page, "lastTxPro1"))
    except AttributeError:
        return None

    return WalletStarknet(
            wallet=wallet,
            transactions=transactions,
            tx_months=tx_months,
            active_months=active_months,
            active_weeks=active_weeks,
            active_days=active_days,
            did_swap=did_swap,
            did_mint=did_mint,
            did_add_liquidity=did_add_liquidity,
            did_remove_liquidity=did_remove_liquidity,
            total_gas=total_gas,
            aggregate_tx=aggregate_tx,
            first_transaction=first_transaction,
            last_transaction=last_transaction
            )

async def get_wallet_scroll(wallet: str, pro_code: str) -> WalletScroll | None:
    page = await get_page_content(wallet, pro_code, Chain.SCROLL)
    try:
        balance_eth = float(get_var_declaration_value(page, "value1_fixed"))
        balance_usdc = float(get_var_declaration_value(page, "valuePro1"))
        transactions = int(get_var_declaration_value(page, "valuePro2"))
        is_native_bridge_used = bool(int(get_var_declaration_value(page, "valuePro3")))
        first_tx_date = get_var_declaration_value(page, "valuePro4")
        tx_months = str_array(get_var_declaration_value(page, "valuePro5"))
        last_tx_date = get_var_declaration_value(page, "valuePro6")
    except AttributeError:
        return None
    
    return WalletScroll(
            wallet=wallet,
            balance_eth=balance_eth,
            balance_usdc=balance_usdc,
            transactions=transactions,
            is_native_bridge_used=is_native_bridge_used,
            first_tx_date=first_tx_date,
            tx_months=tx_months,
            last_tx_date=last_tx_date
            )

async def get_wallet_sybil(wallet: str, pro_code: str) -> WalletSybil | None:
    page = await get_page_content(wallet, pro_code, Chain.SYBIL)
    try:
        is_blacklisted = bool(int(get_var_declaration_value(page, "blacklisted12")))
    except AttributeError:
        return None
    
    return WalletSybil(
            wallet=wallet,
            is_blacklisted=is_blacklisted
            )
    
    
    
    
    
    
    
