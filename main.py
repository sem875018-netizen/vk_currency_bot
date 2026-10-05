import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import TOKEN, CURRENCIES
from extensions import APIException, CurrencyConverter


def send_message(vk_session, user_id: int, text: str):
    """Отправка сообщения пользователю."""
    vk_session.method("messages.send", {
        "user_id": user_id,
        "message": text,
        "random_id": 0
    })


def main():
    if not TOKEN or TOKEN == "ВАШ_VK_ТОКЕН":
        print("Ошибка: укажите корректный токен в файле config.py!")
        return

    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkLongPoll(vk_session)

    print("VK Currency Bot успешно запущен и ожидает сообщений...")

    for event in longpoll.listen():
        # Обрабатываем только новые входящие личные сообщения
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            user_id = event.user_id
            text = event.text.strip()
            command = text.lower()

            # Команды справки
            if command in ["/start", "/help", "начать", "старт", "помощь"]:
                help_message = (
                    "👋 Привет! Я бот для конвертации валют.\n\n"
                    "📌 Чтобы узнать стоимость валюты, отправьте сообщение формата:\n"
                    "<валюта 1> <валюта 2> <количество>\n\n"
                    "👉 Пример:\n"
                    "евро доллар 100\n"
                    "рубль евро 5000\n\n"
                    "📋 Дополнительные команды:\n"
                    "/values — список доступных валют\n"
                    "/help — показать эту инструкцию"
                )
                send_message(vk_session, user_id, help_message)

            # Команда списка валют
            elif command == "/values":
                currencies_list = "\n".join([f"• {name.capitalize()} ({code})" for name, code in CURRENCIES.items()])
                values_message = (
                    f"💰 Список доступных валют:\n"
                    f"{currencies_list}\n\n"
                    f"Пример запроса:\nдоллар рубль 50"
                )
                send_message(vk_session, user_id, values_message)

            # Обработка запроса на конвертацию
            else:
                try:
                    parts = text.split()
                    if len(parts) != 3:
                        raise APIException(
                            "Неверное количество параметров!\n"
                            "Формат запроса должен состоять из 3 элементов через пробел:\n"
                            "<имя валюты> <в какую перевести> <количество>\n"
                            "Пример: евро рубль 10"
                        )

                    base, quote, amount = parts
                    result = CurrencyConverter.get_price(base, quote, amount)

                    response_text = f"💵 {amount} {base.lower()} = {result} {quote.lower()}"
                    send_message(vk_session, user_id, response_text)

                except APIException as error:
                    send_message(vk_session, user_id, f"⚠️ Ошибка пользователя:\n{error}")

                except Exception as error:
                    send_message(vk_session, user_id, f"❌ Системная ошибка при обработке запроса:\n{error}")


if __name__ == "__main__":
    main()