import argparse
import logging
import zipfile
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description="Get the input and output path.")
parser.add_argument(
    "input", metavar="input/path", type=Path, help="path with input cbz files"
)
parser.add_argument(
    "output",
    metavar="output/path",
    type=Path,
    help="path to output proccessed cbz files",
)
parser.add_argument("-f", action='store_true')

args = parser.parse_args()

input_path = args.input
output_path = args.output
force = args.f

logging.info(f"Using input path: {input_path}")
logging.info(f"Using output: path {output_path}")
logging.debug(f"force: {args.f}")


