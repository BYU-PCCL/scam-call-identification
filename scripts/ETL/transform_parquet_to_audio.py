import argparse
from src.ml_scam_classification.utils.file_utils import parquet_to_audio

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Transform Parquet to Audio'
                    )
    
    def add_req_str_arg(parser, flag_str: str):
        parser.add_argument(flag_str, type=str, required=True)

    for flag_str in ['--path_to_parquet', '--output_folder', '--output_file_prefix']:
        add_req_str_arg(parser, flag_str)

    parser.add_argument('--sample_rate', default=44100, type=int, required=False)

    args = parser.parse_args()

    parquet_to_audio(
        path_to_parquet=args.path_to_parquet,
        output_path=args.output_folder,
        output_file_prefix=args.output_file_prefix,
        sample_rate=args.sample_rate
    )
