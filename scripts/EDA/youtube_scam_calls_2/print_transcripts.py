import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv("src/ml_scam_classification/data/youtube_scam_calls_2/extracted_features/transcripts.csv")

    print()
    print("_____________________________________________________________________________")
    print("|                                                                           |")
    print("|  Printing examples of transcripts from dataset: \"Youtube Scam Calls 2\"    |")
    print("|___________________________________________________________________________|")
    print()

    for i in range(3):
        print()
        print(f"- - - TRANSCRIPT EXAMPLE {i + 1}: - - -")
        print()
        print(df["dialogue"][i][:300] + "...")
        print("      ... (TRUNCATED)")
        print()
        print()

    print(f"Total transcripts: {len(df)}")
