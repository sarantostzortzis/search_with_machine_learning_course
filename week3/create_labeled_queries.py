print("hey")
import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv

# Useful if you want to perform stemming.
import nltk
stemmer = nltk.stem.PorterStemmer()

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'
queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/labeled_query_data.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
output_file_name = args.output

if args.min_queries:
    min_queries = int(args.min_queries)

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = 'cat00000'

print("yo")

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
for child in root:
    id = child.find('id').text
    cat_path = child.find('path')
    cat_path_ids = [cat.find('id').text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(list(zip(categories, parents)), columns =['category', 'parent'])

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_csv(queries_file_name)[['category', 'query']]
df = df[df['category'].isin(categories)]

print("Start")

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
df['query'] = df['query'].str.strip().str.lower()
df['query'] = df['query'].str.replace(r"[^a-zA-Z0-9\s]", " ", regex=True)
df['query'] = df['query'].str.replace(r"\s{2,}", " ", regex=True)
df['query'] = df.apply(lambda x: stemmer.stem(x['query']), axis=1)

df['count'] = 1

# print( df[:20])
# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
category_lookup_dict_df = parents_df.set_index("category", drop=True, inplace=False)
category_lookup_dict = category_lookup_dict_df.to_dict()['parent']

# print("Lookup", category_lookup[:20])
print('initial total rows: ', len(df))
print('initial unique cats: ', len(df['category'].unique()))

no_low_cat_left = False
category_count_df = df.groupby(['category']).count()

# print(category_count_df[category_count_df['query'] < 100])
category_lookup_dict[root_category_id] = root_category_id

while not no_low_cat_left:
    
    list_to_replace = list(category_count_df[category_count_df['query'] < min_queries].index)
    print(f"list_to_replace: {len(list_to_replace)}")

    replace_dict = { k: category_lookup_dict[k] for k in list_to_replace}
    df["category"] = df["category"].replace(replace_dict)

    category_count_df = df.groupby(['category']).count()
    low_cat_left = len(list(category_count_df[category_count_df['query'] < min_queries].index))

    print(f"len_low_count: {low_cat_left}")
    if low_cat_left > 0:
        no_low_cat_left = False
    else:
        no_low_cat_left = True

print(category_count_df)


# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
