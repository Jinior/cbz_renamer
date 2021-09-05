import argparse
import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Optional, Tuple

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
    parser.add_argument(
        "-f",
        action="store_true",
        help="set flag to force running, even if this means overwriting existing files",
    )
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

    validate_input_path(input_path, recurse)

    return input_path, output_path, force, recurse


def validate_input_path(path: Path, recurse: bool) -> bool:
    """Checks if the input path is a valid path

    Args:
        path: the input path to validate
        recurse: whether to recurse into subdirectories
    Returns:
        True: if the input path is a valid path
        False: otherwise
    """
    if not path.is_dir():
        # If the path is not a directory it is invalid
        logging.debug(f"Rejecting input path because it is not a directory: {path}")
        return False
    if not any(path.iterdir()):
        # If the path is empty invalidate it
        logging.debug(f"Rejecting input path because it is empty: {path}")

    # check for a valid file to process
    for sub_path in path.iterdir():
        if sub_path.is_dir() and recurse:
            # If a path is a directory and we recurse, do so
            logging.debug(f"Validating input sub-path: {sub_path}")
            if validate_input_path(sub_path, recurse):
                # if the sub_path contains valid files so does the original path
                return True
        else:
            # If the path is a file
            if sub_path.suffix in VALID_SUFFIXES:
                logging.debug(
                    f"Accepting input path because a valid file was found: {sub_path}"
                )
                return True
    # No valid files where found
    logging.debug(
        f"Rejecting input path because it contains no files with a valid suffix: {path}"
    )
    return False


def validate_output_path(path: Path, force: bool) -> bool:
    """Checks if the output path is a valid path


    Args:
        path: the output path to check
    Returns:
        True: if the output path is a valid path
        False: otherwise
    """
    if not path.exists():
        logging.debug("Accepting output path because it does not yet exist")
        return True
    if not any(path.iterdir()):
        logging.debug("Accepting output path because it is empty")
        return True
    if force:
        logging.warning(
            "Output path exists and has files. Accepting anyway because of the froce flag"
        )
        return True
    return False


def process_path(input_path: Path, output_path: Path, force: bool, recurse: bool):
    """Run the program on a path"""
    for file in input_path.iterdir():
        # Iterate over all direct children of the input path
        if not file.is_file():
            # If the path is not a file, go to the next file
            if recurse and file.is_dir():
                # If the path is a directory and we need to recurse, recurse
                logging.debug(f"recursing into directory: {file}")
                process_path(file, output_path, force, recurse)
            else:
                logging.debug(f"Not processing path because it is not a file: {file}")
                continue
        if not file.suffix.lower() in VALID_SUFFIXES:
            # If the file does not have a valid extension, go to the next file
            logging.debug(
                f"Not processing path because it does not have a valid extension: {file}"
            )
            logging.debug(f"Valid extensions are: {VALID_SUFFIXES}")
            continue
        output_file = output_path.joinpath(file.name)
        if output_file.is_file() and not force:
            # If the output file already exists
            logging.debug(
                f"Not processing file '{file}' because the output file already exists: {output_file}"
            )
            continue
        output_path.mkdir(
            exist_ok=True, parents=True
        )  # If the output_dir does not exist, create it
        rebuild_cbz(file, output_file)


def rebuild_cbz(input_file: Path, output_file: Path):
    """Create a new cbz file with the new naming structure

    Args:
        input_file: The original cbz file
        output_file: The new file to write to
    """
    # TODO: Write directly from zip to zip and skip the temp directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        with zipfile.ZipFile(input_file) as original_cbz:
            original_cbz.extractall(tmp_dir)
        mapping = build_rename_mapping(tmp_dir)
        with zipfile.ZipFile(output_file, mode="w") as new_cbz:
            for (
                file,
                new_path,
            ) in mapping.items():  # TODO: check if we need to set a compression level
                new_cbz.write(
                    file, arcname=new_path
                )  # TODO: check if we need to set a compression level


def build_rename_mapping(path: Path, prefix: Optional[Path] = None) -> Dict[Path, Path]:
    """Returns a map with the original path/filenames as a key and the new path/filenames as value.
    The purpose of this function is to provide the new file structure of the cbz.

    Args:
        path: the (sub)path to process renames of)
        prefix: the part of theopath to ignore when renaming
    """
    if prefix is None:
        # if no prefix is given, assume the path is the prefix
        prefix = path
    mapping = dict()
    for sub_path in path.iterdir():
        if sub_path.is_dir():
            # if the sub-path is a directory, process it recursively
            mapping.update(build_rename_mapping(sub_path, prefix))
            continue
        if not sub_path.is_file():
            # if the sub_path is not a file or directory, skip it
            continue
        # create a mapping from the original path to a single filename with the
        zip_path = sub_path.relative_to(
            prefix
        )  # The path the file had inside the zipfile
        # map the original path to a new path where entire zip_path is inside the filename
        mapping[sub_path] = zip_path.joinpath(
            str(zip_path.as_posix()).replace("/", "_")
        )
    return mapping


if __name__ == "__main__":
    input_path, output_path, force, recurse = parse_args()
    process_path(input_path, output_path, force, recurse)
