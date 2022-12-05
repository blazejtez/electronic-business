import re

site = "https://www.empik.com"
regex_url = "/[a-z|0-9|\-/,|]*"
csv = ".csv"
csv_split = ','
csv_limit = '\''
presta_csv_split = ";"
presta_split_replacement = ":"


def find_and_unpack_url(prefix, sufix, text, find=regex_url):
    for url in re.findall(prefix + find + sufix, text):
        yield url.removeprefix(prefix).removesuffix(sufix)


def find_and_unpack(prefix, sufix, text, find=regex_url):
    for url in re.findall(prefix + find + sufix, text):
        yield url.removeprefix(prefix).removesuffix(sufix)

def find_and_upack_dotall(prefix, sufix, text, find=regex_url):
    for url in re.findall(prefix + find + sufix, text,re.DOTALL):
        yield url.removeprefix(prefix).removesuffix(sufix)

def to_csv(ar):
    st = csv_limit + str(ar[0]) + csv_limit
    for value in ar[1:]:
        st += csv_split + csv_limit + str(value) + csv_limit
    return st


def to_presta_csv(ar):
    st = str(ar[0])
    for value in ar[1:]:
        st += presta_csv_split + str(value).replace(presta_csv_split, presta_split_replacement)
    return st

def three_level_to_presta_csv(ar):
    st = ""
    for l1 in ar:
        if type(l1) is list:
            for l2 in l1:
                for l3 in l2:
                    st += str(l3)+":"
                st = st[:-1]+'|'
            st = st[:-1]+";"
        else:
            st += str(l1) + ";"
    print(st[:-1])
    return st[:-1]

def from_presta_csv(line):
    return re.split(presta_csv_split,line)


def from_csv(line):
    return re.split(csv_limit + csv_split + csv_limit, line[1:-2])

def to_presta_from_dict(header,assignment,ob_dict):
    row = []
    for h in header:
        if h in assignment:
            if type(assignment[h]) is str:
                row.append(ob_dict[assignment[h]])
                continue
            r=[]
            for a in assignment[h]:
                r1 = []
                for a1 in a:
                    if a1 in ob_dict:
                        r1.append(ob_dict[a1])
                    else:
                        r1.append("")
                r.append(r1)
            row.append(r)
        else:
            row.append("")
    return three_level_to_presta_csv(row)

def import_assignment(file):
    assignment = dict()
    for line in file.readlines():
        line = from_presta_csv(line)
        args =line[1].strip()
        if "|" in args or ":" in args:
            args = args.split("|")
            for i,a in enumerate(args):
                args[i] = a.split(":")
        assignment[line[0]]=args

    return assignment
def import_default(file):
    default= dict()
    for line in file.readlines():
        line = from_presta_csv(line)
        default[line[0]] = line[1].strip()
    return default

