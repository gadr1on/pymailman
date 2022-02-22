from .inputmanager import jobrunner_options
from . import settings as s
from os.path import join
from .jobcode import JobCode
import re, os, json
from .exceptions import *
from .tools import *
from .menumanager3 import MenuManager


class CommandLine:

    def __init__(self):
        self.command = None
        self.name = None
        self.varibale = None


class JobRunner:

    def __init__(self):
        self.jobcode = JobCode()
        self.reset_variables()
    
    def reset_variables(self):
        self.cline = CommandLine()
        self.crawl = False
        self.previous = {}
        self.currentIndex = 0
        self.command_num = 2
        self.track = 0

    def start(self):
        self.finished = False
        while not self.finished:
            os.system("cls")
            print(self.selection)
            print(len(self.selection)*"-")
            if self.track:
                display = list(map(lambda c: c.strip(), self.content[:self.track]))
                display = [f" {c}" if (len(c) and c[0]=="[") else f"  {c}" for c in display]
                print("\n".join(display))
            self.set_commands_inputs()
        self.save_commands()
        content = [s.serverCommand[2], self.selection] + self.content
        content = "\n".join(content)
        send(content)
    
    def set_command_history(self, ch):
        self.jobcode.set_command_history(ch)

    def set_selection(self, selection):
        self.selection = selection
        self.jobMainPath = join(s.myjobsPath, f"{selection}{s.jobExt}")
        # self.jobCopyPath = join(s.myjobsCopyPath, f"{selection}{s.jobExt}")
        self.content = self.get_commands()
        self.inputLines = self.get_input_lines(self.content)
    
    def save_previous(self, command, name, input):
        match = re.search(r'^"(.*)"$', input)
        if match:
            input = match.group(1)
        try:
            self.previous[command][name] = input
        except KeyError:
            self.previous[command] = { name : input }
    
    def get_input_lines(self, content):
        inputLines = lambda line : re.search(r"=[\n\? ]+", line)
        inputLines = [i for i in range(len(content)) if inputLines(content[i])]
        return inputLines
    
    def get_jobs_history(self):
        history = readHistory(s.jobsHistoryPath, splitLines=False).split(s.jobsHistorySep)
        history = list(filter(lambda s: len(s) , map(lambda h: h.strip(), history)))
        history = list(map(lambda h1: h1.split("\n"), history))
        history = [(h[0],h[1:]) for h in history if len(h[0])][::-1]
        return history
    
    def save_commands(self):
        content = '\n'.join(self.content)
        # history = readHistory(s.jobsHistoryPath, splitLines=False)
        # if not (content in history):
        message = "{} | {}\n{}\n{}".format(now(), self.selection, content, s.jobsHistorySep)
        makeHistory("jobsHistory" ,s.jobsHistoryPath, message, "%(message)s")
    
    def read_history(self):
        history = self.get_jobs_history()
        titles = list(map(lambda x: x[0], history))
        mm = MenuManager("COMMANDS HISTORY", titles)
        while True:
            try:
                mm.show_menu()
                index = mm.selection.index
                selection = history[index][0].split(" | ")[1]
                self.set_selection(selection)
                self.content = history[index][1]
                try: self.start()
                except JobRunFinished: pass
            except Exit:
                break

    def get_commands(self):
        with open(self.jobMainPath, "r") as j:
            content = j.read()
        content = re.sub(r"#.*", "", content)
        content = [job.strip() for job in content.split("\n")]
        content = [j for j in content if j!=""]
        return content
    
    def command_crawler(self, position):
        if self.crawl:
            while True:
                for i in range(position+1):
                    if self.content[i][0]=="[" and self.content[i][-1]=="]":
                        print(f" {self.content[i]}")
                        continue
                    elif re.search(r"=.*", self.content[i]) and (self.content[i].strip()[0]!="#"):
                        if position == i:
                            print(f"> {self.content[i]}")
                        else:
                            print(f"  {self.content[i]}")
                myInput = input("\n> ")
                try:
                    jobrunner_options(myInput)
                except EmptyInput:
                    positions = self.inputLines[self.inputLines.index(position):]
                    for pos in positions:
                        self.content[pos] = re.sub(r"=.*", "=?", self.content[pos])
                    self.reset_variables()
                raise invalidInput

    def set_command_varName(self, commandline):
        content = commandline.split("=")
        self.cline.name = content[0].strip()
        self.cline.varibale = "=".join(content[1:]).strip()

    def set_previouscommand(self):
        if len(self.inputLines):
            self.crawl = True
            previous = 0
            if self.currentIndex == len(self.content):
                previous = self.inputLines[-1]
            try:
                previous = self.inputLines.index(self.currentIndex)
                if previous > 0:
                    previous = self.inputLines[previous-1]
                else:
                    previous = self.inputLines[-1]
            except ValueError:
                pass
            if previous in self.inputLines:
                self.currentIndex = previous
            self.command_num = 2
            self.track = 0
  
    def set_nextcommand(self):
        if len(self.inputLines):
            self.crawl = True
            if self.currentIndex == len(self.content):
                self.currentIndex = self.inputLines[-1]
            try:
                next = self.inputLines.index(self.currentIndex)
                if next < len(self.inputLines)-1:
                    next = self.inputLines[next + 1]
                else:
                    next = self.inputLines[0]
            except ValueError:
                pass
            if next in self.inputLines:
                self.currentIndex = next
            self.command_num = 2
            self.track = 0

    def set_commands_inputs(self):
        try:
            self.command_crawler(self.currentIndex)
            self.command_linebyline()
            # self.currentIndex = len(self.content)
            final = input("\n> ")
            jobrunner_options(final)
        except invalidInput:
            pass
        except PreviousCommand:
            self.set_previouscommand()
        except NextCommand:
            self.set_nextcommand()
        except EmptyInput:
            if self.currentIndex==len(self.content):
                self.reset_variables()
                self.finished = True
            else:
                self.content[self.currentIndex] = f"{self.cline.name}=DEFAULT"
        except Exit:
            self.reset_variables()
            raise JobRunFinished

    def command_linebyline(self):
        for i in range(self.track, len(self.content)):
            self.currentIndex = i
            if self.content[i][0]=="[" and self.content[i][-1]=="]":
                self.cline.command = re.search(r"\w+", self.content[i]).group(0)
                self.content[i] = "[%s-%s]" % (self.cline.command, self.command_num)
                self.command_num += 1
                print(f" {self.content[i]}")
            elif re.search(r"=.*", self.content[i]) and (self.content[i].strip()[0]!="#"):
                self.set_command_varName(self.content[i])
                command = self.cline.command
                var  = self.cline.varibale
                name = self.cline.name
                if re.search(r"=([ ]+)?\?", self.content[i]):
                    if (not len(var)) or (var[0]=='?'):
                        # self.currentIndex = i
                        print(f"  {name}=", end="")
                        try:
                            self.jobcode.set_commandline(self.cline)
                            self.jobcode.set_previous(self.previous)
                            myinput = self.jobcode.get_command_input()
                            self.previous = self.jobcode.get_previous()
                        except Exit:
                            raise PreviousCommand
                        self.content[i] = myinput
                        self.save_previous(command, name, myinput)
                        raise invalidInput
                else:
                    print(f"  {self.content[i]}")
                self.save_previous(command, name, var)
            self.track = i+1
        self.currentIndex += 1

