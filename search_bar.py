from __future__ import annotations

from typing import List, Optional
import colorama
import keyboard
import re
from enum import Enum
import math


class SearchBar:
    class Mode(Enum):
        Empty = 0
        Escaping = 1
        InvalidMode = 2
        Standard = 3
        Regex = 4
        RegexInvalid = 5

    def __init__(self, options: List[str], max_options_per_page: int = 10):
        self.line_count = len(options)
        self.options: List[str] = options
        self.printed_options: List[str] = []
        self.options_slice: List[str] = options
        self.running = False
        self.search_line: str = ""
        self.cursor: int = 0
        self.max_opts: int = max_options_per_page
        self.flair_text: Optional[str] = None
        self.flair_color: colorama.Fore = colorama.Fore.WHITE
        self.search_text_color: colorama.Fore = colorama.Fore.WHITE
        self.mode: SearchBar.Mode = SearchBar.Mode.Empty
        self.page = 0
        self.num_pages = math.ceil(self.line_count / max_options_per_page)

    def print_base(self):
        for line, option in enumerate(self.options):
            print(f"{self.get_line(line)}{option}")

    def get_line(self, line, line_max=None) -> str:
        if line_max is None:
            line_max = self.line_count
        digits = len(str(line_max))
        return f"[{str(line).zfill(digits)}] "

    def search(self) -> List[str]:
        self.update_display()
        self.running = True
        keyboard.hook(self.handle_key_event, suppress=True)
        while self.running:
            pass
        return self.printed_options

    def handle_key_event(self, event: keyboard.KeyboardEvent):
        if event.event_type == keyboard.KEY_DOWN:
            self.handle_key_down(event.name)

    def handle_key_down(self, key):
        # non_alpha = ["enter"]
        if len(key) == 1:
            self.add_char(key)
        elif key == "enter":
            self.exit()
        elif key == "backspace":
            self.remove_char()
        elif key == "space":
            self.add_char(" ")
        elif key == "tab":
            self.add_char("\t")
        elif key == "right":
            self.scroll_right()
            self.update_display()
        elif key == "left":
            self.scroll_left()
            self.update_display()

    def fix_page_display(self):
        self.num_pages = max(math.ceil(len(self.options_slice) / self.max_opts), 1)
        if self.page > self.num_pages:
            self.page = self.num_pages - 1

    def scroll_right(self):
        self.page = (self.page + 1) % self.num_pages

    def scroll_left(self):
        self.page = (self.page - 1) % self.num_pages

    def set_mode(self, new_mode: SearchBar.Mode):
        self.mode = new_mode

    def flair(self) -> Optional[str]:
        if self.flair_text is None:
            return None
        if self.flair_text == "":
            return None
        return f"{self.flair_color}{self.flair_text}{colorama.Fore.RESET}"

    def add_flair_char(self, key):
        self.flair_text += key

    def remove_flair_char(self):
        if not self.flair_text:
            return
        self.flair_text = self.flair_text[:-1]

    def add_char(self, key):
        if self.mode == SearchBar.Mode.Empty:
            if key == "\\":
                self.set_mode(SearchBar.Mode.Escaping)
                self.flair_text = f"\\"
                self.flair_color = colorama.Fore.YELLOW
                self.update_first_line()
                return
            else:
                self.set_mode(SearchBar.Mode.Standard)
                self.add_char_standard(key)
                return
        elif self.mode == SearchBar.Mode.Escaping:
            if (key == "r") or (key == "R"):
                self.set_mode(SearchBar.Mode.Regex)
                self.flair_text = f"Regex: "
                self.flair_color = colorama.Fore.GREEN
                self.update_first_line()
            elif key == "\\":
                self.set_mode(SearchBar.Mode.Standard)
                self.flair_text = None
                self.flair_color = colorama.Fore.WHITE
                self.add_char_standard("\\")
            elif (key == " ") or (key == "\t"):
                return
            else:
                self.set_mode(SearchBar.Mode.InvalidMode)
                self.flair_text = f"\\{key}"
                self.flair_color = colorama.Fore.RED
                self.update_first_line()
            return
        elif self.mode == SearchBar.Mode.InvalidMode:
            if (key == " ") or (key == "\t"):
                return
            self.add_flair_char(key)
            if self.flair_text.lower() == "regex":
                self.flair_text = f"Regex: "
                self.flair_color = colorama.Fore.GREEN
                self.update_first_line()
        elif self.mode == SearchBar.Mode.Standard:
            self.add_char_standard(key)
        elif self.mode == SearchBar.Mode.Regex:
            self.add_char_regex(key)
        elif self.mode == SearchBar.Mode.RegexInvalid:
            self.add_char_regex(key)

    def add_char_standard(self, key: str):
        self.search_line += key
        search_pattern = self.search_line.replace("\\", "\\\\")
        for special_char in [".", "^", "$", "?", "*", "+", "{", "}", "[", "]", "|", "(", ")"]:
            search_pattern = search_pattern.replace(special_char, "\\" + special_char)
        temp = []
        pattern = re.compile(search_pattern)
        for item in self.options_slice:
            if re.search(pattern, item) is not None:
                temp.append(item)
        self.options_slice = temp
        self.update_display()

    def add_char_regex(self, key: str):
        self.search_line += key
        temp = []
        try:
            pattern = re.compile(self.search_line)
            for item in self.options_slice:
                if re.search(pattern, item) is not None:
                    temp.append(item)
        except re.error:
            self.set_mode(SearchBar.Mode.RegexInvalid)
            self.search_text_color = colorama.Fore.RED
            self.update_first_line()
            return
        self.search_text_color = colorama.Fore.WHITE
        self.options_slice = temp
        self.update_display()

    def remove_char(self):
        if self.mode == SearchBar.Mode.Empty:
            return
        if self.mode == SearchBar.Mode.Escaping:
            self.remove_char_escaping()
            return
        if self.mode == SearchBar.Mode.InvalidMode:
            self.remove_char_invalid()
            return
        if self.mode == SearchBar.Mode.Standard:
            self.remove_char_standard()
            return
        if self.mode == SearchBar.Mode.Regex:
            self.remove_char_regex()
            return
        if self.mode == SearchBar.Mode.RegexInvalid:
            self.remove_char_regex()

    def set_search_empty(self):
        self.search_line = ""
        self.options_slice = self.options
        self.flair_text = ""
        self.flair_color = colorama.Fore.WHITE
        self.set_mode(SearchBar.Mode.Empty)
        self.update_display()

    def remove_char_escaping(self):
        self.set_search_empty()

    def remove_char_invalid(self):
        self.remove_flair_char()
        if self.flair_text.lower() in ["regex", "r"]:
            self.flair_text = f"Regex: "
            self.flair_color = colorama.Fore.GREEN
            self.update_first_line()
            return
        if self.flair_text == "\\":
            self.set_mode(SearchBar.Mode.Escaping)
            self.flair_color = colorama.Fore.YELLOW
            self.update_first_line()
            return

    def remove_char_standard(self):
        if len(self.search_line) == 1:
            self.set_search_empty()
            return
        self.search_line = self.search_line[:-1]
        search_pattern = self.search_line.replace("\\", "\\\\")
        for special_char in [".", "^", "$", "*", "+", "{", "}", "[", "]", "|", "(", ")"]:
            search_pattern = search_pattern.replace(special_char, "\\" + special_char)
        temp = []
        pattern = re.compile(search_pattern)
        for item in self.options:
            if re.search(pattern, item) is not None:
                temp.append(item)
        self.options_slice = temp
        self.update_display()

    def remove_char_regex(self):
        if len(self.search_line) == 0:
            self.flair_text = "\\"
            self.flair_color = colorama.Fore.YELLOW
            self.set_mode(SearchBar.Mode.Escaping)
            self.update_first_line()
        if len(self.search_line) == 1:
            self.search_line = ""
            self.options_slice = self.options
            self.search_text_color = colorama.Fore.WHITE
            self.update_display()
            return
        self.search_line = self.search_line[:-1]
        temp = []
        try:
            pattern = re.compile(self.search_line)
            for item in self.options:
                if re.search(pattern, item) is not None:
                    temp.append(item)
        except re.error:
            self.set_mode(SearchBar.Mode.RegexInvalid)
            self.search_text_color = colorama.Fore.RED
            self.update_first_line()
            return
        self.search_text_color = colorama.Fore.WHITE
        self.options_slice = temp
        self.update_display()

    def reset_cursor(self):
        if self.cursor <= 0:
            return
        print(f"{colorama.Cursor.UP(self.cursor)}",end="\r")
        self.cursor = 0

    def clear_line(self) -> str:
        return f"{colorama.ansi.clear_line()}"

    def cursor_down(self) -> str:
        return f"{colorama.Cursor.DOWN(1)}"

    def update_display(self):
        self.fix_page_display()
        start = self.page * self.max_opts
        length = self.max_opts
        self.update_list(start, length)
        self.update_first_line()

    def update_list(self, start: int = 0, length: Optional[int] = None):
        if start > len(self.options_slice):
            return
        if length is None:
            length = self.max_opts
        end: int = min(start+length, len(self.options_slice))
        if length <= 0:
            if self.printed_options:
                self.clear_options()
            return
        options_to_print = self.options_slice[start:end]
        if self.printed_options == options_to_print:
            return
        self.clear_options()
        print_str = self.cursor_down()
        self.cursor += 1
        length = end-start
        if options_to_print:
            print_str += "\n".join([f"{self.get_line(i+start+1, length)}{line}" for i, line in enumerate(options_to_print)]) + "\n"
        print(print_str, end="\r")
        self.cursor += len(options_to_print)
        self.printed_options = options_to_print

    def clear_options(self):
        # Clear current lines
        self.reset_cursor()
        print_str = self.cursor_down()
        self.cursor += 1
        print_str += f"{colorama.ansi.clear_line()}\n" * len(self.printed_options)
        print(print_str, end="\r")
        self.cursor += len(self.printed_options)
        self.reset_cursor()

    def update_first_line(self):
        self.reset_cursor()
        first_line = self.search_line
        # Write search statement
        if self.mode == SearchBar.Mode.Empty:
            print(f"{self.clear_line()}\rSearch...", end="\r")
            return
        if self.flair() is not None:
            print(f"{self.clear_line()}\r", end=f"{self.flair()}{self.search_text_color}{first_line}{colorama.Fore.RESET}")
        else:
            print(f"{self.clear_line()}\r", end=f"{self.search_text_color}{first_line}{colorama.Fore.RESET}")

    def exit(self):
        self.reset_cursor()
        print(f"{colorama.Cursor.DOWN(self.max_opts)}")
        self.cursor += self.max_opts
        self.running = False
        keyboard.unhook_all()

