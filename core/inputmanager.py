from .exceptions import *
from .tools import send
from . import settings as s
from .exceptions import *
import re


def default_options(input):
    if re.match(r"^(e|E)$",input):
        raise Exit

def jobrunner_options(input):
    if not len(input):
        raise EmptyInput
    default_options(input)
    if re.match(r"^(s|S)$",input):
        raise PreviousCommand
    elif re.match(r"^(d|D)$",input):
        raise NextCommand
    elif re.match(r"^(r|R)$", input):
        raise loadPastJob
    elif re.match(r"^(w|W)$", input):
        raise saveCurrentJob

def jobrunner_commands(input):
    if re.match(r"^\\(jmr|JMR)$",input):
        send(s.serverCommand[4])
    if re.match(r"^\\(cls|CLS)$",input):
        send(s.serverCommand[5])
    if re.match(r"^\\(h|H)$",input):
        raise showJobsHistory

def commands(input, name):
    if name == "job_runner":
        jobrunner_commands(input)

def menu_options(input):
    default_options(input)
    if re.match(r"^(a|A)$",input):
        raise PreviousPage
    elif re.match(r"^(f|F)$",input):
        raise NextPage


