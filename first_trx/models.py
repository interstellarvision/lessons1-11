from dataclasses import dataclass
from decimal import Decimal
from typing import Union


class TokenAmount:
    Wei: int
    Ether: Decimal
    decimals: int

    def __init__(self, amount: Union[int, float, str, Decimal], decimals: int = 18, wei: bool = False) -> None:
        if wei:
            self.Wei: int = amount
            self.Ether: Decimal = Decimal(str(amount)) / 10 ** decimals

        else:
            self.Wei: int = int(Decimal(str(amount)) * 10 ** decimals)
            self.Ether: Decimal = Decimal(str(amount))

        self.decimals = decimals

    def __int__(self):
        return self.Wei

    @property
    def value(self) -> int:
        return self.Wei  # Возвращаем целочисленный баланс в Wei


class Network:
    def __init__(self,
                 name: str,
                 rpc: str,
                 chain_id: int,
                 eip1559_tx: bool,
                 coin_symbol: str,
                 explorer: str,
                 decimals: int = 18,
    ):
        self.name = name
        self.rpc = rpc
        self.chain_id = chain_id
        self.eip1559_tx = eip1559_tx
        self.coin_symbol = coin_symbol
        self.decimals = decimals
        self.explorer = explorer

    def __str__(self):
        return f'{self.name}'

BinanceSmartChain = Network(
    name='bsc',
    rpc='https://binance.llamarpc.com',
    chain_id=56,
    eip1559_tx=False,
    coin_symbol='BNB',
    explorer='https://bscscan.com/'
)


Base = Network(
    name='base',
    rpc='https://base.llamarpc.com',
    chain_id=8453,
    eip1559_tx=True,
    coin_symbol='ETH',
    explorer='https://basescan.org/',
)


Arbitrum = Network(
    name='arbitrum',
    rpc='https://arb1.lava.build',
    chain_id=42161,
    eip1559_tx=True,
    coin_symbol='ETH',
    explorer='https://arbiscan.io/',
)
