import datetime
import random
import re


class TextNode:

    def __init__(self) -> None:
        self.content = []

    def __str__(self):
        return ''.join(map(str, self.content)) + '\n'

    def get_pure_text(self):
        return ''.join(filter(lambda x: isinstance(x, str), self.content))

    def print_tab(self, tab: int):
        print('\t' * tab, self.get_pure_text())
        for object in self.content:
            if type(object) == TextNode:
                object.print_tab(tab + 1)

    def make_decision(self):
        highsigns = []
        for i in range(len(self.content)):
            if type(self.content[i]) == TextNode:
                if i >= 2:
                    if self.content[i - 1] == '!' and self.content[i - 2] == '!':
                        highsigns.append(i - 1)
                        highsigns.append(i - 2)
                        answer_string: list = list(self.content[i].make_decision())
                        try:
                            answer_string[0] = answer_string[0].upper()
                        except Exception:
                            pass
                        self.content[i] = ''.join(answer_string)
                    else:
                        self.content[i] = self.content[i].make_decision()
                else:
                    self.content[i] = self.content[i].make_decision()
        for highsign in highsigns:
            self.content.pop(highsign)
        text = ''.join(self.content)
        if self.content[0] == '{':
            words = text[1:-1].split('|')
            return random.choice(words)
        elif self.content[0] == '[':
            basis = text[1:-1].split('+')
            separator = basis[1]
            content = basis[2].lstrip(' ').split('|')
            random.shuffle(content)
            return separator.join(content)


class FormatException(Exception):
    pass


def handle_text(text: str) -> str:
    starting_nodes = []
    node_stack = []
    for letter in text:
        if letter == "{" or letter == "[":
            if not node_stack:
                current_node = TextNode()
                current_node.content.append(letter)
                starting_nodes.append(current_node)
                node_stack.append(current_node)
            else:
                current_node = node_stack[-1]
                current_node.content.append(TextNode())
                current_node = current_node.content[-1]
                node_stack.append(current_node)
                current_node.content.append(letter)
        elif letter == "}" or letter == "]":
            if not node_stack:
                raise FormatException
            else:
                current_node = node_stack[-1]
                current_node.content.append(letter)
                node_stack.pop()
        else:
            if node_stack:
                current_node = node_stack[-1]
                current_node.content.append(letter)
            else:
                starting_nodes.append(letter)
    text = ""
    for i in range(len(starting_nodes)):
        node = starting_nodes[i]
        if type(node) == str:
            text += node
        elif type(node) == TextNode:
            if i < 2:
                text += node.make_decision()
            elif starting_nodes[i - 1] == '!' and starting_nodes[i - 2] == '!':
                text = text[:-2]
                answer_string = list(node.make_decision())
                try:
                    answer_string[0] = answer_string[0].upper()
                except Exception:
                    pass
                text += ''.join(answer_string)
            else:
                text += node.make_decision()
    i = 1
    while i < len(text) - 1:
        letter = text[i]
        if letter in ['.', ',', ':', ';']:
            if text[i - 1] == ' ':
                text = text[:i - 1] + text[i:]
                i = i - 1
                continue
            if text[i + 1] != ' ':
                text = text[:i + 1] + " " + text[i + 1:]
                i += 1
        if letter == '—':
            if text[i - 1] != ' ':
                text = text[i - 1:] + " " + text[:i - 1]
                i += 1
                continue
            if text[i + 1] != " " or text[i + 1] != ',':
                text = text[:i + 1] + " " + text[i + 1:]
                i += 1
        i += 1
    text = re.sub(" +", " ", text)
    return text


def randomize_message(filename, is_text=False):
    def read_lines(filename):
        with open(filename, encoding='utf-8') as f:
            file_lines = f.readlines()
            return [line.strip() for line in file_lines if len(line) > 1]

    def filter_lines_by_time(lines, current_time):
        return [line for line in lines if is_line_applicable(line, current_time)]

    def get_current_time_minutes():
        now = datetime.datetime.now()
        return now.hour * 60 + now.minute

    def is_line_applicable(line, current_time):
        time_range = extract_time_range(line)
        if not time_range:
            return True
        start, end = time_range.split('-')
        start_minutes = convert_to_minutes(start)
        end_minutes = convert_to_minutes(end)
        return start_minutes <= current_time <= end_minutes

    def extract_time_range(line):
        match = re.match(r'^\d+:\d+-\d+:\d+', line)
        if match:
            return match.group()
        return ''

    def convert_to_minutes(time):
        hour, minute = map(int, time.split(':'))
        return hour * 60 + minute

    def clear_time_range(line):
        return re.sub(r'^\d+:\d+-\d+:\d+ ', '', line)

    def generate_variations(line):
        variations = []
        for _ in range(5):
            variation = handle_text(clear_time_range(line))
            variations.append(variation)
        return variations

    lines = read_lines(filename)
    current_time = get_current_time_minutes()

    if is_text:
        result = ""
        variations = []
        for line in lines:
            variations.extend(generate_variations(line))

        for v in range(1, len(variations) + 1):
            line = variations[v - 1]
            result += line + "\n"

            if v % 5 == 0 and v != len(variations):
                result += "\n"

        return result
    else:
        filtered_lines = filter_lines_by_time(lines, current_time)
        result2 = random.choice(filtered_lines)
        result2 = handle_text((clear_time_range(result2)))
        return result2
