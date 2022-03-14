import core.settings as s
# from core.jobmanager import JobManager
from pathlib import Path
import socket, threading, subprocess, os, traceback
from time import sleep
from core.tools import *

jobs = []
# jobman = JobManager()

def getGeneral():
    with open(s.myGeneralJobPath, "r") as file:
        return list(map(lambda x: x.strip(), file.readlines()))

def codeMeaning(jobName, problem):
    if (not problem) or (problem == 131072):
        print(f"{now()} | [JOB-RETURN] {jobName} completed!")
    elif (problem == 1) or (problem == 131073):
        print(f"{now()} | [JOB-RETURN] Communication error between MailManStub.exe and MailMan.exe (Mail Manager).")
    elif (problem == 2) or (problem == 131074):
        print(f"{now()} | [JOB-RETURN] TaskMaster job {jobName} failed to start.")
    elif (problem == 3) or (problem == 131075):
        print(f"{now()} | [JOB-RETURN] MailMan.exe (Mail Manager) failed to start.")
    elif problem == 4 or (problem == 131076):
        print(f"{now()} | [JOB-RETURN] Abnormal termination of MailMan.exe (Mail Manager)")
    elif problem == 5 or (problem == 131077):
        print(f"{now()} | [JOB-RETURN] Job Manager is not available.")
    elif problem == 6 or (problem == 131078):
        print(f"{now()} | [JOB-RETURN] Job Manager is expired.")
    elif problem == 7 or (problem == 131079):
        print(f"{now()} | [JOB-RETURN] {jobName} failed!")
    elif problem == 8 or (problem == 131080):
        print(f"{now()} | [JOB-RETURN] TaskMaster job is not started because Mail Manager was not able to be initialized.")
    elif (problem == 196614) or (problem == 65542):
        print(f"{now()} | [JOB-RETURN] Job Manager is running past its expiration dated in a grace period.")
    else:
        print(f"{now()} | [JOB-RETURN] Exited with unknown code {problem}.")


def cleaning():
    pass

def runJobsInQueue():
    global jobs
    exeCommand = [s.mailmanStubPath,"-j", Path(s.masterJob).stem, "-u",s.username, "-w", s.password]
    while True:
        if len(jobs):
            jobs = list(dict.fromkeys(jobs))
            jobNames = list(map(lambda x: x.split("\n")[1], jobs))
            jobNames = [j for j in jobNames if len(j)]
            if len(jobNames):
                job_display = '\n'.join([f" ({i+1}) {jobNames[i]}" for i in range(len(jobNames))])
                print("-"*20)
                print(f"{now()} | [JOB-QUEUE] \n{job_display}")
                print("-"*20)
            job = jobs[0].split("\n")
            if job[0] == s.serverCommand[1]:
                # jobman.checkAndMoveToIncoming()
                pass
            elif job[0] == s.serverCommand[2]:
                # job[2:] = getGeneral()+job[2:]
                commands = "\n".join(job[2:])
                _ = open(s.masterLog, "w").close() # Clears job log file
                with open(s.masterJob, "w") as mjb:
                    mjb.write(commands)
                print(f"{now()} | [JOB-RUNNING] {job[1]} is now running...")
                problem = subprocess.call(exeCommand)
                codeMeaning(job[1], problem)
                print(f"{now()} | [LISTENING] Waiting for jobs to appear...")
            jobs.pop(0)
        sleep(5)

def readMessage(conn):
    msg = None
    msg_length = conn.recv(2048).decode("utf-8")
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode("utf-8")
    return msg

def start():
    thread1 = threading.Thread(target=runJobsInQueue)
    thread1.start()
    if s.jobmanActive:
        pass
        # thread2 = threading.Thread(target=jobman.runJobManager)
        # thread2.start()
    
    while True:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            hostname = socket.gethostbyname(socket.gethostname())
            server.bind((hostname, 0))
            server.listen(20)
            print(f"{now()} | [LISTENING] Server listening...")
            while True:
                conn, _ = server.accept()
                msg = readMessage(conn)  # TODO: Check if the msg contains any non string character
                conn.close()
                msgSplit = msg.split("\n")
                if msgSplit[0] == s.serverCommand[3]:
                    print(msgSplit[-1])
                elif msgSplit[0] == s.serverCommand[4]:
                    pass
                    # jobman.searchForFilesNow()
                elif msgSplit[0] == s.serverCommand[5]:
                    os.system("cls")
                else:
                    jobs.append(msg)
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()
            print(f"{now()} | [REBOOT] Restarting server due to error...")

if __name__ == "__main__":
    start()
