# (C) Copyright 2025, SECO Mind Srl
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import sys
from pathlib import Path

from colored import fore, stylize

from .interface import convert_interface_from_json_to_c

DEFAUL_C_FILE_NAME = "generated_interfaces"


def collect_json_files(dirs: list[Path], files: list[Path]) -> list[Path]:
    """
    Collects JSON files from specified directories and individual file paths.

    Parameters
    ----------
    dirs : list[Path]
        List of directories to search for JSON files.
    files : list[Path]
        List of individual JSON file paths.

    Returns
    -------
    list[Path]
        A sorted list of unique absolute paths to JSON interface files.
    """
    collected_files = set()

    for d in dirs:
        if not d.is_dir():
            print(stylize(f"Warning: Input directory not found: {d}", fore("yellow")))
            continue
        for ifile in d.iterdir():
            if ifile.suffix == ".json" and ifile.is_file():
                collected_files.add(ifile.resolve())

    for f in files:
        if not f.is_file() or f.suffix != ".json":
            print(stylize(f"Warning: Input file not found or not a JSON: {f}", fore("yellow")))
            continue
        collected_files.add(f.resolve())

    return sorted(list(collected_files))


def wrtite_header_and_source(
    in_header: str,
    in_source: str,
    out_header_dir: Path,
    out_source_dir: Path,
    out_base_name: str,
    check: bool,
):
    """
    Writes the generated C header and source strings to files, handling directories and checks.

    Parameters
    ----------
    in_header : str
        The generated C header file content.
    in_source : str
        The generated C source file content.
    out_header_dir : Path
        Folder where the generated .h file will be saved.
    out_source_dir : Path
        Folder where the generated .c file will be saved.
    out_base_name : str
        Base name for the generated .h and .c files.
    check : bool
        Check if previously generated interfaces are up to date.
    """
    out_header = out_header_dir.joinpath(f"{out_base_name}.h")
    out_source = out_source_dir.joinpath(f"{out_base_name}.c")

    if check:
        if not out_header_dir.exists() or not out_source_dir.exists():
            print(stylize("Check failed: output directories do not exist", fore("yellow")))
            sys.exit(1)

        if not out_header.exists():
            print(stylize(f"Check failed: missing header file '{out_header}'", fore("yellow")))
            sys.exit(1)

        with open(out_header, "r", encoding="utf-8") as out_header_fp:
            if out_header_fp.read() != in_header:
                print(stylize(f"Check failed: header '{out_header}' is outdated", fore("yellow")))
                sys.exit(1)

        if not out_source.exists():
            print(stylize(f"Check failed: missing source file '{out_source}'", fore("yellow")))
            sys.exit(1)
        with open(out_source, "r", encoding="utf-8") as out_source_fp:
            if out_source_fp.read() != in_source:
                print(stylize(f"Check failed: source '{out_source}' is outdated", fore("yellow")))
                sys.exit(1)

        print(stylize("Check passed: Generated files are up to date.", fore("green")))
    else:
        if not out_header_dir.exists():
            os.makedirs(out_header_dir)
        if not out_source_dir.exists():
            os.makedirs(out_source_dir)

        with open(out_header, "w", encoding="utf-8") as out_header_fp:
            out_header_fp.write(in_header)
        print(stylize(f"Generated header: {out_header}", fore("green")))

        with open(out_source, "w", encoding="utf-8") as out_source_fp:
            out_source_fp.write(in_source)
        print(stylize(f"Generated source: {out_source}", fore("green")))


def convert_json_interfaces(
    json_dirs: list[Path] | None = None,
    json_files: list[Path] | None = None,
    output_header_dir: Path = Path(".").resolve(),
    output_source_dir: Path = Path(".").resolve(),
    output_name: str = DEFAUL_C_FILE_NAME,
    check: bool = False,
):
    """
    Handles the core logic for collecting JSON files, converting them to C interfaces,
    and writing the output files.

    Parameters
    ----------
    json_dirs : list[Path]
        One or more directories to search for interface .json files.
        Defaults to an empty list. If both `json_dirs` and `json_files` are empty,
        `json_dirs` will be set to `[current working directory]`.
    json_files : list[Path]
        One or more specific interface .json files to include.
        Defaults to an empty list.
    output_header_dir : Path
        Directory where the generated C header (.h) file will be stored.
        Defaults to the current working directory.
    output_source_dir : Path
        Directory where the generated C source (.c) file will be stored.
        Defaults to the current working directory.
    output_name : str
        Base name for the generated .h and .c files.
        Defaults to 'generated_interfaces'.
    check : bool
        Check if previously generated interfaces are up to date.
        Defaults to False.
    """
    json_dirs = json_dirs if json_dirs is not None else []
    json_files = json_files if json_files is not None else []

    if (json_dirs == []) and (json_files == []):
        json_dirs = [Path(".").resolve()]

    if not (all_json_files := collect_json_files(json_dirs, json_files)):
        print(stylize("No JSON interface files found to convert. Exiting.", fore("yellow")))
        sys.exit(1)

    header, source = convert_interface_from_json_to_c(all_json_files, output_name)

    wrtite_header_and_source(
        header, source, output_header_dir, output_source_dir, output_name, check
    )


def main():
    """
    Generates C interface definitions from JSON files based on command-line arguments.

    Parses arguments to specify input JSON directories/files, output directories
    for C header/source files, and output file names. Converts JSON interfaces
    to C code and writes them. Includes an option to check if generated files
    are up to date. Exits if no JSON files are found.
    """
    parser = argparse.ArgumentParser(
        description="Generates C interfaces definitions from .json definitions."
    )
    parser.add_argument(
        "-d",
        "--json-dirs",
        nargs="+",
        type=Path,
        default=[],
        help="One or more directories to search for interface .json files.",
    )
    parser.add_argument(
        "-f",
        "--json-files",
        nargs="+",
        type=Path,
        default=[],
        help="One or more specific interface .json files to include.",
    )
    parser.add_argument(
        "--output-header-dir",
        type=Path,
        default=Path(".").resolve(),
        help="Directory where the generated C header (.h) file will be stored. Defaults to current directory.",
    )

    parser.add_argument(
        "--output-source-dir",
        type=Path,
        default=Path(".").resolve(),
        help="Directory where the generated C source (.c) file will be stored. Defaults to current directory.",
    )
    parser.add_argument(
        "-N",
        "--output-name",
        type=str,
        default=DEFAUL_C_FILE_NAME,
        help="Base name for the generated .h and .c files Defaults to 'generated_interfaces'.",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="Check if previously generated interfaces are up to date.",
    )

    args = parser.parse_args()

    convert_json_interfaces(
        json_dirs=args.json_dirs,
        json_files=args.json_files,
        output_header_dir=args.output_header_dir,
        output_source_dir=args.output_source_dir,
        output_name=args.output_name,
        check=args.check,
    )


if __name__ == "__main__":
    main()
