import shutil

import requests as req
import re
import codecs

from scraper.lists_of_items_scraper import items_list_file, items_list_dir
from scraper.support_scraper import find_and_unpack_url, site, from_csv, to_csv, find_and_unpack, to_presta_csv, \
    from_presta_csv, import_assignment, to_presta_from_dict, import_default

row_prefix = "<td>"
row_middle = "</td><td><span class=\"attributeDetailsValue\">"
row_suffix = "</span>"
des_prefix = "<div class=\"productDescription ta-product-description \">"
des_suffix = "</div>"

items_detail_dir = "items/"
items_detail_file = "items.csv"

if __name__ == "__main__":
    in_file = codecs.open(items_list_dir+items_list_file, "r", "utf-8")
    out_file = codecs.open(items_detail_dir+items_detail_file, "w", "utf-8")

    afile = codecs.open(items_detail_dir + "assignment.csv", "r", "utf-8")
    assignment = import_assignment(afile)
    afile.close()

    hfile = codecs.open(items_detail_dir + "header.csv", "r", "utf-8")
    headers = from_presta_csv(hfile.readline())
    hfile.close()

    dfile = codecs.open(items_detail_dir + "default.csv", "r", "utf-8")
    default = import_default(dfile)
    dfile.close()

    counter = 0
    out_file.write(to_presta_csv(headers)+"\n")
    for line in in_file.readlines()[:10]:
        print("\n\n",counter,"\n")
        counter += 1
        product = from_presta_csv(line.strip())
        link = product[0]
        if link == "":
            continue
        print(site +"/"+ link,product[1])
        resp = req.get(site +"/"+ link)
        text = resp.text.replace("\n","")
        atributes = default | {
            "Category":product[1],
            "URL":link.replace(",","-"),
        }

        for p in find_and_unpack('<span class="productPriceInfo__price ta-price  withoutLpPromo">', '&nbsp;zł',
                                 text, '.*?'):
            atributes['Price']=p.replace(",",".")

        img_link = ""
        for p in find_and_unpack("itemprop=\"image\" src=\"","\"",text,".*?jpg"):
            img_link = p


        response = req.get(img_link, stream=True)
        link = img_link.split("/")
        print(img_link,"\n",link)
        atributes["Image URL"] = "http://localhost/c/"+link[-1]
        with open(items_detail_dir+"img/"+link[-1], 'wb') as img_file:
             shutil.copyfileobj(response.raw, img_file)

        for prop in find_and_unpack(row_prefix, row_suffix, text, ".*?" + row_middle + ".*?"):
            prop = re.split(row_middle,prop)
            match = find_and_unpack(">","</a>",prop[1],".*?")
            found = False
            for m in match:
                found = True
                atributes[prop[0][:-1]] = m
            if not found:
                atributes[prop[0][:-1]] = prop[1]
        atributes['Autor']=atributes['Autor'].replace("&nbsp;"," ")
        des = re.search(des_prefix+".*?"+des_suffix,text,re.DOTALL).group(0)
        atributes['Description'] = "'"+des.removesuffix(des_suffix).removeprefix(des_prefix).replace("\n","")+"'"



        for a in atributes:
            print(a,":",atributes[a])

        out_file.write(to_presta_from_dict(headers,assignment,atributes)+"\n")
    in_file.close()
    out_file.close()
