import os, sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

from inference.engine import split_sentences
from argparse import ArgumentParser

from tqdm import tqdm


def read_lines(path):
    with open(path, "r") as f:
        lines = f.readlines()
    return lines


def create_txt(outFile, lines):
    add_newline = not "\n" in str(lines[0])
    outfile = open("{0}".format(outFile), "w")
    for line in lines:
        if add_newline:
            outfile.write(line + "\n")
        else:
            outfile.write(line)

    outfile.close()


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--mode",
        type=str,
        default="split",
        help="whether to split or merge the input text file",
        choices=["split", "merge"],
    )
    parser.add_argument(
        "--lang",
        type=str,
        default=None,
        help="language of the input text file",
    )
    parser.add_argument(
        "--input_file",
        type=str,
        required=True,
        help="the input text file",
    )
    parser.add_argument(
        "--index_file",
        type=str,
        default=None,
        help="File storing the indexes of sentencs. In case of split, this file will be created. In case of merge, this will be given by the user",
    )

    args = parser.parse_args()

    if args.mode == "split":
        assert args.lang is not None, "Please provide the language of the input file"

        if args.index_file is None:
            args.index_file = f"{args.input_file}.indexes"

        indexes = []

        lines = read_lines(args.input_file)
        split_lines = []
        for idx, line in enumerate(tqdm(lines)):
            sentences = split_sentences(line, language=args.lang)
            indexes.extend([str(idx)] * len(sentences))
            split_lines.extend(sentences)

        create_txt(args.index_file, indexes)
        create_txt(f"{args.input_file}.split", split_lines)
    elif args.mode == "merge":
        assert args.index_file is not None, "Please provide the index file"

        indexes = read_lines(args.index_file)
        indexes = list(map(int, indexes))
        lines = read_lines(args.input_file)
        new_lines = []
        merged_line = lines[0].replace("\n", "")
        for idx, line in enumerate(tqdm(lines[1:]), start=1):
            line = line.replace("\n", "")
            if indexes[idx - 1] == indexes[idx]:
                merged_line += line
            else:
                new_lines.append(merged_line)
                merged_line = line

        # last line
        new_lines.append(merged_line)

        create_txt(f"{args.input_file}.merge", new_lines)
    else:
        raise ValueError("Invalid mode")


if __name__ == "__main__":
    main()
