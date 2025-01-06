from __future__ import annotations

import asyncio
from typing import List
import colorama
import keyboard
import re


class SearchBar:
    def __init__(self, options: List[str]):
        self.line_count = len(options)
        self.options: List[str] = options
        self.printed_options: List[str] = []
        self.options_slice: List[str] = options
        self.running = False
        self.search_line = ""
        self.cursor = 0

    def print_base(self):
        for line, option in enumerate(self.options):
            print(f"{self.get_line(line)}{option}")

    def get_line(self, line) -> str:
        digits = len(str(self.line_count))
        return f"[{str(line).zfill(digits)}] "

    def search(self):
        self.update_display()
        self.running = True
        keyboard.hook(self.handle_key_event, suppress=True)
        while self.running:
            pass

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

    def add_char(self, key):
        self.search_line += key
        temp = []
        for item in self.options_slice:
            # TODO: Compile pattern to use literal no matter what
            if re.search(self.search_line, item) is not None:
                temp.append(item)
        self.options_slice = temp
        self.update_display()

    def remove_char(self):
        if len(self.search_line) == 0:
            return
        if len(self.search_line) == 1:
            self.search_line = ""
            self.options_slice = self.options
            self.update_display()
            return
        if len(self.search_line) > 1:
            self.search_line = self.search_line[:-1]
            temp = []
            for item in self.options:
                # TODO: Compile pattern to use literal no matter what
                if re.search(self.search_line, item) is not None:
                    temp.append(item)
            self.options_slice = temp
            self.update_display()

    def reset_cursor(self):
        if self.cursor <= 0:
            return
        print(f"{colorama.Cursor.UP(self.cursor)}",end="\r")
        self.cursor = 0

    def clear_line(self):
        print(f"{colorama.ansi.clear_line()}",end="\r")

    def cursor_down(self):
        self.cursor += 1
        print(f"{colorama.Cursor.DOWN(1)}", end="\r")

    def update_display(self):
        first_line = self.search_line
        # Write search statement
        if first_line == "":
            first_line = "Search..."
        self.reset_cursor()
        self.clear_line()
        print(f"{first_line}")
        self.cursor += 1
        # Done if there are no changes to the options
        if self.printed_options == self.options_slice:
            return
        # Clear current lines
        print_str = f"{colorama.ansi.clear_line()}\n" * len(self.printed_options)
        print(print_str,end="\r")
        self.cursor += len(self.printed_options)
        # for i in range(len(self.printed_options)):
        #     self.clear_line()
        #     self.cursor_down()
        # Write new lines below search
        self.reset_cursor()
        self.cursor_down()
        # TODO: change i to correspond to placement in options
        if self.options_slice:
            print_str = "\n".join([f"{self.get_line(i)}{line}" for i, line in enumerate(self.options_slice)]) + "\n"
        else:
            print_str = ""
        print(print_str,end="\r")
        # for i, line in enumerate(self.options_slice):
        #     print(f"{self.get_line(i)}{line}")
        #     self.cursor += 1
        self.cursor += len(self.options_slice)
        self.printed_options = self.options_slice

    def exit(self):
        self.reset_cursor()
        print(f"{colorama.Cursor.DOWN(self.line_count)}")
        self.running = False

class Menu:
    def __init__(self, options: List[str]):
        self.line_count = len(options)
        self.options = options
        self.cursor = 0
        self.running = False

    def print_base(self):
        for line, option in enumerate(self.options):
            print(f"{self.get_line(line)}{option}")

    def get_line(self, line) -> str:
        digits = len(str(self.line_count))
        return f"[{str(line).zfill(digits)}] "

    async def select(self) -> int:
        self.print_base()
        self.select_init()
        self.running = True
        keyboard.hook(self.handle_key_event, suppress=True)
        while self.running:
            pass
        return self.cursor

    def handle_key_event(self, event: keyboard.KeyboardEvent):
        if event.event_type == keyboard.KEY_DOWN:
            self.handle_key_down(event.name)

    def handle_key_down(self, key: str):
        f_dict = {
            "down": self.select_down,
            "up": self.select_up,
            "enter": self.exit,
        }
        if key not in f_dict:
            return
        f_dict[key]()

    def select_init(self):
        self.cursor = 0
        print(f"{colorama.Cursor.UP(self.line_count)}{self.get_line(self.cursor)}{colorama.Fore.RED}{self.options[self.cursor]}{colorama.Fore.WHITE}", end="\r")

    def move_cursor(self, delta):
        if not delta:
            return
        self.unselect_current()
        self.cursor += delta
        if delta < 0:
            print(f"{colorama.Cursor.UP(abs(delta))}{self.get_line(self.cursor)}{colorama.Fore.RED}{self.options[self.cursor]}{colorama.Fore.WHITE}", end="\r")
        else: # delta > 0 case
            print(f"{colorama.Cursor.DOWN(delta)}{self.get_line(self.cursor)}{colorama.Fore.RED}{self.options[self.cursor]}{colorama.Fore.WHITE}", end="\r")

    def select_down(self):
        change = ((self.cursor + 1) % self.line_count) - self.cursor
        self.move_cursor(change)

    def select_up(self):
        change = ((self.cursor - 1) % self.line_count) - self.cursor
        self.move_cursor(change)

    def unselect_current(self):
        print(f"{colorama.Fore.WHITE}{self.get_line(self.cursor)}{self.options[self.cursor]}",end="\r")

    def exit(self):
        self.running = False
        print(f"{colorama.Cursor.DOWN(self.line_count - self.cursor)}",end="\r")


async def main():
    # Note: only works in Pycharm with menu->run->edit configurations...->configuration->execution->Emulate terminal output [enabled]
    # Initialize colorama
    colorama.init()
    foods = ["Salad", "Sandwich", "Soup"]
    # wordle_words = open("valid-wordle-words.txt", "r").read().splitlines()[::140]
    # menu = Menu(foods)
    # selection = await menu.select()
    # print(f"Selected {foods[selection]}!")
    search_menu = SearchBar(foods)
    search_menu.search()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


