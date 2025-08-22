import csv
import pandas as pd

from src.general_file_utils.utils.str import format_self_contained_item_pretty, format_title

def assert_is_df(data):
    if not isinstance(data, pd.DataFrame):  # accept subclasses
        raise ValueError(f"Attempted to assert type as df for: {type(data)}")

def write_df_to_csv(path, df):
    assert_is_df(df)
    df.to_csv(path, index=False)

def get_first_row_csv(path, separator=','):
    # robust to quoted fields
    with open(path, 'r', newline='') as file:
        reader = csv.reader(file, delimiter=separator)
        return next(reader, [])

def append_df_rows_to_csv(path_to_csv, df):
    assert_is_df(df)
    # Appends rows without header
    df.to_csv(path_to_csv, mode='a', index=False, header=False)

def print_entries_pretty(
        path=None,
        df=None,
        rows_to_print=5,
        chars_per_row=80,
        space_padding=3,
        values_indentation=12
):
    neither = (path is None) and (df is None)
    both = (path is not None) and (df is not None)

    if neither or both:
        raise ValueError("Provide either a path or a df, but not both.")

    if path is not None:
        df = pd.read_csv(path, nrows=rows_to_print)
    else:
        # limit df to first n rows in memory
        df = df.head(rows_to_print)

    for i, row in df.iterrows():
        print("\n\n" + format_title(f"ROW {i}"))
        for col_name, row_value in row.items():
            print(f"\n      (ROW {i}) - {col_name}")
            print(format_self_contained_item_pretty(
                item=row_value,
                line_width_chars=chars_per_row,
                space_padding=space_padding,
                indent=values_indentation
            ))


if __name__ == "__main__":
    print_entries_pretty(
        df=pd.DataFrame(
            {
                "col1": [
                    "This is the value of column one int he first row. I am making it longer so that I can see how longer values will look in the printout and so I can see if the truncation is working. The structure should allow easy visual parsing of the values in each row, even if the values are very long and wrap to multiple lines.                           Adding spaces, to see what this looks like in the pretty print, to ensure it does not look confusing.                                                                                                        More spaces.                                                                                                                                                                                  a bit more...                                                          ",
                    "This is the value of columnn 1 in the second row. I am making it longer so that I can see how longer values will look in the printout and so I can see if the truncation is working. The structure should allow easy visual parsing of the values in each row, even if the values are very long and wrap to multiple lines.                           Adding spaces, to see what this looks like in the pretty print, to ensure it does not look confusing.                                                                                                        More spaces.                                                                                                                                                                                  a bit more...                                                          ",
                    "This is the value of column 1 in the third row. I am making it longer so that I can see how longer values will look in the printout and so I can see if the truncation is working. The structure should allow easy visual parsing of the values in each row, even if the values are very long and wrap to multiple lines.                           Adding spaces, to see what this looks like in the pretty print, to ensure it does not look confusing.                                                                                                        More spaces.                                                                                                                                                                                  a bit more...                                                          ",
                    "This is the value of column 1 in the fourth row. I am making it longer so that I can see how longer values will look in the printout and so I can see if the truncation is working. The structure should allow easy visual parsing of the values in each row, even if the values are very long and wrap to multiple lines.                           Adding spaces, to see what this looks like in the pretty print, to ensure it does not look confusing.                                                                                                        More spaces.                                                                                                                                                                                  a bit more...                                                          ",
                    "This is the value of column 1 in the fifth row. I am making it longer so that I can see how longer values will look in the printout and so I can see if the truncation is working. The structure should allow easy visual parsing of the values in each row, even if the values are very long and wrap to multiple lines.                           Adding spaces, to see what this looks like in the pretty print, to ensure it does not look confusing.                                                                                                        More spaces.                                                                                                                                                                                  a bit more...                                                          "
                ],
                "col2": [1, 2, 3, 4, 5],
                "col3": ["apple", "orange", "banana", "pomegranate", "kumquat"],
                "col4 is where I am testing a really long column name just to see what will happen if I make it super super super super long and whether or not things will still be visually parsable...": ['a', 'b', 'c', 'd', 'e']
            }
        )
    )