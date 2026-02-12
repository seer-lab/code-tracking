import pytest

import read


def build_line(
    account="1234",
    name="NAME",
    status="A",
    balance="00000.00",
    transactions="0001",
    plan="SP",
):
    line = [" "] * 45
    line[0:4] = list(account.ljust(4)[:4])
    line[6:25] = list(name.ljust(19)[:19])
    line[27] = status
    line[29:37] = list(balance.ljust(8)[:8])
    line[38:42] = list(transactions.ljust(4)[:4])
    line[43:45] = list(plan.ljust(2)[:2])
    return "".join(line)


def write_single_line(tmp_path, line):
    path = tmp_path / "accounts.txt"
    path.write_text(line + "\n")
    return path


def test_invalid_length(capsys, tmp_path):
    path = write_single_line(tmp_path, "short")

    accounts = read.read_old_bank_accounts(str(path))

    captured = capsys.readouterr()
    assert "Invalid length" in captured.out
    assert accounts == []


def test_invalid_account_number(capsys, tmp_path):
    line = build_line(account="ABCD")
    path = write_single_line(tmp_path, line)

    accounts = read.read_old_bank_accounts(str(path))

    captured = capsys.readouterr()
    assert "Account number must be 5 digits" in captured.out
    assert accounts == []


def test_invalid_status(capsys, tmp_path):
    line = build_line(status="X")
    path = write_single_line(tmp_path, line)

    accounts = read.read_old_bank_accounts(str(path))

    captured = capsys.readouterr()
    assert "Invalid status" in captured.out
    assert accounts == []


def test_negative_balance_prefix(capsys, tmp_path):
    line = build_line(balance="-0000.01")
    path = write_single_line(tmp_path, line)

    accounts = read.read_old_bank_accounts(str(path))

    captured = capsys.readouterr()
    assert "Negative balance detected" in captured.out
    assert accounts == []


def test_invalid_balance_format(capsys, tmp_path):
    line = build_line(balance="12345678")
    path = write_single_line(tmp_path, line)

    accounts = read.read_old_bank_accounts(str(path))

    captured = capsys.readouterr()
    assert "Invalid balance format" in captured.out
    assert accounts == []


def test_invalid_transaction_count(capsys, tmp_path):
    line = build_line(transactions="0A01")
    path = write_single_line(tmp_path, line)

    accounts = read.read_old_bank_accounts(str(path))

    captured = capsys.readouterr()
    assert "Transaction count must be 4 digits" in captured.out
    assert accounts == []


def test_invalid_plan_type(capsys, tmp_path):
    line = build_line(plan="XX")
    path = write_single_line(tmp_path, line)

    accounts = read.read_old_bank_accounts(str(path))

    captured = capsys.readouterr()
    assert "Invalid plan type" in captured.out
    assert accounts == []


def test_negative_balance_after_convert(capsys, tmp_path, monkeypatch):
    line = build_line(balance="00001.00")
    path = write_single_line(tmp_path, line)

    monkeypatch.setattr(read, "float", lambda _: -1.0)
    accounts = read.read_old_bank_accounts(str(path))

    captured = capsys.readouterr()
    assert "Negative balance detected" in captured.out
    assert accounts == []


def test_negative_transactions_after_convert(capsys, tmp_path, monkeypatch):
    line = build_line(balance="00001.00", transactions="0001")
    path = write_single_line(tmp_path, line)

    monkeypatch.setattr(read, "int", lambda _: -1)
    accounts = read.read_old_bank_accounts(str(path))

    captured = capsys.readouterr()
    assert "Negative transaction not allowed" in captured.out
    assert accounts == []


def test_unexpected_exception(capsys, tmp_path, monkeypatch):
    line = build_line(balance="00001.00", transactions="0001")
    path = write_single_line(tmp_path, line)

    def boom(_):
        raise ValueError("boom")

    monkeypatch.setattr(read, "float", boom)
    accounts = read.read_old_bank_accounts(str(path))

    captured = capsys.readouterr()
    assert "Unexpected error" in captured.out
    assert accounts == []


def test_valid_record_appends_account(tmp_path):
    line = build_line(
        account="0001",
        name="Alice",
        status="A",
        balance="00010.00",
        transactions="0002",
        plan="SP",
    )
    path = write_single_line(tmp_path, line)

    accounts = read.read_old_bank_accounts(str(path))

    assert accounts == [
        {
            "account_number": "1",
            "name": "Alice",
            "status": "A",
            "balance": 10.0,
            "total_transactions": 2,
            "plan": "SP",
        }
    ]
