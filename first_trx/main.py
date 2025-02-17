from web3 import Web3
import inquirer # type: ignore

from client import Client
from tasks.woofi import WooFi
from get_info import GetInfo
from data.config import private_key
from models import Arbitrum, BinanceSmartChain, Base, TokenAmount


client = Client(private_key=private_key, network=Arbitrum)

user_action = GetInfo.get_user_action()

if user_action["action"] == "Swap":
    user_input = GetInfo.get_exchange_details()
    amount = float(user_input["amount"])
    
    if user_input['from_currency'] == 'ETH':
        woofi = WooFi(client=client)
        tx = woofi.swap_eth_to_usdc(amount=TokenAmount(amount=amount))
        res = woofi.client.verif_tx(tx_hash=tx)
        print(res)
    else:
        woofi = WooFi(client=client)
        tx = woofi.swap_usdc_to_eth(amount=amount)
        res = woofi.client.verif_tx(tx_hash=tx)
        print(res)

elif user_action["action"] == "Send":
    user_input = GetInfo.get_transfer_details()
    amount = float(user_input["amount"])
    if user_input['currency'] == 'ETH':
        send_eth = client.send_transaction(to=user_input['recipient'], value=int(TokenAmount(amount)))
        res = client.verif_tx(tx_hash=send_eth)
        print(res)
    else:
        send_usdc = client.send_usdc(to_address=user_input['recipient'], amount=amount)
        res = client.verif_tx(tx_hash=send_usdc)
        print(res)


