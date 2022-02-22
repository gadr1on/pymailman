from os.path import join
from .exceptions import *
import re

# with open(r"\\10.2.1.26\bcc\FS\Templates\aCCUPRINT.mwt", "r", errors="ignore") as f:
#     cont = f.read()

# commands = ["LABEL", "EXPORT", "MDFY_SLCTD", "BROWSE", "DISTREPORT","DATAENTRY","UDREPORT"]


# def template_parameters(all_commands, wanted_command):
#     return re.findall(r"[0-9]{20}(?:(?!"+"|".join(commands)+r").)*"+wanted_command, cont)


# print(template_parameters(commands, commands[6]))

# def dbf_to_dict(header, data):
#     result = map(list, zip(*data))
#     return dict(zip(header, result))

def dbf_to_dict(keyIndex, data):
    return { d[keyIndex] : d[:keyIndex]+d[keyIndex+1:] for d in data }


def dbf_reader(filePath, dataStart, cuts, length):
    with open(filePath, "r", errors="ignore") as f:
        data =  f.read()
        header = re.findall(r"[A-Z0-9]+", data[:dataStart])[2:][::2]
        data = data[dataStart:]
        result = []
        done = False
        while not done:
            cut = [0] + cuts + [length]
            row = [tuple(data[:length][x:y] for x,y in zip(cut, cut[1:]))]
            result += row
            data = data[length:]
            if not len(data):
                done = True
        result = [list(map(lambda x: re.sub(r"\x00","",x.strip()), r)) for r in result]
        return header, result

def key_selection(selected, data):
    return [[data[s][i] for s in selected] for i in range(len(data))]

def value_swap(command, match_key, previous_key,out_key, data, previous):
    # _ = input(data)
    previous = previous[command]
    for i in range(len(data[out_key])):
        # _ = input(data[out_key])
        if data[match_key][i]==previous[previous_key]:
            return data[out_key][i]
    raise KeyError

def presortnames(listFolder, listname):
    file_path = join(listFolder, f"{listname}_.MPS")
    with open(file_path, "r", errors="ignore") as f:
        presorts = f.read()
        presorts = presorts.encode().replace(b"\x00", b"\n")
        presorts = presorts.decode('utf-8')
        presorts = re.findall(r"\.MPS(.*)PK", presorts)
        presorts = [p for p in presorts if len(p.strip())]
        return sorted(presorts)

if __name__ == "__main__":
    import settings as s
    # FIX COMPANY COLUMNS NOT MATCHING
    # print(dbf_reader(s.companyFile, 1654, s.companyCuts, s.companyLength))
    data = dbf_reader(s.permitsFile, 598, s.permitCuts, s.permitLength)
    print(data)
    # print(key_selection(["PERMITNO","PERMITNAME","PREPNAME"],data))

    # for d in company_data(companyPath):
    #     print(d)