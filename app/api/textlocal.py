import os
import requests


url = "https://api.textlocal.in/send/"


def send_sms(phone, message):
    params = {
        "apikey": os.getenv('TEXTLOCAL_API_KEY'),
        "numbers": phone,
        "message": message,
        "sender": "CTZNVS",
        "test": True,
    }
    response = requests.get(url, params=params)
    return response.text
