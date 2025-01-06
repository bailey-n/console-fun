from __future__ import annotations

import asyncio
import time
from typing import List, Optional
import colorama
import keyboard
import re
from enum import Enum
import math
from search_bar import SearchBar
from selector_menu import Menu


def main():
    # Note: only works in Pycharm with menu->run->edit configurations...->configuration->execution->Emulate terminal output [enabled]
    # Initialize colorama
    colorama.init()
    # foods = ["Sal.ad", "Sand\\wich", "So?up"]
    wordle_words = open("valid-wordle-words.txt", "r").read().splitlines()
    # menu = Menu(foods)
    # selection = await menu.select()
    # print(f"Selected {foods[selection]}!")
    search_menu = SearchBar(wordle_words)
    search_menu.search()


if __name__ == "__main__":
    main()


