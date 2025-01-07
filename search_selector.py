import selector_menu

from search_bar import SearchBar
from selector_menu import Menu


class SearchSelector:
    def __init__(self, options):
        self.options = options
        self.running = False

    def select(self) -> str:
        search_options = []
        starting_value = 0
        selection = None
        while selection is None:
            while not search_options:
                search_bar = SearchBar(self.options)
                search_options = search_bar.search()
                search_bar.clear_options()
                search_bar.reset_cursor()
                starting_value = search_bar.page * search_bar.max_opts + 1
            selection_menu = Menu(search_options, starting_value)
            selection = selection_menu.select()
            if selection is not None:
                selection = selection_menu.options[selection]
        return selection

