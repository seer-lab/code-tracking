import print_error


def test_log_constraint_error_non_fatal(capsys):
    print_error.log_constraint_error(
        description="Missing value",
        context="constraint",
        fatal=False,
    )
    captured = capsys.readouterr()
    assert captured.out == "ERROR: constraint: Missing value\n"


def test_log_constraint_error_fatal(capsys):
    print_error.log_constraint_error(
        description="Invalid file",
        context="data.csv",
        fatal=True,
    )
    captured = capsys.readouterr()
    assert captured.out == "ERROR: Fatal error - File data.csv - Invalid file\n"
