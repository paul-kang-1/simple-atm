from controller import *
import pytest

bank1 = Bank("Bank 1")
acc1, card_num1, acc_num1 = bank1.create_account("Kang", "0123", 100)
acc2, card_num2, acc_num2 = bank1.create_account("Paul", "1234", 10)
acc3, card_num3, acc_num3 = bank1.create_account("Jane", "1234", 1000)
sus_acc, card_num_sus, acc_num_sus = bank1.create_account("Jim", "1234", 123)
atm = Controller(bank1, 1000)

bank1.deactivate(card_num_sus)


def test_create_account():
    assert acc1.holder == "Kang"
    assert acc2.holder == "Paul"
    assert acc1.balance == 100
    assert acc2.balance == 10


@pytest.mark.parametrize(
    "card_num,pin,expected",
    [
        (card_num1, "0123", "Kang"),
        (card_num2, "1234", "Paul"),
        (card_num3, "1234", "Jane"),
    ],
)
def test_validate(card_num, pin, expected):
    account = bank1.validate(card_num, pin)
    assert account.holder == expected


def test_validate_error():
    with pytest.raises(UnidentifiedUser):
        bank1.validate("12345678", "0000")
    with pytest.raises(SuspendedUser):
        bank1.validate(card_num_sus, "1234")
    with pytest.raises(ValueError):
        bank1.validate(card_num1, "9999")


def test_atm_initiate():
    atm.initiate(card_num2, "1234")
    assert atm.current_user.holder == "Paul"
    atm.end()
    assert atm.current_user == None


def test_wrong_pin_input():
    for i in range(Controller.THRESHOLD + 1):
        assert atm.wrong_count == i
        with pytest.raises(IncorrectPIN):
            atm.initiate(card_num1, "1234")
    assert atm.wrong_count == 0
    assert acc1.active == False


def test_no_user():
    with pytest.raises(AttributeError):
        atm.check_balance()


def test_check_user_balance():
    atm.initiate(card_num2, "1234")
    assert atm.check_balance() == 10


def test_deposit():
    atm.deposit(100)
    assert atm.current_user.balance == 110


def test_deposit_error():
    # Account side
    with pytest.raises(ValueError):
        atm.deposit(-123)
    # ATM side
    with pytest.raises(ValueError):
        atm.deposit(Controller.DEPOSIT_LIMIT + 1)


def test_withdraw():
    atm.withdraw(50)
    assert atm.check_balance() == 60
    atm.withdraw(10)
    assert atm.check_balance() == 50


def test_withdraw_error():
    # Account side
    with pytest.raises(ValueError):
        atm.withdraw(-123)
    # Insufficient funds
    with pytest.raises(ValueError):
        atm.withdraw(500)
    # Cash bin deplete
    with pytest.raises(ValueError):
        atm.withdraw(2000)


def test_transaction():
    atm.transaction(acc_num3, 10)
    assert atm.check_balance() == 40
    assert acc3.balance == 1010


def test_transaction_error():
    with pytest.raises(UnidentifiedUser):
        atm.transaction("12312312", 10)


def _search_transaction_record(record, tr_type, name):
    if tr_type == "send":
        for k in record.keys():
            tr = record[k]
            if tr["type"] == "send" and tr["recipient"] == name:
                return True
    elif tr_type == "receive":
        for k in record.keys():
            tr = record[k]
            if tr["type"] == "receive" and tr["sender"] == name:
                return True
    return False


def test_transaction_record():
    res = atm.get_transactions()
    found = _search_transaction_record(res, "send", "Jane")
    res_other = acc3.transactions
    found_other = _search_transaction_record(res_other, "receive", "Paul")
    assert found == True
    assert found_other == True
