import re, shutil, os
from threading import Event
from os.path import join, isfile, splitext, basename
from os import listdir, rename
import unicodedata
from . import settings as s
from .tools import *
import pandas as pd
from datetime import datetime

class JobManager:

    def __init__(self):
        with open(s.jobManPrefPath, "rb") as file:
            pref = file.read().decode('utf-8','ignore')
        with open(s.jobManConfigPath, "rb") as file:
            config = file.read().decode('utf-8','ignore')
        self.prefer = pref
        self.config = self.configuration(config)
        self.filesInWatch = None
        self.configName = None
        self.exit = Event()
    
    ######### JOB MANAGER ##########

    def replaceUnwanted(self, string):
        return string.replace("&amp;","&")

    def cleanConfigUnwanted(self, config, key):
        for k in config: config[k][key] = self.replaceUnwanted(config[k][key])
        return config

    def configuration(self, myconfig):
        # Get fileNames and JobNames of automated jobs
        configDict = {}
        config = re.search(r"<diffgr.*>(.*)</diffgr.*>", myconfig).group()
        filesConfig = re.findall(r"<FileConfiguration[^>]+>[^\"]+</FileConfiguration>", config)
        for fconfig in filesConfig:
            main = re.search(r"<FileConfiguration.*id=\"([\w\d]+)\"[^>]+>(.*)</FileConfiguration>", fconfig)
            configDict[main.group(1)] = {}
            for tag in re.findall(r"<[^<>]+>[^<>]+</[^<>]+>", main.group(2)):
                tag = re.search(r"<([^<>]+)>([^<>]+)</[^<>]+>", tag)
                configDict[main.group(1)][tag.group(1)] = tag.group(2)
        configDict = self.cleanConfigUnwanted(configDict, "FileName")
        return configDict

    def get_PrefFolders(self):
        folders= re.findall(r"(?:[\w]\:|[\\]+[a-zA-Z_\-\s0-9\.]+)+", self.prefer)
        watchFolder, unhandledFolder = [f for f in folders if len(f)>2]
        return watchFolder, unhandledFolder
    
    ######### FILE MANAGEMENT ##########
    
    def noSpecialChars(self, filename):
        return ''.join((c for c in unicodedata.normalize('NFD', filename) if unicodedata.category(c) != 'Mn'))

    def listToPending(self, standardList):
        return list(map(lambda x: s.pendingStr+x[len(s.standardStr):], standardList))
    
    def listToStandard(self, pendingList):
        return list(map(lambda x: s.standardStr+x[len(s.pendingStr):], pendingList))
    
    def searchForFilesNow(self):
        self.exit.set()
        self.exit.clear()
    
    def renameFiles(self):
        filesInWatch = [f for f in listdir(s.PendingEDP) if isfile(join(s.PendingEDP, f)) and (f[:len(s.pendingStr)]==s.pendingStr)]
        renamedFiles = [self.noSpecialChars(f) for f in filesInWatch]
        if filesInWatch != renamedFiles:
            for i in range(len(filesInWatch)):
                if filesInWatch[i] != renamedFiles[i]:
                    rename(join(s.PendingEDP, filesInWatch[i]), join(s.PendingEDP, renamedFiles[i]))
        renamedFiles = list(map(lambda x: self.replaceUnwanted(x), renamedFiles))
        return renamedFiles
    
    def share_all_history(self):
        auto = list(map(lambda x: f"{x}\n", readHistory(s.sentToIncomingPath)))
        manual = readHistory(s.jobManLogPath, splitLines=False).strip()
        dateRe = r"([0-9]{2}/[0-9]{2}/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2})"
        manual = re.findall(dateRe + r".*(AddrPending[^ ]+\.txt)", manual)
        df = pd.DataFrame(manual, columns =['Datetime', 'Filename'])
        df = df.drop_duplicates(['Filename'], keep='last')
        manual = df.values.tolist()
        manual = [f"{col[0].replace('/','-')} | {col[1].replace('AddrPending','AddrStandardized')}\n"
                    for col in manual]
        allhistory = manual+auto
        allhistory = sorted(allhistory, key = lambda date: datetime.strptime(date[:19], '%m-%d-%Y %H:%M:%S'))
        writeFile(s.sharedSentToIncomingLogPath, "".join(allhistory))

    def checkAndMoveToIncoming(self):
        # CHECKING FOR COMPLETED
        standardInToIncoming = [f for f in listdir(s.ToIncoming) if isfile(join(s.ToIncoming, f)) and (f[:len(s.standardStr)]==s.standardStr)]
        finishedFiles = self.listToStandard(self.filesInWatch)
        for file in standardInToIncoming:
            history = readHistory(s.sentToIncomingPath, splitLines=False)
            if history:
                if re.search(file, history):
                    shutil.move(join(s.ToIncoming, file), join(self.config[self.configName]["MoveToFolder"], file))
                    print(f"{now()} | [FILE-DUPLICATE] {file} moved to {basename(self.config[self.configName]['MoveToFolder'])}...")
                    continue
            shutil.move(join(s.ToIncoming, file), join(s.Incoming, file))
            makeHistory("jobmanHistory", s.sentToIncomingPath, f"{now()} | {file}", '%(message)s')
            print(f"{now()} | [FILE-MOVED] {file} moved to {basename(s.Incoming)}...")
        print(f"{now()} | [FILE-MOVED] {len(standardInToIncoming)} files moved to {basename(s.Incoming)}...")

        # CHECKING FOR FAILED
        failedFiles = list(set(finishedFiles) - set(standardInToIncoming))
        failedFiles = list(set(self.leftBehindFiles() + failedFiles))
        failedFiles = [s.pendingStr+f[len(s.standardStr):] if (s.standardStr in f) else f for f in failedFiles]
        if len(failedFiles):
            for file in failedFiles:
                shutil.copy(join(self.config[self.configName]["MoveToFolder"], file), join(s.PendingEDP, file))
                print(f"{now()} | [FILE-MOVED] {file} moved to {basename(s.PendingEDP)}...")
            print(f"{now()} | [FILE-MOVED] {len(failedFiles)} files moved to {basename(s.PendingEDP)}...")
        self.filesInWatch = None

        self.share_all_history()

    
    def getFileConfigName(self, config, file):
        for key in config.keys():
            if re.match(config[key]["FileName"], file):
                return key
        return None
    
    def changeSpecificCommand(self, commands, command, name, new):
        found_command = None
        for i in range(len(commands)):
            find_command = re.search(r"^\[([\w\d]+).*\]$", commands[i])
            if find_command: 
                found_command = find_command.group(1)
                continue
            if found_command == command:
                if re.match(name+r"=.*", commands[i]):
                    if re.search(r"[ ]{1,}", new):
                        new = f'"{new}"'
                    commands[i] = f"{name}={new}"
        return commands
    
    def changeAllCommand(self, commands, name, new):
        return [name+"="+new if re.match(name+r"[= ]+.*", c) else c for c in commands]
    
    def replaceVars(self, string, filename):
        return string.format(inputfilename = filename)

    def leftBehindFiles(self):
        standardFiles = self.listToStandard(readHistory(s.pendingFilesPath))
        sentToIncomingFiles = readHistory(s.sentToIncomingPath, splitLines=False)
        standardFiles = [stand for stand in standardFiles if not re.search(stand, sentToIncomingFiles) and len(stand)]
        pendingFiles = self.listToPending(standardFiles)
        if len(pendingFiles):
            writeFile(s.pendingFilesPath, "\n".join(pendingFiles)+"\n")
        else:
            writeFile(s.pendingFilesPath, "")
        return pendingFiles


    def jobPreparation(self, jobPath, myFile, config):
        myFile, ext = splitext(myFile)
        myFileAndExt = f"{myFile}{ext}"
        jobFile = join(jobPath, config["JobName"])
        with open(jobFile, "r") as file:
            commands = list(map(lambda x: x.strip(), file.readlines()))
        commands = [c for c in commands if len(c) and (not re.match(r"#.*", c))]

        if config["ReplaceImportFilename"] == "true":
            commands = self.changeSpecificCommand(commands, "IMPORT", "FILENAME", join(config["MoveToFolder"], myFileAndExt))
        if config["NewListTemplate_ReplaceFilename"] == "true":
            filename = self.replaceVars(config["NewListTemplate_Filename"], myFile)
            commands = self.changeSpecificCommand(commands, "NEWLISTTEMPLATE", "FILENAME", filename)
            if config["NewListTemplate_UseFilenameAsActiveList"] == "true":
                commands = self.changeAllCommand(commands, "LIST", filename)
        if config["NonPresortedLabels_ReplaceFilename"] == "true":
            filename = self.replaceVars(config['NonPresortedLabels_Filename'], f"{s.standardStr}{myFileAndExt[len(s.pendingStr):]}")
            commands = self.changeSpecificCommand(commands, "NONPRESORTEDLABELS", "FILENAME", filename)
        return commands

    def runJobManager(self):
        excluded = readHistory(s.jobmanManualJobsPath)
        while True:
            filesInWatch = self.renameFiles()
            print(f"{now()} | [FILE-FOUND] {len(filesInWatch)} files found in PendingEDP...")
            filesInWatch = [f for f in filesInWatch if not any([re.match(ex, f) for ex in excluded])]
            self.filesInWatch = filesInWatch + self.leftBehindFiles()
            if len(filesInWatch):
                for file in filesInWatch:
                    makeHistory("PENDING_FILE", s.pendingFilesPath, file, '%(message)s', 1)
                    configName = self.getFileConfigName(self.config, file)
                    self.configName = configName
                    if configName and (self.config[configName]["Enabled"]=="true"):
                        try:
                            shutil.move(join(s.PendingEDP, file), join(self.config[configName]["MoveToFolder"], file))
                            commands = self.jobPreparation(s.jobsPath, file, self.config[configName])
                            send("\n".join([s.serverCommand[2], file]+commands))
                        except FileNotFoundError:
                            shutil.copy(join(self.config[configName]["MoveToFolder"], file), join(s.PendingEDP, file))
                send("\n".join([s.serverCommand[1],"",""]))
            self.share_all_history()
            self.exit.wait(s.timeToWait)
