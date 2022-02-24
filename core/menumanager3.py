import itertools, os
from . import settings as s
from .exceptions import *
from .inputmanager import menu_options, commands

class Selection(object):

    def __init__(self):
        self.index = None
        self.input = None
        self.value = None


class MenuManager:

    def __init__(self, title=None, menu=None):
        if title: self.set_title(title)
        if menu: self.set_menu(menu)
        self.page = 0
        self.search = True
        self.commands_name = None
        self.marked = []
        self.selection = Selection()
    
    def set_search(self, search : bool):
        self.search = search
    
    def set_commands_name(self, name : str):
        self.commands_name = name
    
    def set_title(self, title):
        self.title = title
    
    def set_menu(self, menu):
        self.original = menu
        self.menu = self.assign_ID(menu)
        self.menuHasCols = True if (type(menu[0]) == list) else False
        self.set_menu_2D()
    
    def set_menu_2D(self):
        self.menu2D = self.menu_pages(self.menu, s.menuGroup)
        self.menu2Dummy = self.menu2D
    
    def reset_selection(self):
        self.selection = Selection()
    
    def reset_page_num(self):
        self.page = 0
    
    def reset_marked(self):
        self.marked = []
    
    def remove_marked(self, value):
        index = self.marked.index(value)
        self.marked.pop(index)
    
    def mark_selection(self, index):
        self.marked += [index]

    def menu_pages(self, menu, menuGroup):
        group = [iter(menu)] * menuGroup
        pages = list(itertools.zip_longest(*group, fillvalue=""))
        pages[-1] = [pag for pag in pages[-1] if pag!=""]
        return pages
    
    def assign_ID(self, menu):
        menu = [(i+1, menu[i]) for i in range(len(menu))]
        return menu
    
    def sort_list(self):
        sort_func = lambda x: ord(x[0].lower())
        if self.menuHasCols:
            sort_func = lambda x: ord(x[0][0].lower())
        menu = sorted(self.original, key=sort_func)
        self.set_menu(menu)
    
    def merge_cols(self, colsToShow):
        colsToShow = sorted(colsToShow)
        if self.menuHasCols:
            menu = [[m[col] for col in colsToShow] for m in self.original]
            maximo = [max([len(menu[j][i]) for j in range(len(self.menu))]) for i in range(len(menu[0]))]
            formatt = ["{%d:>%d}" % (i, maximo[i]) for i in range(len(maximo))]
            formatt = " | ".join(formatt)
            menu = [formatt.format(*ele) for ele in menu]
            self.menu = self.assign_ID(menu)
            self.set_menu_2D()
        
    def get_selection(self):
        return self.selection

    def pages_print(self, pages, spacing=2):
        message = "Select one option:"
        print(f"{message:>{spacing}}\n")
        for i in range(len(pages[self.page])):
            ID, option = pages[self.page][i]
            if i in self.marked:
                ID = f"*{ID}"
            print(f"{ID:>{spacing*2}}. {option}")
        print(f"\n{self.page+1}/{len(pages)}")

    def search_keyword(self, keyword, menu):
        found = [ f for f in menu if (keyword in f[1].lower())]
        if found:
            return self.menu_pages(found, s.menuGroup)
        return self.menu2D
    
    def cls(self):
        print("\n"*100)
        os.system(s.clear)
    
    def show_menu(self):
        done = False
        while not done:
            try:
                self.cls()
                print(f"{self.title}\n{len(self.title)*'-'}")
                self.pages_print(self.menu2Dummy)
                myInput = input("\n> ")
                index = 0
                if myInput.isdigit():
                    index = int(myInput)-1
                    if ((index>(len(self.original)-1)) or ((index+1)<=0)):
                        raise invalidInput
                    self.selection.index = index
                    self.selection.input = myInput
                    self.selection.value = self.original[index]
                else:
                    self.selection.input = myInput
                    menu_options(myInput)
                    if self.commands_name:
                        commands(myInput, self.commands_name)
                    if self.search:
                        raise searchKeyword
                return
            except invalidInput:
                continue
            except PreviousPage:
                if self.page>0:
                    self.page -= 1
            except NextPage:
                if self.page<(len(self.menu2Dummy)-1):
                    self.page += 1
            except searchKeyword:
                self.page = 0
                self.menu2Dummy = self.search_keyword(myInput, self.menu)
            except EmptyInput:
                self.page = 0
                self.menu2Dummy = self.menu2D
            
