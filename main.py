from __future__ import annotations

import colorama
from search_bar import SearchBar
from selector_menu import Menu
from search_selector import SearchSelector

def test_food_menu():
    foods = ["Salad", "Sandwich", "Soup"]
    menu = Menu(foods)
    selection = menu.select()
    print(f"Selected {foods[selection]}!")

def test_wordle_search():
    wordle_words = open("valid-wordle-words.txt", "r").read().splitlines()
    search_menu = SearchBar(wordle_words)
    search_menu.search()

def test_food_search():
    foods = ["Sal.ad", "Sand\\wich", "So?up"]
    search_menu = SearchBar(foods)
    search_menu.search()

def test_wordle_searchselect():
    wordle_words = open("valid-wordle-words.txt", "r").read().splitlines()
    search_menu = SearchSelector(wordle_words)
    print(f"Selected {search_menu.select()}!")

def main():
    # Note: only works in Pycharm with menu->run->edit configurations...->configuration->execution->Emulate terminal output [enabled]
    # Initialize colorama
    colorama.init()
    # test_food_menu()
    # test_wordle_search()
    # test_food_search()
    test_wordle_searchselect()

if __name__ == "__main__":
    main()


