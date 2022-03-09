from os.path import join
import socket
from pathlib import Path
from configparser import ConfigParser
from sys import platform

###########################################
#                SETTINGS                 #
###########################################

# Chose clear command based on OS
clear = "clear"
if platform == "win32":
    clear = "cls"

# Default
masterFilename = "pymailman"
showComments = False
menuGroup = 20
maildatIDLetter = "EVT"
maildatIDLength = 8
maildatID = lambda ID: f"{maildatIDLetter}{ID}"
# jobsHistorySep = "-+-"*20

# DBF Reader Parameter
companyCuts = [10,110,160,210,260,262,271,281,291,391,421,461,462,512,522,534,542,543,551,559,609,619,669,719,725,775,825,834,846,886,936,956]
companyLength = 977
companyDataStart = 1654
permitCuts = [10,25,65,95,125,135,145,155,205,206]
permitLength = 227
permitDataStart = 598


# Server Commands
serverCommand = {
    1 : "MOVE_TO_INCOMING",
    2 : "RUN_JOB",
    3 : "PRINT_MESSAGE",
    4 : "RESET_JOBMAN",
    5 : "CLEAR_SCREEN"
}

# Server info
HEADER = 2048
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = "utf-8"

# BCC File extensions
jobExt = ".mjb" # Jobs file extension
tempExt = ".mwt" # Templates file extension
listExt = ".dbf" # Lists file extension and other database files
pdrExt = ".pdr" # TODO: Search name of ext 
mdsExt = ".mds" # Maildat Settings file extension

###########################################
#                 PATHS                   #
###########################################

# Current working directory
MAIN = Path(__file__).parents[1]

# Configuration
configur = ConfigParser()
configur.read(join(MAIN, "config.ini"))
bccmainPath = configur.get("mailmanager", "bccpath") 
username = configur.get("mailmanager", "username") 
password = configur.get("mailmanager", "password") 
jobmanWait = configur.getint("jobmanager", "wait")*60 # Waiting time for each execution
jobmanActive = configur.getboolean("jobmanager", "active")

# # JobManager Settings
# logLimit = 1000
# pendingStr = "AddrPending"
# standardStr = "AddrStandardized"

# BCC MailManager default paths
mailmanPath = join(bccmainPath, "MailMan.exe")
mailmanStubPath = join(bccmainPath, "MailManStub.exe")
jobsPath = join(bccmainPath, "Jobs")
templPath =  join(bccmainPath, "Templates")
maildatPath = join(bccmainPath, "MailDat")
settingsPath = join(bccmainPath, "Settings")
maildatSettings = join(settingsPath, "MailDat")
presortTablesPath = join(bccmainPath, "Presort Tables")
dataFilesPath = join(bccmainPath, "Data Files")

# JobManager default paths
jobManMain = join(bccmainPath, "JobManager")
jobManExe = join(bccmainPath, "JobManager.exe")
jobManConfigPath = join(jobManMain, "FileConfiguration.dat")
jobManPrefPath = join(jobManMain, "JobManagerPreferences.dat")
jobManLogPath = join(jobManMain, "JobManagerApplication.log")

# Data Files
permitsFile = join(presortTablesPath, "Permits.dbf")
companyFile = join(dataFilesPath, "Company.dbf")
masterJob = join(jobsPath, f"{masterFilename}.mjb")
masterLog = join(jobsPath, f"{masterFilename}.log")

# Data Paths
mysettingsPath = join(MAIN, "settings")
myPortPath = join(mysettingsPath, "socket", "PORT")
myCommandOptionsPath = join(mysettingsPath, "command_options.json")
myCommandRequiredPath = join(mysettingsPath, "command_required.json")



