import copy

VALID_VALUES_FOR_OPTIONAL_FIELDS = [
    ("", None),
    ("  ", None),
    (None, None)
]

INVALID_DATA_TYPES = [
    {},
    [],
    True,
    123456789
]

INVALID_VALUES_FOR_REQUIRED_FIELDS = [
    "",
    "  ",
    None,
    *INVALID_DATA_TYPES
]


def assert_valid_field(validator, base, field, raw, expected):
    data = copy.deepcopy(base)
    data[field] = raw
    errors, cleaned = validator(data)

    assert field not in errors
    assert cleaned.get(field) == expected


def assert_invalid_field(validator, base, field, raw):
    data = copy.deepcopy(base)
    data[field] = raw
    errors, cleaned = validator(data)

    assert field in errors
    assert field not in cleaned
