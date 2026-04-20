import os
import json
import time
import random
import sys
from eth_abi import encode
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from colorama import Fore, Style, init
from utils.banner import show_banner

init(autoreset=True)

MY_PROJECT = "BItverse LP"

RPC_URL  = "https://atlantic.dplabs-internal.com"
CHAIN_ID = 688689

FAROSWAP_ROUTER   = Web3.to_checksum_address("0x819829e5cf6e19f9fed92f6b4cc1edf45a2cc4a2")
POSITION_MANAGER  = Web3.to_checksum_address("0x4638a8e4d6df3376c1c6761adef2a49525ffaa89")
PERMIT2           = Web3.to_checksum_address("0xefeaf7db2672b022b3dab3d376f74b6a14bd53a2")

USDT_ADDRESS = Web3.to_checksum_address("0xe7e84b8b4f39c507499c40b4ac199b050e2882d5")
WBTC_ADDRESS = Web3.to_checksum_address("0x0c64f03eea5c30946d5c55b4b532d08ad74638a4")
NATIVE_TOKEN = Web3.to_checksum_address("0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEEE")
WPHAROS      = Web3.to_checksum_address("0x838800b758277cc111b2d48ab01e5e164f8e9471")
ZERO_ADDRESS = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")

POOL_FEE      = 3000
TICK_SPACING  = 1
TICK_LOWER    = -887272
TICK_UPPER    = 887272

USDT_DECIMALS = 6
WBTC_DECIMALS = 8

MAX_UINT128 = 2**128 - 1

ERC721_TRANSFER_TOPIC = Web3.keccak(text="Transfer(address,address,uint256)").hex()

SWAP_PHAROS_ADAPTERS = [
    Web3.to_checksum_address("0x143be32c854e4ddce45ad48dae3343821556d0c3"),
    Web3.to_checksum_address("0x143be32c854e4ddce45ad48dae3343821556d0c3"),
]
SWAP_PHAROS_PAIRS = [
    Web3.to_checksum_address("0x237ebfeb8880d4820129dc61f032c0b82107b1da"),
    Web3.to_checksum_address("0x02bbc3179339cfdbcd481de2be87921c9f325a43"),
]
SWAP_PHAROS_ASSET_TO = [
    Web3.to_checksum_address("0x237ebfeb8880d4820129dc61f032c0b82107b1da"),
    Web3.to_checksum_address("0x02bbc3179339cfdbcd481de2be87921c9f325a43"),
    Web3.to_checksum_address("0x819829e5cf6e19f9fed92f6b4cc1edf45a2cc4a2"),
]
SWAP_PHAROS_DIRECTION  = 2
SWAP_PHAROS_MORE_INFOS = [bytes(0), bytes(0)]

SWAP_WBTC_ADAPTERS = [
    Web3.to_checksum_address("0x4f8c8e05e946de09d768d062c5e969d1c8920c72"),
    Web3.to_checksum_address("0x143be32c854e4ddce45ad48dae3343821556d0c3"),
    Web3.to_checksum_address("0x143be32c854e4ddce45ad48dae3343821556d0c3"),
]
SWAP_WBTC_PAIRS = [
    Web3.to_checksum_address("0xb3886ee7bcbc24b6060a048fafed9f54ff9d9328"),
    Web3.to_checksum_address("0x02bbc3179339cfdbcd481de2be87921c9f325a43"),
    Web3.to_checksum_address("0x219bddcec70d474f974e8c3fa87d715c7a665015"),
]
SWAP_WBTC_ASSET_TO = [
    Web3.to_checksum_address("0xb3886ee7bcbc24b6060a048fafed9f54ff9d9328"),
    Web3.to_checksum_address("0x02bbc3179339cfdbcd481de2be87921c9f325a43"),
    Web3.to_checksum_address("0x219bddcec70d474f974e8c3fa87d715c7a665015"),
    Web3.to_checksum_address("0x819829e5cf6e19f9fed92f6b4cc1edf45a2cc4a2"),
]
SWAP_WBTC_MORE_INFOS = [
    bytes.fromhex("000000000000000000000000000000000000000000000000000000000000001e0000000000000000000000000000000000000000000000000000000000002710"),
    bytes(0),
    bytes(0),
]

FEE_DATA = bytes.fromhex("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")

