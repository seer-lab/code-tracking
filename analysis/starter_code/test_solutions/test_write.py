import pytest

import write


def make_account(**overrides):
    account = {
        "account_number": "12345",
        "name": "Alice",
        "status": "A",
        "balance": 10.0,
        "plan": "SP",
    }
    account.update(overrides)
    return account


def run_write(tmp_path, accounts):
    path = tmp_path / "accounts.txt"
    write.write_new_current_accounts(accounts, str(path))
    return path


def test_valid_write_defaults_plan(tmp_path):
    account = make_account()
    account.pop("plan")

    path = run_write(tmp_path, [account])

    contents = path.read_text().splitlines()
    assert contents[-1] == "00000 END_OF_FILE          A 00000.00 NP"
    assert contents[0].endswith(" NP")


def test_account_number_not_string(tmp_path):
    account = make_account(account_number=12345)

    with pytest.raises(ValueError, match="Account number must be numeric string"):
        run_write(tmp_path, [account])


def test_account_number_not_digits(tmp_path):
    account = make_account(account_number="12A45")

    with pytest.raises(ValueError, match="Account number must be numeric string"):
        run_write(tmp_path, [account])


def test_account_number_too_long(tmp_path):
    account = make_account(account_number="123456")

    with pytest.raises(ValueError, match="Account number exceeds 5 digits"):
        run_write(tmp_path, [account])


def test_name_too_long(tmp_path):
    account = make_account(name="A" * 21)

    with pytest.raises(ValueError, match="Account name exceeds 20 characters"):
        run_write(tmp_path, [account])


def test_invalid_status(tmp_path):
    account = make_account(status="X")

    with pytest.raises(ValueError, match="Invalid status"):
        run_write(tmp_path, [account])


def test_balance_not_numeric(tmp_path):
    account = make_account(balance="10.0")

    with pytest.raises(ValueError, match="Balance must be numeric"):
        run_write(tmp_path, [account])


def test_negative_balance(tmp_path):
    account = make_account(balance=-1.0)

    with pytest.raises(ValueError, match="Negative balance detected"):
        run_write(tmp_path, [account])


def test_balance_too_large(tmp_path):
    account = make_account(balance=100000.0)

    with pytest.raises(ValueError, match="Balance exceeds maximum"):
        run_write(tmp_path, [account])


def test_invalid_plan_type(tmp_path):
    account = make_account(plan="XX")

    with pytest.raises(ValueError, match="Invalid plan type"):
        run_write(tmp_path, [account])
