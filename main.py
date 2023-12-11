import configparser
import os
import random
import re
import time

import phonenumbers
from ppadb.device import Device

from base_read_write import base_read_write
from devices import get_all_devices, send_message_to_phone
from text_randomaizer import randomize_message
from utils import logger_print


def run_script(device: Device) -> None:
    config = configparser.ConfigParser()
    config.read('./config.cfg')
    pauses = (int(config['global']['pauses_min']), int(config['global']['pauses_max']))
    if "com.github.uiautomator" in device.list_packages():
        logger_print("Удаляю приложение для управления телефоном перед запуском")
        device.uninstall("com.github.uiautomator")
    is_doing = True
    while is_doing:
        phone, name = base_read_write(flag="read")
        if phone == "EOF":
            logger_print("Телефоны закончились, прекращаю отправку")
            break
        logger_print(f"Начинаю отправку по номеру {phone} {name}", "")
        try:
            phonenum = phonenumbers.parse(phone, "RU")
            if len(str(phonenum.national_number)) > 10:
                logger_print("empty")
                base_read_write(flag="write", phone_number=phone, status="empty")
                continue
        except phonenumbers.phonenumberutil.NumberParseException:
            logger_print("empty")
            base_read_write(flag="write", phone_number=phone, status="empty")
            continue
        try:
            message = re.sub(r"<name>", name, randomize_message("message-text.txt"))  # выбираем сообщение для отправки
            logger_print(message, '', True)
        except IndexError:
            logger_print("Не получилось найти сообщения для рассылки на текущее время")
            time.sleep(60)
            continue
        status = send_message_to_phone(phone, name, message, device)
        logger_print(status)
        base_read_write(flag="write", phone_number=phone, status=status)
        delay = random.randint(min(pauses), max(pauses))
        for i in range(delay, 0, -1):
            print(f"\rЗадержка перед отправкой следующего сообщения: {i}", end='')
            time.sleep(1)
        print()


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
