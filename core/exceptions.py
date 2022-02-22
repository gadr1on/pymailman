class Exit(Exception):
    pass

class JobRunFinished(Exception):
    pass

class PreviousCommand(Exception):
    pass

class NextCommand(Exception):
    pass

class PreviousPage(Exception):
    pass

class NextPage(Exception):
    pass

class invalidInput(Exception):
    pass

class loadPastJob(Exception):
    pass

class saveCurrentJob(Exception):
    pass

class searchKeyword(Exception):
    pass

class EmptyInput(Exception):
    pass

class defaultVar(Exception):
    pass

class showJobsHistory(Exception):
    pass