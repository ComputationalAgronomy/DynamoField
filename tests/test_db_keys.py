
from dynamofield.db import db_keys



def test_check_sort_keys():
    sort_keys = []
    result = db_keys.check_sort_keys(sort_keys)
    expected = []
    assert result == expected

    sort_keys = None
    result = db_keys.check_sort_keys(sort_keys)
    expected = []
    assert result == expected

    sort_keys = ""
    result = db_keys.check_sort_keys(sort_keys)
    expected = []
    assert result == expected

    sort_keys = "aoeu"
    result = db_keys.check_sort_keys(sort_keys)
    expected = ["aoeu"]
    assert result == expected

    sort_keys = ["K1", "K2"]
    result = db_keys.check_sort_keys(sort_keys)
    expected = ["K1", "K2"]
    assert result == expected