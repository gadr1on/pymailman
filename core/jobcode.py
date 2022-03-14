from .exceptions import *
from . import settings as s
from .bcc_data_files import *
from .tools import *
from .inputmanager import jobrunner_options
from .menumanager3 import MenuManager
from os.path import join, isdir, isfile, splitext
# from .toolbox.maildat import nextID
from datetime import datetime as dt
import re

with open(s.myCommandOptionsPath, "r") as file:
    optionContent = json.load(file)
# _, companyData = dbf_reader(s.companyFile, s.companyDataStart, s.companyCuts, s.companyLength)
# _, permitsData = dbf_reader(s.permitsFile, s.permitDataStart, s.permitCuts, s.permitLength)


class JobCode:

    def __init__(self):
        self.menuman = MenuManager()
        self.listname = None
        self.previous = None
        self.menutitle = None
        self.content = None
    
    def set_command_history(self, ch):
        self.ch = ch
    
    def set_commandline(self, cline):
        self.cline = cline
        self.set_menutitle()

    def set_menutitle(self):
        self.menutitle = f'[{self.cline.command}] -> {self.cline.name}'
    
    def set_previous(self, previous):
        self.previous = previous

    def get_commandline(self):
        return self.cline
    
    def get_previous(self):
        return self.previous

    def get_listnames(self):
        dirlistman = DirListManager(s.listsPath)
        dirlistman.filterby_ext(s.listExt)
        dirlistman.sortby_modified()
        dirlistman.remove_exts()
        return dirlistman.get_listdir()

    def get_maildatnames(self):
        dirlistman = DirListManager(s.maildatSettingsPath)
        dirlistman.filterby_ext(s.mdsExt)
        dirlistman.sortby_modified()
        dirlistman.remove_exts()
        return dirlistman.get_listdir()
    
    def get_previous_listname(self, command):
        listpath = self.previous[command]["LIST"]
        listpath = listpath.replace('"', '')
        return basename(listpath)[:-len(s.listExt)]

    def get_permits(self):
        pass

    def get_folder(self):
        try:
            assert self.previous[self.cline.command]["FOLDER"] != None
            return self.previous[self.cline.command]["FOLDER"]
        except (KeyError, AssertionError):
            myinput = input()
            jobrunner_options(myinput)
            if isdir(myinput):
                self.previous[self.cline.command]["FOLDER"] = myinput
        raise invalidInput

    def fix_input(self, input):
        if re.search(r"[ ]{1,}", input) and (not re.match(r'"[^"]+"', input)):
            input = re.sub('"', '""', input)
            input = f'"{input}"'
        return input

    ######## COMMANDS #########

    def _INTEGER(self):
        integer = input()
        jobrunner_options(integer)
        if integer.isdigit():
            return str(integer)

    def _OPTIONS(self):
        options = optionContent[self.cline.command][self.cline.name]
        self.menuman.set_title(self.menutitle)
        self.menuman.set_menu(options)
        self.menuman.show_menu()
        return self.menuman.selection.value

    def _LIST(self):
        files = self.get_listnames()
        self.menuman.set_title(self.menutitle)
        self.menuman.set_menu(files)
        self.menuman.show_menu()
        self.listname = self.menuman.selection.value
        filename = f"{self.listname}{s.listExt}"
        return join(s.listsPath, filename)

    def _FILENAME(self, validExt, exists=False):
        if type(validExt) == str:
            validExt = [validExt]
        elif type(validExt) == list:
            if exists:
                myinput = input()
                jobrunner_options(myinput)
                if isfile(myinput):
                    return myinput
            else:
                folder = self.get_folder()
                filename = input(f"{folder}\\")
                jobrunner_options(filename)
                if not hasUnwantedFilenameChars(filename):
                    filename, ext = splitext(filename)
                    if len(validExt) == 1:
                        return join(folder, f"{filename}{validExt[0]}")
                    else:
                        if ext in validExt:
                            self.previous[self.cline.command]["FOLDER"] = None
                            return join(folder, filename)
        raise invalidInput

    # def PERMITSELECTION(self, data, cols):
    #     files = self.get_listnames() # TODO: sort by last modified
    #     self.menuman.set_title(f'[{self.cline.command}] -> {self.cline.name}')
    #     self.menuman.set_menu(files)
    #     self.menuman.show_menu()
    #     self.menuman.selection.value
    #     return mm.start(f'[{command}] -> {name}', data, cols, sortList=False)

    def _PRESORTNAME(self):
        try:
            return self.previous["PRESORT"]["PRESORTNAME"]
        except KeyError:
            presortname = input()
            jobrunner_options(presortname)
            if hasUnwantedFilenameChars(presortname):
                raise invalidInput
        return presortname

    def _PRESORTNAMESAVED(self):
        presorts = presortnames(s.listsPath, self.listname)
        self.menuman.set_title(self.menutitle)
        self.menuman.set_menu(presorts)
        self.menuman.show_menu()
        return self.menuman.selection.value

    def _PRESORTFILENAME(self, ext=".txt"):
        try:
            presortname = self.previous["PRESORT"]["PRESORTNAME"]
            presortfolder = self.previous["PRESORT"]["PRESORT_FOLDER"]
            self.previous[self.cline.command]["FILETYPE"] = None
            return join(presortfolder, f"{presortname}_{self.cline.command}{ext}")
        except KeyError:
            folder = input()
            jobrunner_options(folder)
            if isdir(folder):
                self.previous["PRESORT"]["PRESORT_FOLDER"] = folder
            raise invalidInput            

    def _MAILDATSETTINGS(self):
        maildatInputKeys = ["JobName", "ShipDate"]
        maildatInputs = dict.fromkeys(maildatInputKeys, "")

        def get_maildat_history():
            presortname = self.previous["MAILDAT"]["PRESORTNAME"]
            jobname = presortname.replace("_"," ").upper()
            monthYear = dt.strftime(dt.now(), '%b%Y').upper()
            maildatHistory = dict.fromkeys(maildatInputKeys, "")
            maildatHistory[maildatInputKeys[0]] = [jobname, f"{jobname} {monthYear}"]
            maildatHistory[maildatInputKeys[1]] = [dt.strftime(dt.now(), '%m/%d/%Y')]
            return maildatHistory

        maildatHistory = get_maildat_history()
        setting_id = dt.strftime(dt.now(), "%m%d%Y%H%M%S")
        setting = f'K{setting_id}'
        mds = self.get_maildatnames()
        self.menuman.set_title(self.menutitle)
        self.menuman.set_menu(mds)
        self.menuman.show_menu()
        maildatSet = self.menuman.selection.value
        maildatSetCommands = readHistory(join(s.maildatSettingsPath, f"{maildatSet}.mds"))
        maildatID = "number" # Change TODO
        writeFile(s.lastMaildatIDLogPath, maildatID)
        programTitle(self.menutitle)
        print(f"  JobID = {maildatID}")
        for key in maildatInputs.keys():
            self.ch.add_history_list(maildatHistory[key])
            maildatInputs[key] = input(f"  {key} = ")
            jobrunner_options(maildatInputs[key])
        presortList = ["FileSetName","JobNumber","JobName","SegmentDescription",
                    "MailPieceName","MailPieceDescription","ComponentDescription"]
        shipDateList = ["MoveUpdateDate", "ShipScheduledDateTime","ShipDate"]
        shipDateTimeList = ["StatementDateTime","InductionDateTime","InductionActualDateTime"]
        for i in range(len(maildatSetCommands)):
            if maildatSetCommands[i].strip()[-1] == "?":
                command = maildatSetCommands[i].split("=")[0].strip()
                if command == "JobIDUser":
                    maildatSetCommands[i] = f"  {command} = '{maildatID}'"
                elif command in presortList:
                    maildatSetCommands[i] = f"  {command} = '{maildatInputs['JobName']}'"
                elif command in shipDateList:
                    maildatSetCommands[i] = f"  {command} = '{maildatInputs['ShipDate']}'"
                elif command in shipDateTimeList:
                    maildatSetCommands[i] = f"  {command} = '{maildatInputs['ShipDate']} 18:00'"
        writeFile(join(s.maildatSettings, f"{setting}{s.mdsExt}"), "\n".join(maildatSetCommands))
        return f'"{setting}"'

    def get_command_input(self):
        """
        This function manages the commands in the job (.mjb file)
        and asks inputs from the user in commands containing the ? sign.
        """
        myinput = None
        # [COMMANDLINE]
        if self.cline.command == "COMMANDLINE":
            if self.cline.name == "SETTINGS":	# (REQUIRED)
                pass
        # [COMPANY]
        elif self.cline.command == "COMPANY":
            if self.cline.name == "ACTION":	# (REQUIRED)
                pass
        # [COMPRESS]
        elif self.cline.command == "COMPRESS":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [CONTAINERTAGS]
        elif self.cline.command == "CONTAINERTAGS":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "PRESORTNAME":	# (REQUIRED)
                myinput = self._PRESORTNAME()
            elif self.cline.name == "TAGTYPE":	# (OPTIONAL)
                myinput = self._OPTIONS()
            elif self.cline.name == "FILETYPE":	# (OPTIONAL)
                myinput = self._OPTIONS()
            elif self.cline.name == "FILENAME":	# (OPTIONAL)
                filetype = None
                fileExt = ".pdf"
                try: filetype = self.previous[self.cline.command]["FILETYPE"]
                except KeyError: pass
                if filetype:
                    if (filetype == "DELIMITED") or (filetype == "TEST"):
                        fileExt = ".txt"
                    elif filetype == "DBASE":
                        fileExt = ".dbf"
                myinput = self._PRESORTFILENAME(fileExt)
        # [CONTAINERTOTALSREPORT]
        elif self.cline.command == "CONTAINERTOTALSREPORT":
            if self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [DATASERVICES]
        elif self.cline.command == "DATASERVICES":
            if self.cline.name == "JOBPASSWORD":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "PROCESSES":	# (REQUIRED)
                pass
        # [DATASERVICESJOB]
        elif self.cline.command == "DATASERVICESJOB":
            if self.cline.name == "JOBPASSWORD":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "PROCESSES":	# (REQUIRED)
                pass
        # [DATASERVICESRETURNJOB]
        elif self.cline.command == "DATASERVICESRETURNJOB":
            if self.cline.name == "JOBPASSWORD":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [DEDUPE]
        elif self.cline.command == "DEDUPE":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [DELETEHIDDENRECORDS]
        elif self.cline.command == "DELETEHIDDENRECORDS":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [DELETELIST]
        elif self.cline.command == "DELETELIST":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "ACTION":	# (REQUIRED)
                pass
        # [DISTRIBUTIONREPORT]
        elif self.cline.command == "DISTRIBUTIONREPORT":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "FILENAME":	# (OPTIONAL)
                myinput = self._FILENAME([".pdf"])
        # [EDDMZIPCRREPORT]
        elif self.cline.command == "EDDMZIPCRREPORT":
            if self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [ENCODE]
        elif self.cline.command == "ENCODE":
            if self.cline.name == "PREPAREDFOR":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [ESUBMISSION]
        elif self.cline.command == "ESUBMISSION":
            if self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [EXPORT]
        elif self.cline.command == "EXPORT":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "SETTINGS":	# (REQUIRED)
                pass
            elif self.cline.name == "FILENAME":	# (OPTIONAL)
                myinput = self._FILENAME([".txt"])
        # [FASTMANAGEAPPOINTMENT]
        elif self.cline.command == "FASTMANAGEAPPOINTMENT":
            if self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "SETTINGS":	# (REQUIRED)
                pass
        # [FASTMANAGECONTENT]
        elif self.cline.command == "FASTMANAGECONTENT":
            if self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "SETTINGS":	# (REQUIRED)
                pass
        # [FASTREPORT]
        elif self.cline.command == "FASTREPORT":
            pass
        # [GENERAL]
        elif self.cline.command == "GENERAL":
            if self.cline.name == "EXECUTIONERRORSENDJOB":	# (OPTIONAL)
                myinput = self._OPTIONS()
            elif self.cline.name == "SUPPRESSTASKERRORS":	# (OPTIONAL)
                myinput = self._OPTIONS()
            elif self.cline.name == "TASKERRORSENDJOB":	# (OPTIONAL)
                myinput = self._OPTIONS()
            elif (self.cline.name == "ONEXECUTIONERRORS") or\
                (self.cline.name == "ONTASKERRORS") or\
                (self.cline.name == "ONJOBTERMINATED"):
                myinput = f'"python ""{s.BCCmessengerScript}"""'
        # [HIDE]
        elif self.cline.command == "HIDE":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [IMPORT]
        elif self.cline.command == "IMPORT":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "SETTINGS":	# (REQUIRED)
                pass
            elif self.cline.name == "FILENAME":	# (OPTIONAL)
                myinput = self._FILENAME([".txt"], exists=True)
        # [INDEX]
        elif self.cline.command == "INDEX":
            if self.cline.name == "ACTION":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "NAME":	# (REQUIRED)
                pass
        # [JOBSETUPREPORT]
        elif self.cline.command == "JOBSETUPREPORT":
            if self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [LABELLAYOUTREPORT]
        elif self.cline.command == "LABELLAYOUTREPORT":
            if self.cline.name == "FILENAME":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "SETTINGS":	# (REQUIRED)
                pass
        # [LABELSIMULATIONREPORT]
        elif self.cline.command == "LABELSIMULATIONREPORT":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [LOAD]
        elif self.cline.command == "LOAD":
            if self.cline.name == "JOB":	# (REQUIRED)
                pass
        # [MAILDAT]
        elif self.cline.command == "MAILDAT":
            if self.cline.name == "PRESORTNAME":	# (REQUIRED)
                if not self.listname:
                    self.listname = self.get_previous_listname("MAILDAT")
                myinput = self._PRESORTNAMESAVED()
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
                mpsfile = join(s.listsPath, f"{self.listname}_.MPS")
                if not isfile(mpsfile):
                    raise invalidInput
            elif self.cline.name == "SETTINGS":
                myinput = self._MAILDATSETTINGS()
            elif self.cline.name == "FIRSTCONTAINER":
                myinput = self._INTEGER()
            elif self.cline.name == "LASTCONTAINER":
                myinput = self._INTEGER()
        # [MANIFESTREPORT]
        elif self.cline.command == "MANIFESTREPORT":
            pass
        # [MERGEPURGE]
        elif self.cline.command == "MERGEPURGE":
            if self.cline.name == "SETTINGS":	# (REQUIRED)
                pass
        # [MODIFY]
        elif self.cline.command == "MODIFY":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "SETTINGS":	# (REQUIRED)
                pass
        # [MODIFYPRESORTED]
        elif self.cline.command == "MODIFYPRESORTED":
            if self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "ABSOLUTECONTAINERNUMBERS":	# (REQUIRED)
                pass
        # [NCOALINK]
        elif self.cline.command == "NCOALINK":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [NEWLISTBLANK]
        elif self.cline.command == "NEWLISTBLANK":
            if self.cline.name == "FILENAME":	# (REQUIRED)
                pass
        # [NEWLISTDBASE]
        elif self.cline.command == "NEWLISTDBASE":
            if self.cline.name == "FILENAME":	# (REQUIRED)
                pass
        # [NEWLISTEDDM]
        elif self.cline.command == "NEWLISTEDDM":
            if self.cline.name == "FILENAME":	# (REQUIRED)
                pass
        # [NEWLISTTEMPLATE]
        elif self.cline.command == "NEWLISTTEMPLATE":
            if self.cline.name == "FILENAME":	# (REQUIRED)
                self.previous[self.cline.command]["FOLDER"] = s.listsPath
                myinput = self._FILENAME([s.listExt])
            elif self.cline.name == "SETTINGS":	# (REQUIRED)
                myinput = self._LIST()
        # [NONPRESORTEDLABELS]
        elif self.cline.command == "NONPRESORTEDLABELS":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "FILENAME":
                myinput = self._FILENAME([".txt"])
            elif self.cline.name == "SETTINGS":
                pass
            elif self.cline.name == "SELECTIVITYEXPRESSION":
                myinput = input()
                jobrunner_options(myinput)
        # [PACKAGE]
        elif self.cline.command == "PACKAGE":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [PERMIT]
        elif self.cline.command == "PERMIT":
            pass
            # if self.cline.name == "ACTION":	# (REQUIRED)
            #     myinput = self._OPTIONS()
            # elif self.cline.name == "DESCRIPTION":	# (REQUIRED)
            #     try: myinput = self.previous[command]["DESCRIPTION"]
            #     except KeyError:
            #         selection = PERMITSELECTION(command, name, permitsData, [1,3])
            #         self.previous[command]["PERMITNUMBER"] = selection[1]
            #         self.previous[command]["PERMITHOLDER"] = selection[3]
            #         myinput = selection[-3]
            # elif self.cline.name == "ORIGINPO":	# (REQUIRED)
            #     pass
            # elif self.cline.name == "PERMITNUMBER":	# (REQUIRED)
            #     try: myinput = self.previous[command]["PERMITNUMBER"]
            #     except KeyError:
            #         selection = PERMITSELECTION(command, name, permitsData, [1,3])
            #         self.previous[command]["DESCRIPTION"] = selection[-3]
            #         self.previous[command]["PERMITHOLDER"] = selection[3]
            #         myinput = selection[1]
            # elif self.cline.name == "PERMITTYPE":	# (REQUIRED)
            #     pass
            # elif self.cline.name == "PERMITHOLDER":	# (OPTIONAL)
            #     try: myinput = self.previous[command]["PERMITHOLDER"]
            #     except KeyError:
            #         selection = PERMITSELECTION(command, name, permitsData, [1,3])
            #         self.previous[command]["DESCRIPTION"] = selection[-3]
            #         self.previous[command]["PERMITNUMBER"] = selection[1]
            #         myinput = selection[1]
            # elif self.cline.name == "PREPAREDFOR":	# (OPTIONAL)
            #     selection = PERMITSELECTION(command, name, companyData, [1,-6])
            #     myinput = selection[1]
        # [POSTAGESTATEMENT]
        elif self.cline.command == "POSTAGESTATEMENT":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
        # [POSTAGESTATEMENT3602C]
        elif self.cline.command == "POSTAGESTATEMENT3602C":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
        # [POSTAGESTATEMENTLOAD]
        elif self.cline.command == "POSTAGESTATEMENTLOAD":
            pass
        # [PRESORT]
        elif self.cline.command == "PRESORT":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "MAILCLASS":	# (OPTIONAL)
                myinput = self._OPTIONS()
            elif self.cline.name == "PIECETYPE":	# (OPTIONAL)
                myinput = self._OPTIONS()
            elif self.cline.name == "PCHEIGHT":	# (OPTIONAL)
                pass
            elif self.cline.name == "PCLENGTH":	# (OPTIONAL)
                pass
            elif self.cline.name == "PCTHICK":	# (OPTIONAL)
                pass
            elif self.cline.name == "PCWT":	# (OPTIONAL)
                pass
            elif self.cline.name == "CONTAINERTYPE":	# (OPTIONAL)
                myinput = self._OPTIONS()
            elif self.cline.name == "SELECTIVITYEXPRESSION":	# (OPTIONAL)
                expression = input()
                jobrunner_options(expression)
                myinput = expression
            elif self.cline.name == "PRESORTNAME":	# (OPTIONAL)
                myinput = self._PRESORTNAME()
        # [PRESORTCONTAINERREPORT]
        elif self.cline.command == "PRESORTCONTAINERREPORT":
            pass
        # [PRESORTEDLABELS]
        elif self.cline.command == "PRESORTEDLABELS":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "PRESORTNAME":	# (REQUIRED)
                myinput = self._PRESORTNAME()
            elif self.cline.name == "FILENAME":	# (OPTIONAL)
                myinput = self._PRESORTFILENAME()
        # [PRESORTSUMMARYREPORT]
        elif self.cline.command == "PRESORTSUMMARYREPORT":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
        # [PROMPT]
        elif self.cline.command == "PROMPT":
            pass
        # [PUBLICATION]
        elif self.cline.command == "PUBLICATION":
            if self.cline.name == "ACTION":	# (REQUIRED)
                pass
            elif self.cline.name == "PUBLICATIONTITLE":	# (REQUIRED)
                pass
        # [QUALIFICATIONREPORT]
        elif self.cline.command == "QUALIFICATIONREPORT":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "PRESORTNAME":	# (REQUIRED)
                myinput = self._PRESORTNAME()
            elif self.cline.name == "FILENAME":	# (OPTIONAL)
                myinput = self._PRESORTFILENAME(".pdf")
        # [QUICKREPORT]
        elif self.cline.command == "QUICKREPORT":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [REBUILDINDEXES]
        elif self.cline.command == "REBUILDINDEXES":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [RECALCULATE]
        elif self.cline.command == "RECALCULATE":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [REORDERLIST]
        elif self.cline.command == "REORDERLIST":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [SUBLIST]
        elif self.cline.command == "SUBLIST":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [TERMINATE]
        elif self.cline.command == "TERMINATE":
            pass
        # [TRACKNTRACEJOB]
        elif self.cline.command == "TRACKNTRACEJOB":
            if self.cline.name == "ACTION":	# (REQUIRED)
                pass
            elif self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "MAILINGDATE":	# (REQUIRED)
                pass
            elif self.cline.name == "ORDERTERMSACCEPTED":	# (REQUIRED)
                pass
            elif self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
        # [TRUCKDIRECTMAIL]
        elif self.cline.command == "TRUCKDIRECTMAIL":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
        # [UNHIDE]
        elif self.cline.command == "UNHIDE":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [UNPACKAGE]
        elif self.cline.command == "UNPACKAGE":
            if self.cline.name == "FILENAME":	# (REQUIRED)
                pass
        # [USERDEFINEDREPORT]
        elif self.cline.command == "USERDEFINEDREPORT":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
        # [USPSPRODUCTREPORT]
        elif self.cline.command == "USPSPRODUCTREPORT":
            if self.cline.name == "REPORTTYPE":	# (REQUIRED)
                pass
        # [ZONEREPORT]
        elif self.cline.command == "ZONEREPORT":
            if self.cline.name == "LIST":	# (REQUIRED)
                myinput = self._LIST()
            elif self.cline.name == "PRESORTNAME":	# (REQUIRED)
                pass
        # [OTHER]
        else:
            myinput = self.cline.variable # raise UnknownCommand
        myinput = self.fix_input(myinput)
        return f"{self.cline.name}={myinput}"
