"""
Wrapper around the AlphaLink2 pipeline. Performing crosslink generation, MSA and structure prediction with a single
command line call.
"""
import argparse

from tqdm import tqdm

from alphalink.scripts.alphalink_generate_crosslinks import crosslink_parser, main as main_crosslinks
from alphalink.scripts.alphalink_inference import inference_parser, main as main_inference
from alphalink.scripts.alphalink_msa import msa_parser, main as main_msa


def main_parser():
    msa_p = msa_parser()
    inference_p = inference_parser()
    crosslink_p = crosslink_parser()

    combined_parser = argparse.ArgumentParser(description=__doc__)
    combined_parser.add_argument("--output_dir_msa", help="Output directory for the MSA.")
    combined_parser.add_argument("--output_dir_inference", help="Output directory for the predicted PDBs.")
    combined_parser.add_argument("--output_dir", help='', dest=argparse.SUPPRESS)
    combined_parser.add_argument("--crosslinks", help='', dest=argparse.SUPPRESS)

    # Add arguments from the first parser
    for action in msa_p._actions:
        if (
                (not action.option_strings[0] == "-h") and
                (not action.option_strings[0] == "--output_dir")
        ):
            combined_parser._add_action(action)

    # Add arguments from the second parser
    for action in inference_p._actions:
        if (
                (not action.option_strings[0] == "-h") and
                (not action.option_strings[0] == "--output_dir") and
                (not action.option_strings[0] == "--crosslinks")
        ):
            combined_parser._add_action(action)

    for action in crosslink_p._actions:
        if (not action.option_strings[0] == "-h"):
            combined_parser._add_action(action)

    return combined_parser.parse_args()


def main():
    arguments = main_parser()

    pbar = tqdm(total=100)
    print("AlphaLink2: crosslink processing.")
    main_crosslinks(arguments)
    pbar.update(33)

    print("AlphaLink2: MSA computation.")
    arguments.output_dir = arguments.output_dir_msa
    main_msa(arguments)
    pbar.update(33)

    print("AlphaLink2: PDB inference.")
    arguments.output_dir = arguments.output_dir_inference
    arguments.crosslinks = arguments.output
    main_inference(arguments)
    pbar.update(33)
    print("AlphaLink2 is done.")


if __name__ == '__main__':
    main()
