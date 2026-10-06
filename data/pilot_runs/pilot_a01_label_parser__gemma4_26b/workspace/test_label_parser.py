from label_parser import parse_labels

def test_parse_labels():
    test_cases = [
        ("key1=value1;key2=value2", {"key1": "value1", "key2": "value2"}),
        ("  key1 = value1 ; key2=value2  ", {"key1": "value1", "key2": "value2"}),
        ("key1=value1;invalid_entry;key2=", {"key1": "value1"}),
        ("=value1;key1=;key2=value2", {"key2": "value2"}),
        ("key1=value=with=equals;key2=value2", {"key1": "value=with=equals", "key2": "value2"}),
        ("key1=value1; ;key2=value2", {"key1": "value1", "key2": "value2"}),
        ("", {}),
        (";;;", {}),
    ]

    for input_str, expected in test_cases:
        result = parse_labels(input_str)
        assert result == expected, f"Failed on {input_str!r}: expected {expected}, got {result}"
    print("All tests passed!")

if __name__ == "__main__":
    test_parse_labels()
