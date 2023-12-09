import random
import re
import time
from enum import Enum
from typing import NamedTuple, Optional

import uiautomator2 as u2
from ppadb.client import Client as AdbClient
from ppadb.device import Device as DeviceADB
from uiautomator2 import UiObject
from loguru import logger



TYPE_CHAR_DELAY_MS = 1


class CommandTypes(Enum):
    NEW_LINE = 1
    SEND_MESSAGE = 2


class MessagePartWithCommand(NamedTuple):
    text: str
    command: Optional[CommandTypes]


class MessagePartWithDelay(NamedTuple):
    parts: list[MessagePartWithCommand]
    start_sleep: int
    stop_sleep: int


def get_control_to_device(device: DeviceADB) -> u2.Device:
    d = u2.connect(device.serial)
    return d


def get_all_devices() -> list[DeviceADB]:
    """Функция для получения всех подключенных по ADB устройств"""
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()
    return devices


def split_part_message_to_command(message: str) -> list[MessagePartWithCommand]:
    """Разбивает текст на список частей сообщений с возможной командой для исполения"""
    commands = re.findall(r"<[a-z]+\. [a-z]+>", message)
    result = []
    for command in commands:
        part, message = message.split(command)
        command_type = None
        if command == "<shift. enter>":
            command_type = CommandTypes.NEW_LINE
        elif command == "<enter. enter>" or command == "<send. button>":
            command_type = CommandTypes.SEND_MESSAGE
        result.append(MessagePartWithCommand(part, command_type))
    result.append(MessagePartWithCommand(message, None))
    return result


def split_message_with_delay(message: str) -> list[MessagePartWithDelay]:
    """Разбивает текст сообщения на части с задержкой"""
    all_sleeps = re.findall(r"<\d+, \d+>", message)
    res = []
    for sleep in all_sleeps:
        parts = message.split(sleep)
        if len(parts) == 2:
            part, message = parts
        else:
            i = 0
            if parts[0] == "":
                i = 1
            part = parts[i]
            message = sleep.join(parts[i + 1:])
        start, stop = map(int, sleep.strip('<>').split(', '))
        res.append(MessagePartWithDelay(split_part_message_to_command(part), start, stop))
    res.append(MessagePartWithDelay(split_part_message_to_command(message), 0, 0))
    return res


def send_char_typing_part(message: MessagePartWithCommand, message_box: UiObject, d: u2.Device) -> str:
    if message.text != "":
        text_before = message_box.get_text()
        if text_before == "Сообщение" or text_before == "Message":
            text_before = ""
        words = message.text.split()
        for i in range(len(words) + 1):
            message_box.send_keys(text_before + " ".join(words[:i]))
    if message.command == CommandTypes.SEND_MESSAGE:
        d(resourceId="com.whatsapp.w4b:id/conversation_entry_action_button").click()
    elif message.command == CommandTypes.NEW_LINE:
        d.press('enter')


def send_message_to_phone(phone: str, name: str, message: str, device: DeviceADB) -> str:
    d = get_control_to_device(device)
    d.logger.disabled = True
    d.unlock()
    d.app_stop('com.whatsapp.w4b')
    d.open_url(f"whatsapp://send?phone={phone}")
    message_box = d(resourceId="com.whatsapp.w4b:id/entry")
    if not message_box.click_exists(10):
        return "empty"
    try:
        message_box.clear_text()
    except u2.UiObjectNotFoundError:
        return "empty"
    message = split_message_with_delay(re.sub(r"<name>", name, message))
    for p in message:
        list(send_char_typing_part(part, message_box, d) for part in p.parts)
        delay = random.uniform(min(p.start_sleep, p.stop_sleep), max(p.start_sleep, p.stop_sleep))
        time.sleep(delay)
    text_before = message_box.get_text()
    if text_before != "Сообщение" and text_before != "Message":
        d(resourceId="com.whatsapp.w4b:id/conversation_entry_action_button").click()
    return "sent"
