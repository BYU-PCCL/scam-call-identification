import pandas as pd

df = pd.read_csv('./data/call_identification.csv')
df = df[['CONVERSATION_ID', 'CONVERSATION_STEP', 'TEXT']]
df_small = df.iloc[0:6]

output_file = './outputs/call_data_chunked.txt'

f = open(output_file, 'a')

for index, row in df_small.iterrows():
    f.write(f'{row["CONVERSATION_STEP"]}. {row["TEXT"]}\n')

f.close()