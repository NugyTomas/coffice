def check_optional_value(field_name, data, error_name, maximum_length=None):
    errors = {}

    field_value = data.get(field_name)

    if field_value is None:
        return errors, None

    if not isinstance(field_value, str):
        errors[field_name] = f"{error_name} must be a text."
        return errors, None

    field_value = field_value.strip()

    if not field_value:
        return errors, None

    if maximum_length is not None and len(field_value) > maximum_length:
        errors[field_name] = f"{error_name} must contain at most {maximum_length} characters."
        return errors, None
    return errors, field_value


def validate_choice(field_name, data, field_label, enum_class):
    errors = {}
    value = None

    text = data.get(field_name)

    if text is None:
        errors[field_name] = f"{field_label.capitalize()} is required."
    elif not isinstance(text, str):
        errors[field_name] = f"{field_label.capitalize()} must be a text."
    else:
        text = text.strip()

        if not text:
            errors[field_name] = f"{field_label.capitalize()} cannot be empty."
        else:
            try:
                choice = enum_class(text)
            except ValueError:
                errors[field_name] = f"Invalid data! Please choose one of the options."
            else:
                value = choice

    return errors, value
