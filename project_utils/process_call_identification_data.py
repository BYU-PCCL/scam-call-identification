import pandas as pd

df = pd.read_csv('./data/call_identification.csv')
df = df[['CONVERSATION_ID', 'CONVERSATION_STEP', 'TEXT', 'LABEL']]

conversations = df.groupby('CONVERSATION_ID')['TEXT'].apply(' \n'.join).reset_index()
#print(conversations)

output_file = './outputs/call_data_by_conversation.csv'
conversations.to_csv(output_file, index=False)



# output_file = './outputs/call_data_chunked.txt'
# f = open(output_file, 'a')

# for index, row in df_small.iterrows():
#     f.write(f'{row["CONVERSATION_STEP"]}. {row["TEXT"]}\n')

# f.close()