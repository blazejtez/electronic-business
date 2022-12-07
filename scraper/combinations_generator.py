import codecs
import re


def get_acceptable_categories(file, root):
    categories_file = codecs.open(file, 'r', 'utf-8')
    acceptable_categories = [root]
    for line in categories_file.readlines():
        split = re.split(';', line)
        category = split[2]
        parent = split[3]
        if parent in acceptable_categories:
            acceptable_categories.append(category)
    categories_file.close()
    return acceptable_categories


def get_ids(file, acceptable_categories):
    product_file = codecs.open(file, 'r', 'utf-8')
    product_ids = []
    for line in product_file.readlines():
        split = re.split(';', line)
        product_id = split[0]
        category = split[3]
        if category in acceptable_categories:
            product_ids.append(product_id)
    product_file.close()
    return product_ids


def generate_combinations(file, config, product_ids):
    combinations_file = codecs.open(file, 'w', 'utf-8')
    combinations_file.write('Product_ID;Product index;Attributes(name:type:position)*;Values(name:position);Supplier reference;Reference;EAN13;UPC;MPN;Wholesale price;Impact on price;Ecotax;Quantity;Minimal quantity;Low stock;Low stock receive email;Impact on weight;Default;Combination available date;Image position;Image URLs (x,y,z...);Image alt text;ID/Name of shop;Advanced Stock Managment;Depends on stock;Warehouse\n')
    for product_id in product_ids:
        for position, value in enumerate(config['values']):
            combinations_file.write(f'{product_id};;{config["name"]}:{config["type"]}:0;{value}:{position};;;;;;;{config["price"][position]};;{config["quantity"]};;;;;;;;;;;;;\n')
    combinations_file.close()


if __name__ == "__main__":
    combinations_config = {
        'name': 'Okładka',
        'type': 'radio',
        'values': ['Miękka', 'Twarda'],
        'price': ['0', '10'],
        'quantity': '100'
    }

    accept = get_acceptable_categories('categories/presta_categories.csv', 'Książki')
    id_list = get_ids('items/items.csv', accept)
    generate_combinations('items/combinations.csv', combinations_config, id_list)
