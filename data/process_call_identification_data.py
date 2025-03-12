import pandas as pd

df = pd.read_csv('./data/call_identification.csv')
df = df[['CONVERSATION_ID', 'CONVERSATION_STEP', 'TEXT', 'LABEL']]

conversations = df.groupby('CONVERSATION_ID').agg({
    'TEXT': lambda x: ', \n'.join(x),
    'LABEL': lambda x: ', \n'.join(x)
}).reset_index()

output_file = './data/call_data_by_conversation.csv'
conversations.to_csv(output_file, index=False)
