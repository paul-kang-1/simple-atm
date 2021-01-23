import datetime
from typing import Mapping


class Account:
    def __init__(self, holder: str, acc_type: str, card_num: int, balance=0) -> None:
        self.holder = holder
        self.acc_type = acc_type
        self.card_num = card_num
        self.balance = balance
        self.active = True
        self.transactions = {}

    def format_transactions(self) -> str:
        pass


class Bank:
    ACC_TYPES = ["savings", "checking"]
    ACC_COUNT = 0

    def __init__(self, name: str) -> None:
        self.name = name
        self.accounts = {}

    def create_account(
        self, holder: str, acc_type: str, pin: int, balance: int
    ) -> None:
        acc = Account(holder, acc_type, balance)
        card_num = self.genereate_card_num()
        self.accounts[(card_num, pin)] = acc
        Bank.ACC_COUNT += 1

    def validate(self, card_num: int, pin: int) -> Account:
        return (card_num, pin) in self.accounts

    def transaction(self, sender: Account, recepient: Account, amt: int) -> None:
        pass

    def genereate_card_num(self) -> int:
        str_num = str() + str(Bank.ACC_COUNT)
        return str.zfill(str_num)


class Controller:
    THRESHOLD = 3

    def __init__(self, bank: Bank, init_cash: int) -> None:
        self.bank = bank
        self.cash_bin = init_cash
        self.current_user: Account = None
        self.wrong_count = 0

    def validate(self, card_num: int, pin: int) -> Account:
        return self.bank.validate(card_num, pin)

    def initiate(self, card_num, pin) -> tuple(int, str):
        if self.validate(card_num, pin):
            pass

    def check_balance(self):
        if self.current_user:
            return self.current_user.balance

    def deposit(self, amt):
        pass

    def withdraw(self, amt):
        pass

    def transaction(self, recepient, amt):
        pass

    def deactivate(self) -> None:
        if self.current_user:
            self.current_user.active = False

    def end(self) -> tuple(int, str):
        self.current_user = None
        self.wrong_count = 0
