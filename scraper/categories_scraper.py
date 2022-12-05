import requests as req
import re
import codecs
from scraper.support_scraper import find_and_unpack_url, site, regex_url, to_csv, find_and_unpack, to_presta_csv, \
    import_assignment, from_presta_csv, to_presta_from_dict, import_default

class_str = '" class="nav-.*__link.*>\n'
cat_dir = "categories/"
presta_cat_file = "presta_categories.csv"


resp = req.get(site)

cat_tree = dict()
cat_id = 3
name_tag = "#NAME"

default_cat = {
    "ID": 2,
    "Active": 1,
    "Name": "Strona Główna",
    "Parent":"",
    "Root": 1,
    "URL": "strona-glowna"
}


def add_to_tree(p, name, tree=cat_tree):
    if len(p) == 0:
        tree[name_tag] = name
    elif p[0] not in tree:
        tree[p[0]] = dict()
    else:
        add_to_tree(p[1:], name, tree[p[0]])


def whole_tree(path="", tree=cat_tree):
    re = []
    if name_tag in tree:
        re = [to_csv([path, tree[name_tag]])]

    for t in tree:
        if t != name_tag:
            re += whole_tree(path + '/' + t, tree[t])
    return re


def leaf(path="", tree=cat_tree):
    if len(tree) == 1 and name_tag in tree:
        return [to_csv([path, tree[name_tag]])]
    re = []
    for t in tree:
        if t != name_tag:
            re += leaf(path + '/' + t, tree[t])
    return re


def precta_tree(path, cat_dict, tree):
    global cat_id
    if not name_tag in tree:
        tree[name_tag] = path.split("/")[-1].split(",")[0].replace("-"," ").title()
        print(tree[name_tag])
            #input("Name not detected\n"+path+"\nName: ")

    re = [
        default |
        {
            "ID": cat_id,
            "Name": tree[name_tag],
            "Parent": cat_dict["Parent"],
            "URL": path
        }
    ]
    cat_id += 1
    for t in tree:
        if t != name_tag:
            cat_dict["Parent"] = tree[name_tag]
            re += precta_tree(path + '/' + t, cat_dict.copy(), tree[t])
    return re

def roots(tree=cat_tree):
    for t in tree:
        if t != name_tag:
            yield t


if __name__ == "__main__":

    file = codecs.open(cat_dir + presta_cat_file, "w", "utf-8")
    presta = codecs.open(cat_dir + "presta_categories.csv", "w", "utf-8")

    afile = codecs.open(cat_dir + "assignment.csv", "r", "utf-8")
    assignment = import_assignment(afile)
    afile.close()

    hfile = codecs.open(cat_dir + "header.csv", "r", "utf-8")
    headers = from_presta_csv(hfile.readline())
    hfile.close()

    dfile = codecs.open(cat_dir + "default.csv", "r", "utf-8")
    default = import_default(dfile)
    dfile.close()

    for cat in find_and_unpack('"', '\n', resp.text, regex_url + class_str + '.*'):
        c = re.split(class_str, cat)
        path = c[0][1:].split("/")
        match = re.search(">[a-z,A-Z,\,,\ ]*<",c[1])
        if match is not None:
            print(match)
            c[1] = match.group(0)[1:-1]
        add_to_tree(path, c[1])

    for r in roots():
        print(r)
    print()

    presta.write(to_presta_csv(headers)+"\n")
    presta.write(to_presta_from_dict(headers, assignment, default_cat)+"\n")
    to_scrap = open(cat_dir+"to_scrap.csv")
    for cat in to_scrap.readlines():
        cat=cat.strip()
        parent_name = cat_tree[cat][name_tag]
        for p in leaf(cat, cat_tree[cat]):
            file.write(p + "\n")
        cat_dict = {"Parent": default_cat["Name"]}
        for p in precta_tree(cat, cat_dict, cat_tree[cat]):
            presta.write(to_presta_from_dict(headers, assignment, p) + "\n")

    to_scrap.close()
    file.close()
