import datetime
from enum import Enum
from typing import Mapping, Tuple


class Bank:
    ACC_TYPES = ["savings", "checking"]

    def __init__(self, name: str) -> None:
        self.name = name
        self.accounts = {}

    def create_account(
        self, holder: str, acc_type: str, pin: int, balance: int
    ) -> None:
        acc = Account(holder, acc_type, pin, balance)
        card_num = self.genereate_card_num()
        self.accounts[card_num] = acc

    def validate(self, credentials: Mapping[str, int]) -> bool:
        pass

    def transaction(self, sender: Account, recepient: Account, amt: int) -> None:
        pass

    def genereate_card_num(self) -> int:
        return 0


class Account:
    def __init__(
        self, holder: str, acc_type: str, acc_num: int, pin: int, balance=0
    ) -> None:
        self.holder = holder
        self.acc_type = acc_type
        self.acc_num = acc_num
        self.balance = balance
        self.active = True
        self.transactions = {}

    def format_transactions(self) -> str:
        pass


class Controller:
    THRESHOLD = 3

    def __init__(self, bank: Bank, init_cash: int) -> None:
        self.bank = bank
        self.cash_bin = init_cash
        self.current_user = None
        self.wrong_dount = 0

    def validate(self, credentials: Mapping[str, int]) -> bool:
        pass

    def check_balance(self):
        pass

    def deposit(self, amt):
        pass

    def withdraw(self, amt):
        pass

    def transaction(self, recepient, amt):
        pass

    def deactivate(self) -> None:
        pass

    def end(self) -> tuple(int, str):
        pass