ERC20_ABI = [
    {"name": "balanceOf",  "type": "function", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "approve",    "type": "function", "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable"},
    {"name": "allowance",  "type": "function", "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
]

ERC721_ABI = [
    {"name": "balanceOf",           "type": "function", "inputs": [{"name": "owner", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "tokenOfOwnerByIndex", "type": "function", "inputs": [{"name": "owner", "type": "address"}, {"name": "index", "type": "uint256"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
]

PERMIT2_ABI = [
    {
        "name": "approve",
        "type": "function",
        "inputs": [
            {"name": "token",   "type": "address"},
            {"name": "spender", "type": "address"},
            {"name": "amount",  "type": "uint160"},
            {"name": "expiration", "type": "uint48"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "name": "allowance",
        "type": "function",
        "inputs": [
            {"name": "user", "type": "address"},
            {"name": "token", "type": "address"},
            {"name": "spender", "type": "address"}
        ],
        "outputs": [
            {"name": "amount", "type": "uint160"},
            {"name": "expiration", "type": "uint48"},
            {"name": "nonce", "type": "uint48"}
        ],
        "stateMutability": "view"
    }
]

ROUTER_ABI = [
    {
        "name": "mixSwap",
        "type": "function",
        "inputs": [
            {"name": "fromToken",       "type": "address"},
            {"name": "toToken",         "type": "address"},
            {"name": "fromTokenAmount", "type": "uint256"},
            {"name": "expReturnAmount", "type": "uint256"},
            {"name": "minReturnAmount", "type": "uint256"},
            {"name": "mixAdapters",     "type": "address[]"},
            {"name": "mixPairs",        "type": "address[]"},
            {"name": "assetTo",         "type": "address[]"},
            {"name": "directions",      "type": "uint256"},
            {"name": "moreInfos",       "type": "bytes[]"},
            {"name": "feeData",         "type": "bytes"},
            {"name": "deadLine",        "type": "uint256"},
        ],
        "outputs": [{"name": "returnAmount", "type": "uint256"}],
        "stateMutability": "payable",
    }
]

MULTICALL_ABI = [
    {
        "name": "multicall",
        "type": "function",
        "inputs": [{"name": "data", "type": "bytes[]"}],
        "outputs": [{"name": "results", "type": "bytes[]"}],
        "stateMutability": "payable",
    }
]

PAIR_ABI = [
    {
        "name": "getReserves",
        "type": "function",
        "inputs": [],
        "outputs": [
            {"name": "reserve0", "type": "uint112"},
            {"name": "reserve1", "type": "uint112"},
            {"name": "blockTimestampLast", "type": "uint32"},
        ],
        "stateMutability": "view",
    },
    {
        "name": "token0",
        "type": "function",
        "inputs": [],
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
    },
]

G   = Fore.GREEN  + Style.BRIGHT
R   = Fore.RED    + Style.BRIGHT
Y   = Fore.YELLOW + Style.BRIGHT
RST = Style.RESET_ALL

MIN_PHAROS_FOR_FEE = Web3.to_wei(0.0005, "ether")

def log_info(msg):
    print(f"{G}{msg}{RST}")

def log_success(msg):
    print(f"{G}{msg}{RST}")

def log_warn(msg):
    print(f"{Y}{msg}{RST}")

def log_error(msg):
    print(f"{R}{msg}{RST}")

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def load_private_keys():
    load_dotenv()
    keys = []
    i = 1
    while True:
        val = os.getenv(f"PRIVATEKEY_{i}")
        if not val:
            break
        keys.append(val.strip())
        i += 1
    return keys

def connect_web3():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        log_error("Failed to Connect to RPC Endpoint Exiting")
        sys.exit(1)
    return w3

def build_gas(w3, tx):
    try:
        latest = w3.eth.get_block("latest")
        if hasattr(latest, "baseFeePerGas") and latest.baseFeePerGas is not None:
            base_fee = latest.baseFeePerGas
            priority = w3.to_wei(1, "gwei")
            tx["maxFeePerGas"] = base_fee + priority
            tx["maxPriorityFeePerGas"] = priority
        else:
            tx["gasPrice"] = w3.eth.gas_price
    except Exception:
        tx["gasPrice"] = w3.eth.gas_price
    return tx

def build_and_send(w3, tx, private_key, label):
    account = Account.from_key(private_key)
    tx["nonce"]   = w3.eth.get_transaction_count(account.address)
    tx["chainId"] = CHAIN_ID
    tx = build_gas(w3, tx)
    tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.1)
    signed  = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    log_info(f"Transaction Submitted {label}")
    log_info(f"Transaction Hash {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    if receipt.status == 1:
        log_success(f"Transaction Confirmed {label} Block {receipt.blockNumber}")
    else:
        log_error(f"Transaction Reverted {label}")
    return receipt

def ensure_approval(w3, private_key, token_address, spender, amount, label):
    account = Account.from_key(private_key)
    token = w3.eth.contract(address=token_address, abi=ERC20_ABI)
    allowance = token.functions.allowance(account.address, spender).call()
    if allowance < amount:
        log_warn(f"Approving {label} for Spender")
        tx = token.functions.approve(spender, 2**256 - 1).build_transaction({
            "from": account.address,
        })
        build_and_send(w3, tx, private_key, f"Approve {label}")

def ensure_permit2_approval(w3, private_key, token_address, label):
    account = Account.from_key(private_key)
    token = w3.eth.contract(address=token_address, abi=ERC20_ABI)
    allowance = token.functions.allowance(account.address, PERMIT2).call()
    if allowance < 2**200:
        log_warn(f"Approving {label} to Permit2")
        tx = token.functions.approve(PERMIT2, 2**256 - 1).build_transaction({
            "from": account.address,
        })
        build_and_send(w3, tx, private_key, f"Approve {label} to Permit2")
    permit2 = w3.eth.contract(address=PERMIT2, abi=PERMIT2_ABI)
    p2_allowance, _, _ = permit2.functions.allowance(account.address, token_address, POSITION_MANAGER).call()
    if p2_allowance < 2**150:
        MAX_UINT160 = 2**160 - 1
        MAX_UINT48  = 2**48 - 1
        log_warn(f"Setting Permit2 Allowance {label} for Position Manager")
        tx = permit2.functions.approve(token_address, POSITION_MANAGER, MAX_UINT160, MAX_UINT48).build_transaction({
            "from": account.address,
        })
        build_and_send(w3, tx, private_key, f"Permit2 Approve {label}")

def get_amount_out_amm(amount_in, reserve_in, reserve_out):
    amount_in_fee = amount_in * 997
    return (amount_in_fee * reserve_out) // (reserve_in * 1000 + amount_in_fee)

def get_usdt_out_estimate(w3, pharos_wei):
    pair = w3.eth.contract(address=SWAP_PHAROS_PAIRS[0], abi=PAIR_ABI)
    token0   = pair.functions.token0().call()
    reserves = pair.functions.getReserves().call()
    if token0.lower() == WPHAROS.lower():
        return get_amount_out_amm(pharos_wei, reserves[0], reserves[1])
    return get_amount_out_amm(pharos_wei, reserves[1], reserves[0])

def get_wbtc_out_estimate(w3, pharos_wei):
    pair = w3.eth.contract(address=SWAP_WBTC_PAIRS[0], abi=PAIR_ABI)
    token0   = pair.functions.token0().call()
    reserves = pair.functions.getReserves().call()
    if token0.lower() == WPHAROS.lower():
        return get_amount_out_amm(pharos_wei, reserves[0], reserves[1])
    return get_amount_out_amm(pharos_wei, reserves[1], reserves[0])

def swap_pharos_to_usdt(w3, private_key, pharos_amount_eth, config):
    account = Account.from_key(private_key)
    router  = w3.eth.contract(address=FAROSWAP_ROUTER, abi=ROUTER_ABI)
    amount_wei = w3.to_wei(pharos_amount_eth, "ether")
    deadline   = int(time.time()) + 600
    try:
        exp = get_usdt_out_estimate(w3, amount_wei)
    except Exception:
        exp = 1
    min_ret = max(1, int(exp * 0.90))
    log_warn(f"Swap PHAROS to USDT Amount {pharos_amount_eth} PHAROS Expected {exp} Min {min_ret}")
    tx = router.functions.mixSwap(
        NATIVE_TOKEN, USDT_ADDRESS, amount_wei,
        exp, min_ret,
        SWAP_PHAROS_ADAPTERS, SWAP_PHAROS_PAIRS, SWAP_PHAROS_ASSET_TO,
        SWAP_PHAROS_DIRECTION, SWAP_PHAROS_MORE_INFOS, FEE_DATA, deadline,
    ).build_transaction({
        "from":  account.address,
        "value": amount_wei,
    })
    build_and_send(w3, tx, private_key, "Swap PHAROS to USDT")

def swap_pharos_to_wbtc(w3, private_key, pharos_amount_eth, config):
    account = Account.from_key(private_key)
    router  = w3.eth.contract(address=FAROSWAP_ROUTER, abi=ROUTER_ABI)
    amount_wei = w3.to_wei(pharos_amount_eth, "ether")
    deadline   = int(time.time()) + 600
    try:
        exp = get_wbtc_out_estimate(w3, amount_wei)
    except Exception:
        exp = 1
    min_ret = max(1, int(exp * 0.90))
    log_warn(f"Swap PHAROS to WBTC Amount {pharos_amount_eth} PHAROS Expected {exp} Min {min_ret}")
    tx = router.functions.mixSwap(
        NATIVE_TOKEN, WBTC_ADDRESS, amount_wei,
        exp, min_ret,
        SWAP_WBTC_ADAPTERS, SWAP_WBTC_PAIRS, SWAP_WBTC_ASSET_TO,
        0, SWAP_WBTC_MORE_INFOS, FEE_DATA, deadline,
    ).build_transaction({
        "from":  account.address,
        "value": amount_wei,
    })
    build_and_send(w3, tx, private_key, "Swap PHAROS to WBTC")

def get_token_id_from_receipt(receipt, user_address):
    for log in receipt.logs:
        try:
            if log.address.lower() != POSITION_MANAGER.lower():
                continue
            if len(log.topics) < 4:
                continue
            topic0 = log.topics[0].hex() if isinstance(log.topics[0], bytes) else log.topics[0]
            if not topic0.startswith("0x"):
                topic0 = "0x" + topic0
            if topic0.lower() != ERC721_TRANSFER_TOPIC.lower():
                continue
            to_raw  = log.topics[2] if isinstance(log.topics[2], bytes) else bytes.fromhex(log.topics[2][2:])
            to_addr = "0x" + to_raw.hex()[-40:]
            if to_addr.lower() != user_address.lower():
                continue
            token_id_raw = log.topics[3] if isinstance(log.topics[3], bytes) else bytes.fromhex(log.topics[3][2:])
            return int(token_id_raw.hex(), 16)
        except Exception:
            continue
    return None

def get_user_token_id(w3, user_address):
    pm = w3.eth.contract(address=POSITION_MANAGER, abi=ERC721_ABI)
    try:
        balance = pm.functions.balanceOf(user_address).call()
        if balance == 0:
            return None
        return pm.functions.tokenOfOwnerByIndex(user_address, 0).call()
    except Exception:
        return None

def build_increase_liquidity_calldata(token_id, liquidity, deadline):
    SELECTOR = bytes.fromhex("dd46508f")
    actions = bytes.fromhex("000d")
    params_item1 = encode(
        ["uint256", "uint256", "uint128", "uint128", "bytes"],
        [token_id, liquidity, MAX_UINT128, MAX_UINT128, b'']
    )
    params_item2 = encode(
        ["address", "address"],
        [WBTC_ADDRESS, USDT_ADDRESS]
    )
    unlock_data = encode(
        ["bytes", "bytes[]"],
        [actions, [params_item1, params_item2]]
    )
    return SELECTOR + encode(["bytes", "uint256"], [unlock_data, deadline])

def build_mint_position_calldata(liquidity, deadline, recipient):
    SELECTOR = bytes.fromhex("dd46508f")
    actions = bytes.fromhex("020d")
    params_item1 = encode(
        [
            "address", "address", "uint24", "int24", "address",
            "int24", "int24", "uint256",
            "uint128", "uint128",
            "address",
            "bytes"
        ],
        [
            WBTC_ADDRESS, USDT_ADDRESS, POOL_FEE, TICK_SPACING, ZERO_ADDRESS,
            TICK_LOWER, TICK_UPPER, liquidity,
            MAX_UINT128, MAX_UINT128,
            recipient,
            b'']
    )
    params_item2 = encode(
        ["address", "address"],
        [WBTC_ADDRESS, USDT_ADDRESS]
    )
    unlock_data = encode(
        ["bytes", "bytes[]"],
        [actions, [params_item1, params_item2]]
    )
    return SELECTOR + encode(["bytes", "uint256"], [unlock_data, deadline])

def add_lp(w3, private_key, usdt_amount_raw, wbtc_amount_raw, round_num, total_rounds, cached_token_id=None):
    account  = Account.from_key(private_key)
    deadline = int(time.time()) + 600
    ensure_permit2_approval(w3, private_key, WBTC_ADDRESS, "WBTC")
    ensure_permit2_approval(w3, private_key, USDT_ADDRESS, "USDT")
    log_warn(f"Round {round_num}/{total_rounds} Add LP USDT {usdt_amount_raw} WBTC {wbtc_amount_raw} (raw units)")
    token_id = cached_token_id
    if token_id is None:
        token_id = get_user_token_id(w3, account.address)
    new_token_id = cached_token_id
    if token_id is not None:
        log_info(f"Round {round_num}/{total_rounds} Found Existing Position TokenId {token_id} Using Increase Liquidity")
        inner_calldata = build_increase_liquidity_calldata(token_id, usdt_amount_raw, deadline)
        pm = w3.eth.contract(address=POSITION_MANAGER, abi=MULTICALL_ABI)
        tx = pm.functions.multicall([inner_calldata]).build_transaction({
            "from":  account.address,
            "value": 0,
        })
        build_and_send(w3, tx, private_key, f"Add LP USDT/WBTC Round {round_num}")
        new_token_id = token_id
    else:
        log_warn(f"Round {round_num}/{total_rounds} No Existing Position Found Minting New Position")
        inner_calldata = build_mint_position_calldata(usdt_amount_raw, deadline, account.address)
        pm = w3.eth.contract(address=POSITION_MANAGER, abi=MULTICALL_ABI)
        tx = pm.functions.multicall([inner_calldata]).build_transaction({
            "from":  account.address,
            "value": 0,
        })
        receipt = build_and_send(w3, tx, private_key, f"Add LP USDT/WBTC Round {round_num}")
        if receipt.status == 1:
            minted_id = get_token_id_from_receipt(receipt, account.address)
            if minted_id is not None:
                log_info(f"Round {round_num}/{total_rounds} Minted New Position TokenId {minted_id}")
                new_token_id = minted_id
            else:
                new_token_id = get_user_token_id(w3, account.address)
    return new_token_id

def ensure_tokens(w3, private_key, config, account):
    usdt = w3.eth.contract(address=USDT_ADDRESS, abi=ERC20_ABI)
    wbtc = w3.eth.contract(address=WBTC_ADDRESS, abi=ERC20_ABI)
    usdt_bal = usdt.functions.balanceOf(account.address).call()
    wbtc_bal = wbtc.functions.balanceOf(account.address).call()
    if usdt_bal == 0:
        pharos_swap = config["swap_pharos_to_usdt_amount"]
        log_warn(f"USDT Balance is Zero Swapping {pharos_swap} PHAROS to USDT")
        swap_pharos_to_usdt(w3, private_key, pharos_swap, config)
        usdt_bal = usdt.functions.balanceOf(account.address).call()
    if wbtc_bal == 0:
        pharos_swap_wbtc = config["swap_pharos_to_wbtc_amount"]
        log_warn(f"WBTC Balance is Zero Swapping {pharos_swap_wbtc} PHAROS to WBTC")
        swap_pharos_to_wbtc(w3, private_key, pharos_swap_wbtc, config)
        wbtc_bal = wbtc.functions.balanceOf(account.address).call()
    return usdt_bal, wbtc_bal

def run_account_cycles(w3, private_key, config):
    account = Account.from_key(private_key)
    usdt = w3.eth.contract(address=USDT_ADDRESS, abi=ERC20_ABI)
    wbtc = w3.eth.contract(address=WBTC_ADDRESS, abi=ERC20_ABI)
    pharos_bal = w3.eth.get_balance(account.address)
    usdt_bal   = usdt.functions.balanceOf(account.address).call()
    wbtc_bal   = wbtc.functions.balanceOf(account.address).call()
    log_info(f"Balance PHAROS {w3.from_wei(pharos_bal, 'ether'):.6f} USDT {usdt_bal / 10**USDT_DECIMALS:.6f} WBTC {wbtc_bal / 10**WBTC_DECIMALS:.8f}")
    cfg = config["lp"]
    total_rounds = random.randint(cfg["count_min"], cfg["count_max"])
    log_info(f"Total LP Rounds {total_rounds}")
    cached_token_id = None
    for i in range(1, total_rounds + 1):
        pharos_now = w3.eth.get_balance(account.address)
        if pharos_now < MIN_PHAROS_FOR_FEE:
            log_error(f"Round {i}/{total_rounds} Insufficient PHAROS for Gas Stopping Account")
            break
        usdt_amount_float = random.uniform(cfg["usdt_amount_min"], cfg["usdt_amount_max"])
        usdt_amount_raw   = int(usdt_amount_float * 10**USDT_DECIMALS)
        usdt_bal = usdt.functions.balanceOf(account.address).call()
        wbtc_bal = wbtc.functions.balanceOf(account.address).call()
        min_wbtc_needed = 100
        if usdt_bal < usdt_amount_raw or wbtc_bal < min_wbtc_needed:
            log_warn(f"Round {i}/{total_rounds} Insufficient Token Balance USDT {usdt_bal} needed {usdt_amount_raw} WBTC {wbtc_bal} Restocking")
            try:
                if usdt_bal < usdt_amount_raw:
                    swap_pharos_to_usdt(w3, private_key, config["swap_pharos_to_usdt_amount"], config)
                    usdt_bal = usdt.functions.balanceOf(account.address).call()
                if wbtc_bal < min_wbtc_needed:
                    swap_pharos_to_wbtc(w3, private_key, config["swap_pharos_to_wbtc_amount"], config)
                    wbtc_bal = wbtc.functions.balanceOf(account.address).call()
            except Exception as e:
                err = str(e)
                log_error(f"Round {i}/{total_rounds} Restock Failed {err}")
                ph = w3.eth.get_balance(account.address)
                if ph < MIN_PHAROS_FOR_FEE or "-32600" in err or "INSUFFICIENT_BALANCE" in err:
                    log_error(f"Round {i}/{total_rounds} Cannot Restock Stopping Account")
                    break
                log_warn(f"Round {i}/{total_rounds} Skipping Round")
                continue
            usdt_bal = usdt.functions.balanceOf(account.address).call()
            wbtc_bal = wbtc.functions.balanceOf(account.address).call()
            if usdt_bal < usdt_amount_raw or wbtc_bal < min_wbtc_needed:
                log_warn(f"Round {i}/{total_rounds} Still Insufficient After Restock Skipping Round")
                continue
        try:
            cached_token_id = add_lp(w3, private_key, usdt_amount_raw, wbtc_bal, i, total_rounds, cached_token_id=cached_token_id)
        except Exception as e:
            err = str(e)
            log_error(f"Round {i}/{total_rounds} Add LP Failed {err}")
            ph = w3.eth.get_balance(account.address)
            if ph < MIN_PHAROS_FOR_FEE or "-32600" in err or "INSUFFICIENT_BALANCE" in err:
                log_error(f"Round {i}/{total_rounds} Stopping Account")
                break
            log_warn(f"Round {i}/{total_rounds} Skipping Round")
            continue

def countdown_sleep(seconds):
    log_warn(f"All Accounts Completed Entering Sleep Mode Duration {seconds} seconds")
    end_time = time.time() + seconds
    try:
        while True:
            remaining = int(end_time - time.time())
            if remaining <= 0:
                break
            h = remaining // 3600
            m = (remaining % 3600) // 60
            s = remaining % 60
            print(f"\r{Y}Next Cycle In {h:02d}:{m:02d}:{s:02d}{RST}", end="", flush=True)
            time.sleep(1)
        print()
    except KeyboardInterrupt:
        print()
        log_error("Script Stopped by User")
        raise

def process_account(w3, index, private_key, config):
    account = Account.from_key(private_key)
    log_warn(f"Processing Account {index} Address {account.address}")
    try:
        usdt_bal, wbtc_bal = ensure_tokens(w3, private_key, config, account)
        run_account_cycles(w3, private_key, config)
        log_success(f"Account {index} Completed Successfully Address {account.address}")
    except Exception as e:
        log_error(f"Account {index} Encountered an Error {str(e)}")

def main():
    show_banner(MY_PROJECT)
    config = load_config()
    private_keys = load_private_keys()
    w3 = connect_web3()
    if not private_keys:
        log_error("No Private Keys Found in .env Exiting")
        sys.exit(1)
    log_info(f"Loaded {len(private_keys)} Private Keys")
    while True:
        for i, private_key in enumerate(private_keys):
            process_account(w3, i + 1, private_key, config)
            print()
        sleep_duration = random.randint(config["sleep_min"], config["sleep_max"])
        countdown_sleep(sleep_duration)
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_error("Script Stopped by User")

