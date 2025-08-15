import pandas as pd
import json

with open('data/features.json', 'r') as file:
    features = json.load(file)

lables_caller = []
labels_recipient = []
for key in features.keys():
    for letter in features[key]['Labels']:
        lables_caller.append("caller_" + key + letter)
        labels_recipient.append("recipient_" + key + letter)


labels = lables_caller + labels_recipient
df = pd.DataFrame(columns=labels)



print(df)