from app.common.conf import PHONE_NUMBER_VALIDATOR


def phone_number_valid(phone_number):
    if phone_number.is_digit():
        if PHONE_NUMBER_VALIDATOR.match(phone_number):
            return True
    raise ValueError
