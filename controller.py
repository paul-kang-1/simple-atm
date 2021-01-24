from datetime import datetime
from typing import Mapping, Union, Tuple


class UnidentifiedUser(ValueError):
    """
    Raised when a specified account does not exist within a bank.
    """

    pass


class IncorrectPIN(ValueError):
    """
    Raised when an incorrect PIN accompanied by a valid card number is given to
    access an account.
    """

    pass


class SuspendedUser(Exception):
    """
    Raised when a user attempts to gain access to a suspended (inactive) account
    through an ATM.
    """

    pass


class Account:
    """
    A class to represent an account stored in a bank.
    ...

    holder : str
        name of the owner of the account
    pin : str
        the number sequence to gain access to the account.
        (type set to string to PINs with leading zeroes)
    balance : int
        the current balance of the account
    active : bool
        the current status of the account. If False, it indicates that the
        account has been suspended due to an erroneous PIN input for more than
        three times.
    transaction : dict
        the record of transactions that involves this account. It holds the
        string timestamp as key, and the dictionary of all other information as
        value.
    """

    # Types of allowed transactions
    TRANSACTION_TYPES = ["withdraw", "deposit", "send", "receive"]

    def __init__(self, holder: str, pin: str, balance=0) -> None:
        self.holder = holder
        self.pin = pin
        self.balance = balance
        self.active = True
        self.transactions = {}

    @staticmethod
    def check_amt(amt: int) -> None:
        """Check validity of the provided cash amount.

        Raises:
            ValueError: if `amt` is zero or negative
        """
        if amt <= 0:
            raise ValueError("Amount should be a positive integer.")

    def deposit(self, amt: int, sender_name: str = None) -> None:
        """Deposits the specified amount to the account, adds log to
        transactions.
        """
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
        """Withdraws the specified amount from the account, adds log to
        transactions.

        Raises:
            ValueError: if `amt` exceeds the account's current balance
        """
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
    """
    A class to represent a bank system that the ATM bears.
    ...

    name : str
        name of the bank.
    accounts : str
        a mapping of account numbers to corresponding Account objects.
    cards : dict
        a mapping of card numbers to corresponding account numbers.
    """

    ACC_COUNT, CARD_COUNT = 0, 9  # Counters to assign unique card, acc numbers

    def __init__(self, name: str) -> None:
        self.name = name
        self.accounts = {}
        self.cards = {}

    @staticmethod
    def generate_credentials() -> Tuple[str, str]:
        """Generates a unique string pair of (card number, account number).
        The pairs are of type string due to the possibility of leading zeros.

        Raises:
            ValueError: if `amt` exceeds the account's current balance
        """
        credentials = [Bank.ACC_COUNT, Bank.CARD_COUNT]
        return tuple(map(lambda x: str.zfill(str(x), 8), credentials))

    def create_account(
        self, holder: str, pin: str, balance: int
    ) -> Tuple[Account, int, int]:
        """Creates an account with the information provided and adds to the
        dictionary of card numbers and accounts.
        """
        acc = Account(holder, pin, balance)
        card_num, acc_num = Bank.generate_credentials()
        self.cards[card_num] = acc_num
        self.accounts[acc_num] = acc
        Bank.ACC_COUNT += 1
        Bank.CARD_COUNT += 1
        return acc, card_num, acc_num

    def validate(self, card_num: str, pin: str) -> Account:
        """Validates the credentials (card number and PIN) and provides the
        corresponding Account instance if valid.

        Raises:
            UnidentifiedUser: if the provided `card_num` is nonexistent
            SuspendedUser: if the Account corresponding to the `card_num` is
                suspended (inactive).
            ValueError: if the provided `card_num` is valid, but the `pin` does
                not match the card number.
        """
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
        """Executes the provided transaction with the given information.

        Raises:
            UnidentifiedUser: if the provided `recipient_num` is an invalid
                account number
        """
        recipient = self.fetch_account(recepient_num)
        if not recipient:
            raise UnidentifiedUser("Recipient information was not found.")
        sender.withdraw(amt, recipient.holder)
        recipient.deposit(amt, sender.holder)

    def fetch_account(self, acc_num: str) -> Union[Account, None]:
        """Returns the Account instance corresponding to the provided account
        number. None if nonexistent."""
        return self.accounts.get(acc_num)

    def deactivate(self, card_num: str) -> None:
        """Deactivates the account with the provided card number."""
        account = self.accounts.get(self.cards[card_num])
        account.active = False


class Controller:
    """
    A class to represent a bank system that the ATM bears.
    ...

    bank : Bank
        the bank the ATM belongs to.
    cash_bin : int
        the amount of cash that the machine currently bears.
    current_user : Account
        the current user interacting with the ATM. None if the user ends
        interaction (idle)
    prev_credentials : str
        the card number of the previous failed attempt to access an account with
        an incorrect pin.
    wrong_count : int
        the number of failures to access an account with the card number in
        prev_credintials. If it exceeds the class variable THRESHOLD, it
        suspends the account.
    """

    THRESHOLD = 3  # Maximum number of initiation attempts with a wrong PIN
    DEPOSIT_LIMIT = 5000  # Maximum amount of cash allowed in a single deposit

    def __init__(self, bank: Bank, init_cash: int) -> None:
        self.bank = bank
        self.cash_bin = init_cash
        self.current_user: Account = None
        self.prev_credentials = None
        self.wrong_count = 0

    def initiate(self, card_num: str, pin: str) -> None:
        """ "Signs in" the user, providing access to the account specified
        if the given credentials (card number and PIN) are valid.

        Raises:
            IncorrectPIN: if `card_num` is valid but the `pin` is not
        """
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

    def check_balance(self) -> int:
        """Returns the balance of the current user."""
        return self.current_user.balance

    def deposit(self, amt: int) -> None:
        """Deposits the provided amount to the current account

        Raises:
            ValueError: if `amt` exceeds the deposit limit set for the ATM.
        """
        if amt > Controller.DEPOSIT_LIMIT:
            raise ValueError(
                f"Deposit Limit: \
                {Controller.DEPOSIT_LIMIT}"
            )
        self.current_user.deposit(amt)
        self.cash_bin += amt

    def withdraw(self, amt: int) -> None:
        """Withdraws the provided amount from the current account

        Raises:
            ValueError: if `amt` exceeds the current balance of the account.
        """
        if self.cash_bin < amt:
            raise ValueError("Cash bin is deplete.")
        self.current_user.withdraw(amt)
        self.cash_bin -= amt

    def get_transactions(self) -> any:
        """Returns the transaction-log dictionary of the current user"""
        return self.current_user.transactions

    def transaction(self, recepient_num: str, amt: int) -> None:
        """Performs transaction between the current account and the account
        specified by the provided card number."""
        self.bank.transaction(self.current_user, recepient_num, amt)

    def end(self) -> None:
        """ "Signs out" the user account from the ATM."""
        self.current_user = None
        self.wrong_count = 0
