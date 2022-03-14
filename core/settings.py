from os.path import join, isdir, isfile
import socket, re
from pathlib import Path
from configparser import ConfigParser

###########################################
#                SETTINGS                 #
###########################################

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

# # JobManager Settings
# logLimit = 1000
# pendingStr = "AddrPending"
# standardStr = "AddrStandardized"

###########################################
#                 PATHS                   #
###########################################

# Current working directory
MAIN = Path(__file__).parents[1]

# Configuration
configur = ConfigParser()
configFile = join(MAIN, "config.ini")
# Create config file if doesnt exist
if not isfile(configFile):
    # Defining sections and their key and value pairs
    configur["mailmanager_settings"] = {
        "username" : "ADMIN",
        "password" : "ADMIN",
        "maildat_startID" : "00000000",
        "maildat_endID" : "99999999"
    }
    configur["jobmanager_settings"] = {
        "active" : "False",
        "wait" : "60"
    }
    configur["paths"] = {
        "mailmanager_path" : "",
        "jobs_path" : "",
        "maildatsettings_path" : ""
    }

    # Savin config file
    with open(configFile, "w") as file:
        configur.write(file)

# Reding config file and setting variables
configur.read(configFile)
username = configur.get("mailmanager_settings", "username") 
password = configur.get("mailmanager_settings", "password") 
maildatStartID = configur.get("mailmanager_settings", "maildat_startID ") 
maildatEndID = configur.get("mailmanager_settings", "maildat_endID ") 
jobmanWait = configur.getint("jobmanager_settings", "wait")*60 # Waiting time for each execution
jobmanActive = configur.getboolean("jobmanager_settings", "active")
bccmainPath = configur.get("paths", "mailmanager_path") 
maildatSettings = configur.get("paths", "maildatsettings_path") 
jobsPath = configur.get("paths", "jobs_path") 

# BCC MailManager default paths
mailmanPath = join(bccmainPath, "MailMan.exe")
mailmanStubPath = join(bccmainPath, "MailManStub.exe")
templPath =  join(bccmainPath, "Templates")
maildatPath = join(bccmainPath, "MailDat")
settingsPath = join(bccmainPath, "Settings")
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

# Check every path exist and set defaults
if not isdir(bccmainPath):
    raise FileNotFoundError(f"{bccmainPath} directory not found...")
if not isdir(maildatSettings):
    maildatSettings = join(settingsPath, "MailDat")
if not isdir(jobsPath):
    jobsPath = join(jobsPath, "Jobs")
# if (len(maildatStartID) > 0) and (len(maildatStartID) <= maildatIDLength) and \
#    (len(maildatEndID) > 0) and (len(maildatEndID) <= maildatIDLength):
#     startNumber = re.findall(r"\d+", maildatStartID)
#     startNumber = int(startNumber[0]) if len(startNumber) else 0
#     endNumber = re.findall(r"\d+", maildatEndID)
#     endNumber = int(endNumber[0]) if len(endNumber) else 0
#     if startNumber < endNumber:
#         
