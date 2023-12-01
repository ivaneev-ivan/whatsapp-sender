import os
import time

from loguru import logger

from base_read_write import base_read_write
from devices import get_all_devices, send_message_to_phone
from text_randomaizer import randomize_message


def main():
    while True:
        try:
            devices = get_all_devices()
        except RuntimeError:
            logger.error("ADB не включен. Попробую включить командой adb devices")
            os.system('adb devices')
            continue
        else:
            if len(devices) != 0:
                logger.info("Обнаружен телефон")
                break
            logger.error("Телефон не обнаружен. Повтор обнаружения через 15 секунд")
        time.sleep(15)
    device = devices[0]
    if "com.github.uiautomator" in device.list_packages():
        logger.info("Удаляю приложение для управления телефоном перед запуском")
        device.uninstall("com.github.uiautomator")
    is_doing = True
    while is_doing:
        phone, name = base_read_write(flag="read")
        if phone == "EOF":
            logger.info("Телефоны закончились, прекращаю отправку")
            break
        logger.info(f"Начинаю отправку по номеру {phone}")
        try:
            message = randomize_message("message-text.txt")  # выбираем сообщение для отправки
        except IndexError:
            logger.warning("Не получилось найти сообщения для рассылки на текущее время")
            time.sleep(60)
            continue
        status = send_message_to_phone(phone, name, message, device)
        logger.info(f"Статус отправки по номеру телефона {phone}: {status}")
        logger.info(base_read_write(flag="write", phone_number=phone, status=status))


if __name__ == '__main__':
    main()
