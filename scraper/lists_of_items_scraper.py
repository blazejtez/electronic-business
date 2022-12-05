import requests as req
import re
import codecs

from scraper.support_scraper import find_and_unpack_url, site, from_csv, to_csv, from_presta_csv, to_presta_csv
from categories_scraper import cat_dir,presta_cat_file

items_list_dir = "items_list/"
items_list_file = "items_list.csv"
print(__name__)
if __name__=="__main__":
    in_file = codecs.open(cat_dir+presta_cat_file,"r","utf-8")
    out_file = codecs.open(items_list_dir+items_list_file,"w","utf-8")

    hfile = codecs.open(cat_dir + "header.csv","r","utf-8")
    headers = from_presta_csv(hfile.readline())
    hfile.close()

    name_index = headers.index("Name *")
    url_index = headers.index("URL rewritten")
    products = dict()
    for line in in_file.readlines()[2:]:
        cat = from_presta_csv(line)
        cat_url = cat[url_index]
        if cat_url == "":
            continue
        print(site+"/"+cat_url)
        resp = req.get(site+"/"+cat_url)
        for pr in find_and_unpack_url("<a href=\"","\" class=\"img seoImage\"",resp.text):
            print(pr)
            products[pr]=cat[name_index]
        print(len(products))


    for p in products:
        out_file.write(to_presta_csv([p,products[p]])+"\n")
    in_file.close()
    out_file.close()