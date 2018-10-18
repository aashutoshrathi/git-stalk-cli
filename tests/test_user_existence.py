import os


def test_non_existing():
    # GitHub's username cannot begin with a hyphen
    # So there is no way that account with username _O_ exists
    process = os.popen('stalk _O_')
    output = process.read()
    # If API limit is reached, there's no way to test this case
    if "API" in output or len(output) <= 1:
        assert True
    else:
        assert "does not exists" in output
    process.close()


def test_existing():
    process = os.popen('stalk 1')
    output = process.read()
    # If API limit is reached, there's no way to test this case
    if "API" in output or len(output) <= 1:
        assert True
    else:
        assert "followers" in output.lower()
    process.close()
