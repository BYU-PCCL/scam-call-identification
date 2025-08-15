from ...project_utils.file_utils import get_dataframe_from_csv_url

def get_world_bank_group_current_demographics():
    url="https://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv"
    return get_dataframe_from_csv_url(url)


def get_current_world_demographics():
    pass

if __name__ == "__main__":
    # load population demographic statistics
    print(get_world_bank_group_current_demographics())