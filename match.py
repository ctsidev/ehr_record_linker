import pandas as pd
import numpy as np
import json
import csv
import os
import cx_Oracle as ora
from fuzzywuzzy import fuzz

json = json.load(open('config.json'))
left_data = pd.read_csv(json['left_data']['file_path'])
conn = json['right_data']['db_conn']
sql = open(json['right_data']['query_path']).read()

match_dir = json['matching']['match_dir']
if not os.path.exists(match_dir):
    os.mkdir(match_dir)
db = ora.connect(f"{conn['username']}/{conn['password']}@{conn['host']}").cursor()

csv_header = ['WEIGHTED_AVG', 'ID_LEFT', 'ID_RIGHT']
for col in json['matching']['columns']:
    csv_header.append(col['left_col'] + '_LEFT')
    csv_header.append(col['right_col'] + '_RIGHT')

batch_num = 500

for i, l_row in left_data.iterrows():
    if i > 0 and i % batch_num == 0:
        f.close()
        
    if i == 0 or i % batch_num == 0:
        f = open(f"{match_dir}/group_{i}.csv", 'w', encoding='UTF-8')
        out_csv = csv.writer(f)
        out_csv.writerow(csv_header)
    
    db.execute(sql, [l_row[col] for col in json['matching']['right_joins']])
    right_col_list = [row[0] for row in db.description]
    right_cols = {}
    for j, col in enumerate(right_col_list):
        right_cols[col] = j
    
    results_dict = {}
    
    for r_row in db:
        row_score = 0
        l_vals = []
        r_vals = []
        csv_row = [l_row[json['matching']['left_id']]]
        csv_row.append(r_row[right_cols[json['matching']['right_id']]])
        
        for col in json['matching']['columns']:
            match_val = None
            l_val = l_row[col['left_col']]
            csv_row.append(l_val)
            r_val = r_row[right_cols[col['right_col']]]
            csv_row.append(r_val)
            
            if col['algo'] == 'ratio':
                match_val = fuzz.ratio(l_val, r_val)
            elif col['algo'] == 'partial_ratio':
                match_val = fuzz.partial_ratio(l_val, r_val)
            elif col['algo'] == 'token_sort_ratio':
                match_val = fuzz.token_sort_ratio(l_val, r_val)
            elif col['algo'] == 'token_set_ratio':
                match_val = fuzz.token_set_ratio(l_val, r_val)
            
            
            row_score += match_val * col['acc_avg_weight']
    
        results_dict[round(row_score, 2)] = csv_row
    
    best_avg = max(results_dict.keys())
    out_csv.writerow([best_avg] + results_dict[best_avg])
    
    os.system('cls')
    print(f'Records matched: {i+1}')

f.close()