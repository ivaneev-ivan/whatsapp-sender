import os
import time

from ppadb.device import Device

from base_read_write import base_read_write
from devices import get_all_devices, send_message_to_phone
from text_randomaizer import randomize_message
from utils import logger_print
import phonenumbers


def run_script(device: Device) -> None:
    if "com.github.uiautomator" in device.list_packages():
        logger_print("Удаляю приложение для управления телефоном перед запуском")
        device.uninstall("com.github.uiautomator")
    is_doing = True
    while is_doing:
        phone, name = base_read_write(flag="read")
        if phone == "EOF":
            logger_print("Телефоны закончились, прекращаю отправку")
            break
        try:
            phonenumbers.parse(phone, "RU")
        except phonenumbers.phonenumberutil.NumberParseException:
            logger_print("empty", "")
            base_read_write(flag="write", phone_number=phone, status="empty")
        try:
            message = randomize_message("message-text.txt")  # выбираем сообщение для отправки
        except IndexError:
            logger_print("Не получилось найти сообщения для рассылки на текущее время")
            time.sleep(60)
            continue
        logger_print(f"Начинаю отправку по номеру {phone}")
        status = send_message_to_phone(phone, name, message, device)
        logger_print(status, '')
        base_read_write(flag="write", phone_number=phone, status=status)


def main():
    while True:
        try:
            devices = get_all_devices()
            if len(devices) != 0:
                logger_print("Обнаружен телефон")
                run_script(devices[0])
                break
        except RuntimeError:
            logger_print("ADB не включен. Попробую включить командой adb devices")
            os.system('adb devices')
            continue
        else:
            logger_print("Телефон не обнаружен. Повтор обнаружения через 15 секунд")
        time.sleep(15)


if __name__ == '__main__':
    main()
