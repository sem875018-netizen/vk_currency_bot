import json
import requests
from config import CURRENCIES


class APIException(Exception):
    """Пользовательское исключение для обработки ошибок ввода и работы с API."""
    pass


class CurrencyConverter:
    @staticmethod
    def get_price(base: str, quote: str, amount: str) -> float:
        """
        Метод конвертации валюты.
        :param base: исходная валюта (например, 'евро')
        :param quote: целевая валюта (например, 'доллар')
        :param amount: количество исходной валюты
        :return: итоговая сумма в целевой валюте
        """
        base = base.lower().strip()
        quote = quote.lower().strip()

        # 1. Проверка на одинаковые валюты
        if base == quote:
            raise APIException(f"Невозможно перевести одинаковые валюты «{base}».")

        # 2. Проверка существования валюты base
        try:
            base_ticker = CURRENCIES[base]
        except KeyError:
            raise APIException(f"Не удалось распознать валюту «{base}». Доступные валюты можно узнать командой /values.")

        # 3. Проверка существования валюты quote
        try:
            quote_ticker = CURRENCIES[quote]
        except KeyError:
            raise APIException(f"Не удалось распознать валюту «{quote}». Доступные валюты можно узнать командой /values.")

        # 4. Проверка корректности введенного числа
        try:
            # Поддерживаем ввод чисел через запятую или точку
            amount_val = float(amount.replace(",", "."))
            if amount_val <= 0:
                raise APIException("Количество валюты должно быть больше нуля.")
        except ValueError:
            raise APIException(f"Не удалось обработать количество: «{amount}». Введите корректное число.")

        # 5. Запрос к бесплатному API курсов валют
        url = f"https://api.exchangerate-api.com/v4/latest/{base_ticker}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as error:
            raise APIException(f"Ошибка соединения с сервисом курсов валют: {error}")

        # 6. Парсинг ответа JSON
        try:
            data = json.loads(response.text)
            rate = data["rates"][quote_ticker]
        except (KeyError, json.JSONDecodeError):
            raise APIException("Ошибка обработки данных курса валют от стороннего сервиса.")

        total = round(rate * amount_val, 2)
        return total