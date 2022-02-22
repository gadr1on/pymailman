from pyreadline import Readline
import pyreadline.console as console

class CommandHistory(Readline):

    def set_readline_console(self):
        console.install_readline(self.readline)
    
    def get_history_list(self):
        return [self.get_history_item(i) for i in range(self.get_current_history_length())]
    
    def get_first_command(self):
        return self.get_history_item(-(self.get_current_history_length()-1))

    def get_last_command(self):
        return self.get_history_item(0)
    
    def add_history_list(self, list : list):
        for l in list: self.add_history(l)
    

if __name__ == "__main__":
    ch = CommandHistory()
    ch.set_readline_console()
    _ = input()
    print(ch.get_completer())
    print(ch.get_line_buffer())