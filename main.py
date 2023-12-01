import time

from base_read_write import base_read_write
from devices import get_all_devices, send_message_to_phone
from text_randomaizer import randomize_message


def main():
    devices = get_all_devices()
    if len(devices) == 0:
        raise Exception("ADB device not found")
    device = devices[0]
    is_doing = True
    while is_doing:
        phone, name = base_read_write(flag="read")
        if phone == "EOF":
            print("Телефоны закончились, прекращаю отправку")
            break
        print(f"Начинаю отправку по номеру {phone}")
        try:
            message = randomize_message("message-text.txt")  # выбираем сообщение для отправки
        except IndexError:
            print("Не получилось найти сообщения для рассылки на текущее время")
            time.sleep(60)
            continue
        status = send_message_to_phone(phone, name, message, device)
        print(f"Статус отправки по номеру телефона {phone}: {status}")
        print(base_read_write(flag="write", phone_number=phone, status=status))


if __name__ == '__main__':
    main()
