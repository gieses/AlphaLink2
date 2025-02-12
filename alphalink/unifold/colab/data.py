import hashlib
import os
from typing import Dict, List, Sequence, Tuple, Union, Any, Optional


from alphalink.unifold.data import residue_constants, protein
from alphalink.unifold.msa.utils import divide_multi_chains
from alphalink.unifold.dataset import load_and_process, UnifoldDataset
from alphalink.unifold.symmetry import load_and_process_symmetry

import numpy as np
from Bio import SeqIO
import re
import random
import hashlib

def load_crosslinks(fname):
  links = np.loadtxt(fname,dtype=str)

  if len(links.shape) == 1:
      links = np.array([links])

  crosslinks = {}

  for i,chain1,j,chain2,fdr in links:
      i = int(i)
      j = int(j)
      fdr = float(fdr)
      if not chain1 in crosslinks:
          crosslinks[chain1] = {}
      if not chain2 in crosslinks[chain1]:
          crosslinks[chain1][chain2] = []

      crosslinks[chain1][chain2].append((i-1,j-1,fdr))

  return crosslinks


def load_fasta(fname,jobname):
  def add_hash(x,y):
      return x+"_"+hashlib.sha1(y.encode()).hexdigest()[:5]

  input_sequences = []
  descriptions = []
  for seq in SeqIO.parse(fname, 'fasta'):
      input_sequences.append(str(seq.seq))
      descriptions.append(seq.description)

  basejobname = "".join(input_sequences)
  basejobname = re.sub(r'\W+', '', basejobname)
  target_id = add_hash(jobname, basejobname)

  descriptions = ['>'+target_id+' chain '+d for d in descriptions]

  return input_sequences, descriptions



def clean_and_validate_sequence(
    input_sequence: str, min_length: int, max_length: int) -> str:
  """Checks that the input sequence is ok and returns a clean version of it."""
  # Remove all whitespaces, tabs and end lines; upper-case.
  clean_sequence = input_sequence.translate(
      str.maketrans('', '', ' \n\t')).upper()
  aatypes = set(residue_constants.restypes)  # 20 standard aatypes.
  if not set(clean_sequence).issubset(aatypes):
    raise ValueError(
        f'Input sequence contains non-amino acid letters: '
        f'{set(clean_sequence) - aatypes}. AlphaFold only supports 20 standard '
        'amino acids as inputs.')
  if len(clean_sequence) < min_length:
    raise ValueError(
        f'Input sequence is too short: {len(clean_sequence)} amino acids, '
        f'while the minimum is {min_length}')
  if len(clean_sequence) > max_length:
    raise ValueError(
        f'Input sequence is too long: {len(clean_sequence)} amino acids, while '
        f'the maximum is {max_length}. You may be able to run it with the full '
        f'Uni-Fold system depending on your resources (system memory, '
        f'GPU memory).')
  return clean_sequence


def validate_input(
    input_sequences: Sequence[str],
    symmetry_group: str,
    min_length: int,
    max_length: int,
    max_multimer_length: int) -> Tuple[Sequence[str], bool]:
  """Validates and cleans input sequences and determines which model to use."""
  sequences = []

  for input_sequence in input_sequences:
    if input_sequence.strip():
      input_sequence = clean_and_validate_sequence(
          input_sequence=input_sequence,
          min_length=min_length,
          max_length=max_length)
      sequences.append(input_sequence)
  
  if symmetry_group != 'C1':
    if symmetry_group.startswith('C') and symmetry_group[1:].isnumeric():
      print(f'Using UF-Symmetry with group {symmetry_group}. If you do not '
            f'want to use UF-Symmetry, please use `C1` and copy the AU '
            f'sequences to the count in the assembly.')
      is_multimer = (len(sequences) > 1)
      return sequences, is_multimer, symmetry_group
    else:
      raise ValueError(f"UF-Symmetry does not support symmetry group "
                       f"{symmetry_group} currently. Cyclic groups (Cx) are "
                       f"supported only.")

  elif len(sequences) == 1:
    print('Using the single-chain model.')
    return sequences, False, None

  elif len(sequences) > 1:
    total_multimer_length = sum([len(seq) for seq in sequences])
    if total_multimer_length > max_multimer_length:
      raise ValueError(f'The total length of multimer sequences is too long: '
                       f'{total_multimer_length}, while the maximum is '
                       f'{max_multimer_length}. Please use the full AlphaFold '
                       f'system for long multimers.')
    print(f'Using the multimer model with {len(sequences)} sequences.')
    return sequences, True, None

  else:
    raise ValueError('No input amino acid sequence provided, please provide at '
                     'least one sequence.')


def load_feature_for_one_target(
    config, data_folder, seed=0, is_multimer=False, use_uniprot=False, symmetry_group=None,
):
    if not is_multimer:
        uniprot_msa_dir = None
        sequence_ids = ["A"]
        if use_uniprot:
            uniprot_msa_dir = data_folder

    else:
        uniprot_msa_dir = data_folder
        sequence_ids = open(os.path.join(data_folder, "chains.txt")).readline().split()
    
    batch, _ = load_and_process(
        config=config.data,
        mode="predict",
        seed=seed,
        batch_idx=None,
        data_idx=0,
        is_distillation=False,
        crosslinks='crosslinks.pkl.gz',
        sequence_ids=sequence_ids,
        monomer_feature_dir=data_folder,
        uniprot_msa_dir=uniprot_msa_dir,
    )

    batch = UnifoldDataset.collater([batch])
    return batch
