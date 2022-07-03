import fasttext
import csv

input_path_name = r'/workspace/datasets/fasttext/top_words.txt'
output_path_name = r'/workspace/datasets/fasttext/synonyms.csv'
model_path_name = r'/workspace/datasets/fasttext/title_model.bin'
# model_path_name = r'/workspace/datasets/fasttext/normalized_title_model.bin'

model = fasttext.load_model(model_path_name)

threshold = 0.75
top_words_f =  open(input_path_name, 'r')
syn_f = open(output_path_name, 'w') 
csv_writer = csv.writer(syn_f)
for word_line in top_words_f:
    word = word_line.strip()
    row = []
    row.append(word)
    syns = model.get_nearest_neighbors(word)
    for syn_feat in syns:
        syn_name = syn_feat[1]
        similarity = syn_feat[0]
        # print(similarity, syn_name)

        if similarity >= threshold:
            row.append(syn_name)
    print(row)

    if len(row) > 1:
        csv_writer.writerow(row)