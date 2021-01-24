from datetime import datetime
from typing import Mapping, Union, Tuple


class UnidentifiedUser(ValueError):
    pass


class IncorrectPIN(ValueError):
    pass


class SuspendedUser(Exception):
    pass


class Account:
    TRANSACTION_TYPES = ["withdraw", "deposit", "send", "receive"]

    def __init__(self, holder: str, pin: int, balance=0) -> None:
        self.holder = holder
        self.pin = pin
        self.balance = balance
        self.active = True
        self.transactions = {}

    @staticmethod
    def check_amt(amt: int) -> None:
        if amt <= 0:
            raise ValueError("Amount should be a positive integer.")

    def deposit(self, amt: int, sender_name: str = None) -> None:
        Account.check_amt(amt)
        self.balance += amt
        record = {}
        if not sender_name:
            record["type"] = Account.TRANSACTION_TYPES[1]
        else:
            record["type"] = Account.TRANSACTION_TYPES[3]
            record["sender"] = sender_name
        record["amount"] = amt
        record["balance"] = self.balance
        self.transactions[str(datetime.now())] = record

    def withdraw(self, amt: int, recipient_name: str = None) -> None:
        Account.check_amt(amt)
        if self.balance < amt:
            raise ValueError("Insufficient Balance")
        self.balance -= amt
        record = {}
        if not recipient_name:
            record["type"] = Account.TRANSACTION_TYPES[0]
        else:
            record["type"] = Account.TRANSACTION_TYPES[2]
            record["recipient"] = recipient_name
        record["amount"] = amt
        record["balance"] = self.balance
        self.transactions[str(datetime.now())] = record


class Bank:
    ACC_COUNT, CARD_COUNT = 0, 9

    def __init__(self, name: str) -> None:
        self.name = name
        self.accounts = {}
        self.cards = {}

    def create_account(
        self, holder: str, pin: str, balance: int
    ) -> Tuple[Account, int, int]:
        acc = Account(holder, pin, balance)
        card_num, acc_num = self.generate_credentials()
        self.cards[card_num] = acc_num
        self.accounts[acc_num] = acc
        Bank.ACC_COUNT += 1
        Bank.CARD_COUNT += 1
        return acc, card_num, acc_num

    def validate(self, card_num: str, pin: str) -> Account:
        if card_num not in self.cards:
            raise UnidentifiedUser("The card number does not exist.")
        account = self.accounts.get(self.cards[card_num])
        if not account.active:
            raise SuspendedUser(
                "Your account has been suspended for \
                security reasons."
            )
        if account.pin != pin:
            raise ValueError("Wrong PIN, Try again.")
        return account

    def transaction(self, sender: Account, recepient_num: str, amt: int) -> None:
        recipient = self.fetch_account(recepient_num)
        if not recipient:
            raise UnidentifiedUser("Recipient information was not found.")
        sender.withdraw(amt, recipient.holder)
        recipient.deposit(amt, sender.holder)

    def generate_credentials(self) -> Tuple[str, str]:
        credentials = [Bank.ACC_COUNT, Bank.CARD_COUNT]
        return tuple(map(lambda x: str.zfill(str(x), 8), credentials))

    def fetch_account(self, acc_num: str) -> Union[Account, None]:
        return self.accounts.get(acc_num)

    def deactivate(self, card_num: str) -> None:
        account = self.accounts.get(self.cards[card_num])
        account.active = False


class Controller:
    THRESHOLD = 3
    DEPOSIT_LIMIT = 5000

    def __init__(self, bank: Bank, init_cash: int) -> None:
        self.bank = bank
        self.cash_bin = init_cash
        self.current_user: Account = None
        self.prev_credentials = None
        self.wrong_count = 0

    def initiate(self, card_num: str, pin: str) -> None:
        try:
            account = self.bank.validate(card_num, pin)
            self.current_user = account
        except ValueError:
            if card_num == self.prev_credentials:
                if self.wrong_count < Controller.THRESHOLD:
                    self.wrong_count += 1
                else:
                    self.bank.deactivate(card_num)
                    self.prev_credentials = None
                    self.wrong_count = 0
            else:
                self.wrong_count = 1
                self.prev_credentials = card_num
            raise IncorrectPIN()

    def check_user_status(self) -> None:
        if not self.current_user:
            raise UnidentifiedUser()

    def check_balance(self) -> int:
        self.check_user_status()
        return self.current_user.balance

    def deposit(self, amt: int) -> None:
        self.check_user_status()
        if amt > Controller.DEPOSIT_LIMIT:
            raise ValueError(
                f"Deposit Limit: \
                {Controller.DEPOSIT_LIMIT}"
            )
        self.current_user.deposit(amt)
        self.cash_bin += amt

    def withdraw(self, amt: int) -> None:
        self.check_user_status()
        if self.cash_bin < amt:
            raise ValueError("Cash bin is deplete.")
        self.current_user.withdraw(amt)
        self.cash_bin -= amt

    def get_transactions(self) -> any:
        self.check_user_status()
        return self.current_user.transactions

    def transaction(self, recepient_num: str, amt: int) -> None:
        self.check_user_status()
        self.bank.transaction(self.current_user, recepient_num, amt)

    def end(self) -> None:
        self.check_user_status()
        self.current_user = None
        self.wrong_count = 0
