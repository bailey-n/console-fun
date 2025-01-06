from __future__ import annotations

from typing import List
import colorama
import keyboard

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

    def select(self) -> int:
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