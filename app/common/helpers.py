from app.common.conf import PHONE_NUMBER_VALIDATOR


def phone_number_valid(phone_number):
    if phone_number.isdigit():
        if PHONE_NUMBER_VALIDATOR.match(phone_number):
            return True
    raise ValueError


def normalize_phone_number(phone):
    phone = phone.replace("+", "")
    phone = phone.replace(" ", "")
    if len(phone) == 10:
        phone = f"91{phone}"
    return phone
