import hashlib
import hmac
import time

from src.config import Config


def check_telegram_authorization(auth_data: dict):
    check_hash = auth_data.pop('hash', None)
    data_check_arr = [f'{key}={auth_data[key]}' for key in sorted(auth_data)]
    data_check_string = '\n'.join(data_check_arr)
    secret_key = hashlib.sha256(Config.BOT_TOKEN.encode()).digest()
    hash_bytes = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if hash_bytes != check_hash:
        raise Exception('Data is NOT from Telegram')

    if time.time() - int(auth_data['auth_date']) > 86400:
        raise Exception('Data is outdated')

    return auth_data
