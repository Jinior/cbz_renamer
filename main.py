import argparse
import logging
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple

VALID_SUFFIXES = {".cbz", ".zip"}

logging.basicConfig(level=logging.DEBUG)

def parse_args() -> Tuple[Path, Path, bool, bool]:
    """Parse arguments
    
    Returns:
        A tuple containing:
            The input path
            The output path
            A boolean describing whether to force running, even if this means overwriting existing files
    """
    parser = argparse.ArgumentParser(description="get the input and output path.")
    parser.add_argument(
        "input", metavar="input/path", type=Path, help="path with input cbz files"
    )
    parser.add_argument(
        "output",
        metavar="output/path",
        type=Path,
        help="path to output proccessed cbz files",
    )
    parser.add_argument("-f", action='store_true', help="set flag to force running, even if this means overwriting existing files")
    parser.add_argument("-r", action="store_true", help="set flag to run recursively")

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    force = args.f
    recurse = args.r

    logging.info(f"Using input path: {input_path}")
    logging.info(f"Using output: path {output_path}")
    logging.debug(f"force: {force}")
    logging.debug(f"recurse: {recurse}")

    return input_path, output_path, force, recurse


def validate_input_path() -> bool:
    """Checks if the input path is a valid path

    Returns:
        True: if the input path is a valid path
        False: otherwise
    """
    pass


def validate_output_path(force: bool = False) -> bool:
    """Checks if the output path is a valid path

    Returns:
        True: if the output path is a valid path
        False: otherwise
    """
    pass

def process_path():
    """Run the program on a path

    """

if __name__ == "__main__":
    input_path, output_path, force = parse_args()
    for file in input_path.iterdir():
        # Iterate over all direct children of the input path
        if not file.is_file():
            # If the path is not a file, go to the next file
            logging.debug(f"Not processing path because it is not a file: {}")
            continue
        if not file.suffix.lower() in VALID_SUFFIXES:
            # If the file does not have a valid extension, go to the next file
            logging.debug(f"Not processing path because it does not have a valid extension: {file}")
            logging.debug(f"Valid extensions are: {VALID_SUFFIXES}"
            continue

