from web3 import Web3
from typing import Optional
import requests

from models import TokenAmount
from utils import read_json
from models import Network

from data.config import TOKEN_ABI 

class Client:
    default_abi = read_json(TOKEN_ABI)

    def __init__(
            self,
            private_key: str, 
            network: Network
    ):
        self.private_key = private_key
        self.network = network
        self.w3 = Web3(Web3.HTTPProvider(endpoint_uri=self.network.rpc))
        self.address = Web3.to_checksum_address(self.w3.eth.account.from_key(private_key=private_key).address)
    
    def get_decimals(self, contract_address: str) -> int:
        return int(self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=Client.default_abi
        ).functions.decimals().call())
    
    def balance_of(self, contract_address: str, address: Optional[str] = None) -> TokenAmount:
        if not address:
            address = self.address
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=Client.default_abi)
        return TokenAmount(
            amount=contract.functions.balanceOf(address).call(),
            decimals=self.get_decimals(contract_address=contract_address),
            wei=True,
        )
    
    def get_allowance(self, token_address: str, spender: str) -> TokenAmount:
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=Client.default_abi)
        return TokenAmount(
            amount=contract.functions.allowance(self.address, spender).call(),
            decimals=self.get_decimals(contract_address=token_address),
            wei=True
        )

    def check_balance_interface(self, token_address, min_value) -> bool:
        print(f'{self.address} | balanceOf | check balance of {token_address}')
        balance = self.balance_of(contract_address=token_address)
        decimal = self.get_decimals(contract_address=token_address)
        #print(f"Balance (raw): {balance.value}")
        #print(f"Decimals: {decimal}")
        #print(f"Min required (raw): {min_value * 10 ** decimal}")
        if balance.value < min_value * 10 ** decimal:
            print(f'{self.address} | balanceOf | not enough {token_address}')
            return False
        return True
    
    # @staticmethod
    # async def get_max_priority_fee_per_gas(w3: Web3, block: dict) -> int:
    #     block_number = block['number']
    #     latest_block_transactions_count = w3.eth.get_block_transaction_count(block_number)
    #     max_priority_fee_per_gas_lst = []
    #     for i in range(latest_block_transactions_count):
    #         try:
    #             transaction = w3.eth.get_transaction_by_block(block_number, i)
    #             if 'maxPriorityFeePerGas' in transaction:
    #                 max_priority_fee_per_gas_lst.append(transaction['maxPriorityFeePerGas'])
    #         except Exception:
    #             continue

    #     if not max_priority_fee_per_gas_lst:
    #         max_priority_fee_per_gas = w3.eth.max_priority_fee
    #     else: 
    #         max_priority_fee_per_gas_lst.sort()
    #         max_priority_fee_per_gas = max_priority_fee_per_gas_lst[len(max_priority_fee_per_gas_lst) // 2]
    #     return max_priority_fee_per_gas

    def send_usdc(self, to_address: str, amount):
        to = Web3.to_checksum_address(to_address)
        usdc_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address('0xaf88d065e77c8cC2239327C5EDb3A432268e5831'),
            abi=self.default_abi,
        )
        amount=TokenAmount(amount=amount,decimals=6,wei=False)
        data = usdc_contract.encode_abi('transfer', args=(
            to,
            amount.Wei,
        )
        )
        return self.send_transaction(to=usdc_contract.address, data=data, value=None)
    
    def send_transaction(
            self,
            to,
            data=None,     
            from_=None,
            increase_gas=1.2,
            value=None,
            max_priority_fee_per_gas: Optional[int] = None,
            max_fee_per_gas: Optional[int] = None,
    ):
        if not from_:
            from_ = self.address

        tx_params = {
            'chainId': self.w3.eth.chain_id,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'from': Web3.to_checksum_address(from_),
            'to': Web3.to_checksum_address(to),
            'gasPrice': self.w3.eth.gas_price
        }
        if data:
            tx_params['data'] = data

        if value:
            tx_params['value'] = value #если велью существует и не ровняется none (как например в апрувах) то добавляем в тх_парамс велью
        
        #print("Параметры транзакции перед отправкой:", tx_params)

        try: 
            tx_params['gas'] = int(self.w3.eth.estimate_gas(tx_params) * increase_gas) #естимейт расчитывает исходя из тхпарамс скока газа нужно
        except Exception as err:
            print(f'{self.address} | Transaction failed (GAS ERROR) | {err}')
            return None
        try:
            sign = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
            print(f'{self.address} | Транзакция подписана, отправляем...')
            return self.w3.eth.send_raw_transaction(sign.raw_transaction) #отправка транзы возвращает хэш
        except Exception as err:
            print(f'{self.address} | Ошибка при отправке транзакции: {err}')
            return None
        
    def verif_tx(self,tx_hash) -> bool:
        try:
            data = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=200)
            if 'status' in data and data['status'] == 1:
                print(f'{self.address} | transaction was successful: {tx_hash.hex()}')
                return True
            else:
                print(f'{self.address} | transaction failed: {tx_hash.hex()}')
                return False
        except Exception as err:
            print(f'{self.address} | unexpected error in <verif_tx> function: {err}')
            return False
        
    def approve(self, token_address, spender, amount: Optional[TokenAmount] = None):
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=Client.default_abi
        )
        return self.send_transaction(
            to=token_address,
            data=contract.encode_abi('approve',
                                    args=(
                                        spender,
                                        amount.Wei
                                    ))

        )

    def approve_interface(self, token_address: str, spender: str, amount: Optional[TokenAmount] = None) -> bool:
        print(f'{self.address} | approve | start approve {token_address} for spender {spender}')
        decimals = self.get_decimals(contract_address=token_address)
        
        raw_balance = self.balance_of(contract_address=token_address)
        if isinstance(raw_balance, TokenAmount):
            balance = raw_balance
        else:
            balance = TokenAmount(
                amount=self.balance_of(contract_address=token_address),
                decimals=decimals,
                wei=True
            )
        
        if balance.Wei <= 0:
            print(f'{self.address} | approve | zero balance')
            return False
        
        amount = TokenAmount(amount=amount, decimals=self.get_decimals(contract_address=token_address), wei=False)
        # print(amount) отладка
        if not amount or amount.Wei > balance.Wei:
            amount = balance

        raw_allowance = self.get_allowance(token_address=token_address, spender=spender)

        if isinstance(raw_allowance, TokenAmount):
            approved = raw_allowance
        else:
            approved = TokenAmount(
                amount=self.get_allowance(token_address=token_address, spender=spender),
                decimals=decimals,
                wei=True
            )
        
        if amount.Wei <= approved.Wei:
            print(f'{self.address} | approve | already approved')
            return True
        
        tx_hash = self.approve(token_address=token_address, spender=spender, amount=amount)
        if not self.verif_tx(tx_hash=tx_hash):
            print(f'{self.address} | approve | {token_address} for spender {spender}')
            return False
        return True
    
    def get_eth_price(self, token='ETH'):
        token = token.upper()
        print(f'{self.address} | getting {token} price')
        response = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={token}USDT')
        if response.status_code != 200:
            print(f'code: {response.status_code} | json: {response.json()}')
            return None
        result_dict = response.json()
        return float(result_dict['price'])
    

