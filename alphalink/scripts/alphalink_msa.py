"""
alphalink2-msa - generate MSAs for constrained structure generation with AlphaFold.

if not provided the database dir is attempted to be retrieved from the env variable 'AFLINK2_DATABASE_DIR'
Example:
        $ alphalink2-msa --fasta_path fasta_test/H1142.fasta \
            --output_dir fata_test/alphalink_msas/ \
            --database_dir path_to_openfold/database/ \
            --max_template_date 2022-05-01 \
            --n_cpu 255

"""
import argparse
import os
import subprocess
from argparse import RawTextHelpFormatter
from pathlib import Path

import alphalink


def run_homo_search(*,
                    fasta_path,
                    max_template_date,
                    database_dir,
                    output_dir,
                    precomputed_msa: bool = True,
                    verbose: bool = True,
                    n_cpu: int = 8):
    # Construct the command to call the homo_search.py script
    database_dir_path = Path(database_dir)

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    command = [
        "python",
        str(Path(alphalink.__file__).parent / "unifold" / "homo_search.py"),
        f"--fasta_path={str(fasta_path)}",
        f"--max_template_date={str(max_template_date)}",
        f"--output_dir={str(output_dir)}",
        f"--uniref90_database_path={str(database_dir_path / 'uniref90' / 'uniref90.fasta')}",
        f"--mgnify_database_path={str(database_dir_path / 'mgnify' / 'mgy_clusters_2018_12.fa')}",
        f"--bfd_database_path={str(database_dir_path / 'bfd' / 'bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt')}",
        f"--uniclust30_database_path={str(database_dir_path / 'uniclust30' / 'uniclust30_2018_08' / 'uniclust30_2018_08')}",
        f"--uniprot_database_path={str(database_dir_path / 'uniprot' / 'uniprot.fasta')}",
        f"--pdb_seqres_database_path={str(database_dir_path / 'pdb_seqres' / 'pdb_seqres.txt')}",
        f"--template_mmcif_dir={str(database_dir_path / 'pdb_mmcif' / 'mmcif_files')}",
        f"--obsolete_pdbs_path={str(database_dir_path / 'pdb_mmcif' / 'obsolete.dat')}",
        f"--use_precomputed_msas={str(precomputed_msa)}",
        f"--n_cpu={n_cpu}"
    ]
    if verbose:
        command_str = " ".join(command)
        print(command_str)

    # Use subprocess.Popen to call the script
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("starting sequence search (this might take a while)...")
    stdout, stderr = process.communicate()
    print("Done!")

    # Check if the command was successful
    if process.returncode == 0:
        print("homo_search.py executed successfully.")
        print("Output:")
        print(stdout)
    else:
        print("Error running homo_search.py:")
        print("Error message:")
        print(stderr)


def msa_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)

    parser.add_argument("--fasta_path", required=True, help="Path to the FASTA file")
    parser.add_argument("--output_dir", required=True, help="Base output directory")
    parser.add_argument("--database_dir", required=False, default=None, help="Path to obsolete PDBs file")
    parser.add_argument("--max_template_date", default=None, required=True,
                        type=str, help="Max template date to consider (year-month-day, e.g. 2023-10-01)")
    parser.add_argument('--n_cpu', default=8, type=int, help="Number of CPUs to use. Default is 8.")

    return parser


def main(args=None):
    if not args:
        args = msa_parser().parse_args()

    database_dir = os.getenv("AFLINK2_DATABASE_DIR", args.database_dir)
    if database_dir is None:
        raise ValueError("AFLINK2_DATABASE_DIR is not set and database_dir argument not provided")

    run_homo_search(fasta_path=args.fasta_path,
                    output_dir=args.output_dir,
                    database_dir=database_dir,
                    max_template_date=args.max_template_date,
                    n_cpu=args.n_cpu)


if __name__ == "__main__":
    main()
