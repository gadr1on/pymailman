from os.path import join
import socket
from pathlib import Path

# Current working directory
MAIN = Path(__file__).parents[1]

# Settings
showComments = False
menuGroup = 20
maildatIDLetter = "EVT"
maildatIDLength = 8
maildatID = lambda ID: f"{maildatIDLetter}{ID}"
jobsHistorySep = "-+-"*20

# BCC Credentials
username = "ADMIN"
password = "ADMIN"

# BCC Paths
BCCmain = ""
listsFolder = ""
listsPath = join(listsFolder, "Lists")
mailmanPath = join(BCCmain, "MailMan.exe")
mailmanStubPath = join(BCCmain, "MailManStub.exe")
jobsPath = join(BCCmain, "Jobs")
templPath =  join(BCCmain, "Templates")
maildatPath = join(BCCmain, "MailDat")
settingsPath = join(BCCmain, "Settings")
maildatSettings = join(settingsPath, "MailDat")
presortTablesPath = join(BCCmain, "Presort Tables")
dataFilesPath = join(BCCmain, "Data Files")
masterJob = join(jobsPath, "python.mjb")
masterLog = join(jobsPath, "python.log")
permitsFile = join(presortTablesPath, "Permits.dbf")
companyFile = join(dataFilesPath, "Company.dbf")

# JobManager Paths
jobManMain = join(BCCmain, "JobManager")
jobManExe = join(BCCmain, "JobManager.exe")
jobManConfigPath = join(jobManMain, "FileConfiguration.dat")
jobManPrefPath = join(jobManMain, "JobManagerPreferences.dat")
jobManLogPath = join(jobManMain, "JobManagerApplication.log")
ezWarehouse = ""
PendingEDP = join(ezWarehouse, "PendingEDP")
ToIncoming = join(PendingEDP, "ToIncoming")
Incoming = join(ezWarehouse, "Incoming")
donePath = join(PendingEDP, "Done")

# JobManager Settings
timeToWait = 60*60 # Waiting time for each execution
logLimit = 1000
pendingStr = "AddrPending"
standardStr = "AddrStandardized"

# Server Commands
serverCommand = {
    1 : "MOVE_TO_INCOMING",
    2 : "RUN_JOB",
    3 : "PRINT_MESSAGE",
    4 : "RESET_JOBMAN",
    5 : "CLEAR_SCREEN"
}

# Data Paths
mydataPath = join(MAIN, "data")
myjobsPath = join(mydataPath, "jobs")
myjobsOtherPath = join(mydataPath, "jobs_other")
myExePath = join(mydataPath, "exe")
mylogsPath = join(mydataPath, "logs")
mysettingsPath = join(mydataPath, "settings")
maildatSettingsPath = join(mysettingsPath, "maildat")
myaddressStandPath = join(mydataPath, "address_correction")
myPrimaryPath = join(myaddressStandPath, "primary.csv")
myNotAcceptablePath = join(myaddressStandPath, "notacceptable.csv")
myAcceptablePath = join(myaddressStandPath, "acceptable.csv")
jobManDoneFilesPath = join(mydataPath, "jobManager_doneFiles.txt")
jobmanManualJobsPath = join(mysettingsPath, "JobManager_ManualJobs.txt")
myPortPath = join(mysettingsPath, "socket", "PORT")

# JSON
myLayoutHeadPath = join(mysettingsPath, "layout_headers.json")
myCommandOptionsPath = join(mysettingsPath, "command_options.json")
myCommandRequiredPath = join(mysettingsPath, "command_required.json")
toolboxOptionsPath = join(mysettingsPath, "toolboxOptions.json")
etransferAccountsPath = join(mysettingsPath, "ftp_accounts.json")
outlookSendSettings = join(mysettingsPath, "outlook_send.json")

# Other Settings
saveCommandNames = [(presortNamesPath, "PRESORT", "PRESORTNAME")]

# BCC File extensions
jobExt = ".mjb"
tempExt = ".mwt"
listExt = ".dbf"
pdrExt = ".pdr"
mdsExt = ".mds"

# Server info
HEADER = 2048
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = "utf-8"

# DBF Reader Parameter
companyCuts = [10,110,160,210,260,262,271,281,291,391,421,461,462,512,522,534,542,543,551,559,609,619,669,719,725,775,825,834,846,886,936,956]
companyLength = 977
companyDataStart = 1654
permitCuts = [10,25,65,95,125,135,145,155,205,206]
permitLength = 227
permitDataStart = 598

    