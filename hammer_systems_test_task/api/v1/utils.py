import os
import random
import string


def get_verification_code():
    """Формирование кода авторизации."""
    return random.randint(1000, 9999)


def save_verification_code(phone: str, verification_code: int):
    """Функция сохранения кода подтверждения в файл."""

    directory = os.path.join(os.getcwd(), 'send_sms')

    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = os.path.join(directory, f'{phone}.txt')

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f'Код подтверждения для телефона {phone}: '
                   f'{str(verification_code)}')


def get_invite_code():
    """Формирование инвайт-кода."""

    characters = string.digits + string.ascii_letters
    return ''.join(random.choice(characters) for _ in range(6))
