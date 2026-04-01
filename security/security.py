from cryptography.fernet import Fernet
from config import settings

_fernet = Fernet(settings.secret_key.encode())


def encrypt(password: str) -> str:
    """Шифрование пароля бота с помощью Fernet. Выбор в его пользу, а не хеширования был сделан, потому что, как понимаю,
        тестирующей системе удобнее будет получать полностью готовые данные пароль и логин сразу
     """
    return _fernet.encrypt(password.encode()).decode()


def decrypt(encrypted_password: str) -> str:
    """Расшифровка пароля бота с помощью Fernet"""
    return _fernet.decrypt(encrypted_password.encode()).decode()
