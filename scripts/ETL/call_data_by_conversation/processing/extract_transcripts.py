import pandas as pd

from src.ml_scam_classification.utils.file_utils import make_dir_rec

if __name__ == "__main__":
    df = pd.read_csv('src/ml_scam_classification/data/call_data_by_conversation/raw_data/call_identification.csv')

    # made this for checking data format and printing entire values (no truncation)
    # in this case, used for checking data to make sure it got processed correctly (each instance is a conversation)

    def print_df_values(df):
        for col in df.columns:
            print(f"\nCOLUMN: {col}")
            for i in range(10):
                print(f"    {col} at i={i}: {df[[col]][col].iloc[i]}")

    # print_df_values(df)

    df_conversations = (
        df[['CONVERSATION_ID', 'TEXT']]
        .groupby('CONVERSATION_ID')['TEXT']
        .apply(' '.join)  # Separator between utterances
        .reset_index()
    )[['TEXT']].rename(columns={'TEXT': 'transcripts'})

    # Regex pattern to match "[Step: n]" where n is any number
    label_pattern = r'\[Step: \d+\]'

    # Removes labels from label pattern
    df_conversations['transcripts'] = (
        df_conversations['transcripts']
        .str.replace(label_pattern, '', regex=True) # remove labels of parts of conversation, llm will re-label
        .str.replace("[Your Name]", "[_name]") # more generic name placeholder
        .str.replace("  ", " ") # no double spaces
        )

    #print_df_values(df_conversations)
    
    output_file = 'src/ml_scam_classification/data/call_data_by_conversation/processed/call_data_by_conversation_conv_only.csv'

    # create dirs along path
    make_dir_rec(output_file)

    df_conversations.to_csv(output_file, index=False)
