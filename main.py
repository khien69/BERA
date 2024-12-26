import asyncio
import json
from aiohttp import ClientSession
from web3 import AsyncWeb3, AsyncHTTPProvider, Web3
import random

rpc = "https://eth.meowrpc.com" # RPC эфира, можете поменять на свой, если очень много счетов и получили бан на запросы

what_gas = 50  # Максимальный газ, при котором будет сделан депозит

value_from = 0.001  # Минимальный депозит в ETH

value_to = 0.0021  # Максимальный депозит в ETH

sleep_from = 10  # Минимальная задержка в секундах между кошелями

sleep_to = 30  # Максимальная задержка в секундах между кошелями

w3_async = AsyncWeb3(AsyncHTTPProvider(rpc))


async def load_abi(filename):
    with open(filename, 'r') as abi_file:
        abi = json.load(abi_file)
    return abi

async def wait_gas():
    while True:
        gas = await w3_async.eth.gas_price
        gas_gwei = w3_async.from_wei(gas, 'gwei')
        print(f"Текущий газ: {gas_gwei} Gwei")
        if gas_gwei <= what_gas:
            break
        print(f"Текущий газ {gas}, ожидаю снижение")
        await asyncio.sleep(20)

# Проверка баланса
async def check_balance(address, max_deposit):
    checksum_address = w3_async.to_checksum_address(address)
    balance = await w3_async.eth.get_balance(checksum_address)
    ether_balance = w3_async.from_wei(balance, 'ether')
    gas_fee = int(await w3_async.eth.gas_price * 1.25 + await w3_async.eth.max_priority_fee)
    if float(ether_balance) < (float(max_deposit) + float(w3_async.from_wei(gas_fee, 'ether'))):
        print(f"Недостаточно средств на кошельке {checksum_address}. Баланс: {ether_balance} ETH")
        return False
    return True

async def deposit(private_key, min_deposit, max_deposit):
    getadres = w3_async.eth.account.from_key(private_key).address
    async with ClientSession() as session:
        url = "https://points.stakestone.io/bera/gWithCode"
        pay_load = {"address": getadres, "refCode": "2CC84"}
        async with session.post(url=url, json=pay_load) as response:
            data = await response.json()

    deposit_value = w3_async.to_wei(random.uniform(value_from, value_to), 'ether') # Расчет объема транзы

    a = await load_abi("abi.json")
    contract = w3_async.eth.contract(address="0x2aCA0C7ED4d5EB4a2116A3bc060A2F264a343357", abi=a)

    tx = await contract.functions.depositETH(getadres).build_transaction({
        'value': deposit_value,  # обьем транзы
        'from': Web3.to_checksum_address(getadres),
        'nonce': await w3_async.eth.get_transaction_count(getadres),
        'maxPriorityFeePerGas': await w3_async.eth.max_priority_fee,
        'maxFeePerGas': int(await w3_async.eth.gas_price * 1.25 + await w3_async.eth.max_priority_fee),
        'chainId': await w3_async.eth.chain_id
    })
    tx['gas'] = int((await w3_async.eth.estimate_gas(tx)) * 1.5)

    # Подписываем транзакцию
    signed_tx = w3_async.eth.account.sign_transaction(tx, private_key)

    # Отправляем транзакцию
    tx_hash = await w3_async.eth.send_raw_transaction(signed_tx.rawTransaction)
    await asyncio.sleep(10)
    print(f"Депозит выполнен. Transaction hash: https://etherscan.io/tx/{tx_hash.hex()}")


async def main():
    # Загрузка приватных ключей
    with open("private_keys.txt", 'r') as f:
        private_keys = [line.strip() for line in f.readlines()]

    await wait_gas()

    for private_key in private_keys:
        try:
            address = w3_async.eth.account.from_key(private_key).address
            print(f"Обрабатываю кошелёк: {address}")

            # Проверяем баланс
            if not await check_balance(address, value_to):
                continue

            # Выполняем депозит
            await deposit(private_key,value_from, value_to)
        except Exception as e:
            print(f"Ошибка при обработке кошелька {address}: {e}")
        finally:
            # Задержка между обработкой ключей
            sleep_time = random.uniform(sleep_from, sleep_to)
            print(f"Задержка {sleep_time:.2f} секунд перед следующим ключом...")
            await asyncio.sleep(sleep_time)

print("Подпишись на автора https://t.me/gaincryptolox")

asyncio.run(main())
