from audioop import reverse
from email.mime import base
import logging, socket, re, json, os, subprocess
from datetime import datetime as dt
from genericpath import isdir
from logging.handlers import RotatingFileHandler
from . import settings as s
from .exceptions import *
from os.path import splitext, basename, isfile, join, isdir, dirname
from os import listdir


class PathManager:

    def __init__(self, path):
        self.path = path
    
    def get_path_ext(self, path):
        return splitext(path)[1]
    
    def get_path_filename(self, path):
        return basename(path)
    
    def get_path_dirname(self, path):
        return dirname(path)
    
    def rem_path_ext(self, path):
        return splitext(path)[0]


class DirListManager(PathManager):
    
    def __init__(self, path):
        self.folder = path
        self.listdir = [f for f in listdir(path)]

    def set_listdir(self, listdir):
        self.listdir = listdir
    
    def get_listdir(self):
        return self.listdir
    
    def remove_exts(self):
        self.set_listdir([self.rem_path_ext(f) for f in self.listdir])

    def set_fullpath_listdir(self):
        self.set_listdir([join(self.folder, f) for f in self.listdir])

    def filterby_ext(self, ext : str):
        self.set_listdir([f for f in self.listdir if self.get_path_ext(f)==ext])
    
    def filterby_dir(self):
        self.set_listdir([f for f in self.listdir if isdir(f)])
    
    def fileterby_file(self):
        self.set_listdir([f for f in self.listdir if isfile(f)])
    
    def sortby_modified(self):
        self.set_listdir(sorted(self.listdir, key=lambda f: os.stat(join(self.folder, f)).st_mtime, reverse=True))

    def sortby_created(self):
        self.set_listdir(sorted(self.listdir, key=lambda f: os.stat(join(self.folder, f)).st_ctime, reverse=True))

    def sortby_size(self):
        self.set_listdir(sorted(self.listdir, key=lambda f: os.stat(join(self.folder, f)).st_size, reverse=True))


#####################################################


def now(strf="%m-%d-%Y %H:%M:%S"):
    return dt.now().strftime(strf)


def readHistory(filePath, splitLines=True, encoding=None):
    try:
        with open(filePath, "r", encoding=encoding) as file:
            content = file.read().strip()
            if splitLines:
                return content.split("\n")
            return content
    except FileNotFoundError:
            return None

def writeFile(filePath, content, encoding=None):
    with open(filePath, "w", encoding=encoding) as file:
        file.write(content)

def readJSON(filePath):
    try:
        with open(filePath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None

def makeHistory(name, logFile, string, strFormat='%(message)s', MB=5):
    log_formatter = logging.Formatter(strFormat)
    my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=MB*1024*1024, 
                                    backupCount=2, encoding=None, delay=0)
    my_handler.setFormatter(log_formatter)
    app_log = logging.getLogger(name)
    if not app_log.hasHandlers():
        app_log.setLevel(logging.INFO)
        app_log.addHandler(my_handler)
    app_log.info(string)

def send(msg):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with open(s.myPortPath, "r") as f:
        PORT = f.read().strip()
    client.connect((s.SERVER, int(PORT)))
    message = msg.encode(s.FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(s.FORMAT)
    send_length += b' ' * (s.HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    client.close()

def getValidPath(myInput):
    try:
        regex = r"(?:[\w]\:|[\\]+[^\\/:\*\?\"<>\|]+)+"
        search = re.search(regex, myInput)
        return search.group()
    except:
        raise invalidInput

def hasUnwantedFilenameChars(string):
    return True if re.search(r"[\\/:\*\?\"<>\|]", string) else False


def getFilenameList(folderPath, Ext=None, showExt=False):
    files = [splitext(basename(f)) for f in listdir(folderPath) if isfile(join(folderPath, f))]
    if Ext: files = [files[i] for i in range(len(files)) if files[i][1]==Ext]
    files = [f"{f[0]}{f[1]}" if showExt else f[0] for f in files]
    return files

def getDirnameList(folderPath):
    files = [basename(f) for f in listdir(folderPath) if isdir(join(folderPath, f))]
    return files

def sortByMod(filenames, filesPath, ext=""):
    return sorted(filenames, key=lambda t: os.stat(join(filesPath,f"{t}{ext}")).st_mtime)

def sortBySize(filenames, filesPath, ext=""):
    return sorted(filenames, key=lambda t: os.stat(join(filesPath,f"{t}{ext}")).st_size)

def isDIR(filePath):
    if isdir(filePath):
        return filePath
    raise invalidInput

def isFILE(filePath):
    if isfile(filePath):
        return filePath
    raise invalidInput

def clearScreen():
    print("\n"*100)
    os.system("cls")

def programTitle(title):
    clearScreen()
    print(f"{title}\n{len(title)*'-'}")

def zipFile(zipFilename, addFilename):
    exe7z = r"C:\Program Files\7-Zip\7z.exe"
    FNULL = open(os.devnull, 'w')
    _, zipType = splitext(zipFilename)
    exeCommand = [exe7z, "a", f"-t{zipType[1:]}", zipFilename, addFilename]
    _ = subprocess.call(exeCommand, stdout=FNULL, stderr=subprocess.STDOUT)

def strContainSpecialChr(string):
    return any([w for w in string if ord(w)>=128 or ord(w)<=31])

def rgbToInt(rgb):
    colorInt = rgb[0] + (rgb[1] * 256) + (rgb[2] * 256 * 256)
    return colorInt