import core.settings as s
from core.exceptions import *
from core import *
import traceback
from core.menumanager3 import MenuManager
from core.tools import getFilenameList
from core.commandhistory import CommandHistory

ch = CommandHistory() 
# READ  PREVIOUS HISTORY  ## TODO
ch.set_readline_console()

mm = MenuManager("JOB RUNNER")
jr = JobRunner()
jr.set_command_history(ch)

done = False
while not done:
    try:
        files = getFilenameList(s.myjobsPath, s.jobExt)
        mm.set_menu(files)
        mm.set_commands_name("job_runner")
        mm.sort_list()
        mm.show_menu()
        sel = mm.selection.value
        jr.set_selection(sel)
        jr.start()
    except Exit:
        done = True
    except JobRunFinished:
        continue
    except showJobsHistory:
        jr.read_history()
    except Exception as e:
        _ = input(traceback.print_exc())