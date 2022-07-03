import argparse

input_path_name = r'/workspace/datasets/fasttext/labeled_products.txt'
output_path_name = r'/workspace/datasets/fasttext/pruned_labeled_products.txt'

parser = argparse.ArgumentParser()
parser.add_argument("min_count", type=int)
args = parser.parse_args()
min_count = args.min_count



cat2count = {}

product_f =  open(input_path_name, 'r')


for line in product_f:
    category_txt = line.split()[0]
    if category_txt not in cat2count.keys():
        cat2count[category_txt] = 0
    cat2count[category_txt] += 1

top_k_categories = []
for cat_name, cat_count in cat2count.items():
    if cat_count >= min_count:
        top_k_categories.append(cat_name)
        print(cat_name, ' : ', cat_count)

pruned_products_f = open(output_path_name, 'w')
with open(input_path_name, 'r') as product_f:
    for line in product_f:
        print(line)
        category_txt = line.split()[0]
        if category_txt in top_k_categories:
            pruned_products_f.write(line)



#Check tree categ
import xml.etree.ElementTree as ET

categoriesFilename = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'
tree = ET.parse(categoriesFilename)
root = tree.getroot()

for child in root:
    catPath = child.find('path')
    idArray = [cat.find('id').text for cat in catPath]
    print(idArray)