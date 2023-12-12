# AlphaLink2: Modelling protein complexes with crosslinking mass spectrometry and deep learning

Code for the paper ["Modelling protein complexes with crosslinking mass spectrometry and deep learning"](https://www.biorxiv.org/content/10.1101/2023.06.07.544059v2). We extend [AlphaLink](https://github.com/lhatsk/AlphaLink) to protein complexes. AlphaLink2 is based on [Uni-Fold](https://github.com/dptech-corp/Uni-Fold) and integrates crosslinking MS data directly into Uni-Fold. The current [networks](https://doi.org/10.5281/zenodo.8007238) were trained with simulated SDA data (25 Å Cα-Cα).

![case](./img/figure_github.png)
<center>
<small>
Figure 1. Prediction of RpoA-RpoC with real DSSO crosslinking MS data. Satisfied crosslinks are shown in blue (< 30 Å Cα-Cα) and violated crosslinks in red (> 30 Å Cα-Cα).
</small>
</center>

## Running AlphaLink in ColabFold

The AlphaLink2 ColabFold can be found [here](https://colab.research.google.com/github/Rappsilber-Laboratory/AlphaLink2/blob/main/notebooks/alphalink2.ipynb).

## Crosslink input format

AlphaLink takes as input a python dictionary of dictionaries with a list of crosslinked residue pairs with a false-discovery rate (FDR). That is, for inter-protein crosslinks A->B 1,50 and 30,80 and an FDR=20%, the input would look as follows:

```
In [6]: crosslinks
Out[6]: {'A': {'B': [(1, 50, 0.2), (30, 80, 0.2)]}}
```

Intra-protein crosslinks would go from A -> A

```
In [6]: crosslinks
Out[6]: {'A': {'A': [(5, 20, 0.2)]}}
```

The dictionaries are 0-indexed, i.e., residues start from 0.


You can create the dictionaries with the generate_crosslink_pickle.py script by running

```
python generate_crosslink_pickle.py --csv crosslinks.csv --output crosslinks.pkl.gz
```

The crosslinks CSV has the following format (residues are 1-indexed).

residueFrom chain1 residueTo chain2 FDR

Example:

```
1 A 50 B 0.2
5 A 5 A 0.1
```

The chain IDs A..Z+ designate all unique chains (based on sequence identity) in the FASTA file, enumerated by order of appearance. That is, the first chain gets the identifier A, the second chain the identifier B and so on. In case, for example, the second chain is a copy of the first chain, it will also be assigned chain A. After feature generation, the chain assignment can be found in the output folder in the file "chain_id_map.json" and the final composition (denoting copies) in the file "chains.txt". Changing "chains.txt" is an easy way to test different compositions and doesn't require regenerating the features.

## Installation and preparations

To install AlphaLink, clone the repository and run the command below (linux). It is highly recommended to install mamba
before creating the environment. For other systems, build [Uni-Core from scratch.](https://github.com/dptech-corp/Uni-Core#installation).
The installation takes less than an hour. Successfull installation will also create the command line tools to run
AlphaLink (see below).

```bash
# get forked repo
git clone https://github.com/gieses/AlphaLink2
# optional
conda install -c conda-forge mamba -y
# alphalink env
mamba env create --file environment.yml --prefix ENV_PATH
```

### Install AlphaFold - necessary for relax

```bash
# download folding resources
wget --no-check-certificate https://git.scicore.unibas.ch/schwede/openstructure/-/raw/7102c63615b64735c4941278d92b554ec94415f8/modules/mol/alg/src/stereo_chemical_props.txt

# copy stereo_chemical_props.txt to the alphafold conda folder
cp stereo_chemical_props.txt $CONDA_PREFIX/lib/python3.10/site-packages/`ls $CONDA_PREFIX/lib/python3.10/site-packages/ | grep alphafold`/alphafold/common/

cd ..
```

### Databases

If you are missing the databases for MSA generation, you can download them with the following script:

```
bash scripts/download/download_all_data.sh /path/to/database/directory full_dbs
```
or for the smaller databases:

```
bash scripts/download/download_all_data.sh /path/to/database/directory reduced_dbs
```

They require up to 3TB of storage.

## Model weights
	
The model weights are deposited here: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8007238.svg)](https://doi.org/10.5281/zenodo.8007238)

## Running AlphaLink

After set up, AlphaLink can be run with individual scripts or as a workflow. To simplify the command arguments,
specify the two environment variables in your shell (or keep providing them on the command line):

```bash
export AFLINK2_PARAMS="/path/to/weights/alphalink2_params/AlphaLink-Multimer_SDA_v3.pt"
export AFLINK2_DATABASE_DIR="/path/to/openfold/data"
```

```bash
# single commands
alphalink2-crosslinks --csv data/H1142.csv --output data/H1142.pkl
alphalink2-msa \
--fasta_path data/H1142.fasta \
--output_dir data/alphalink_msas/ \
--max_template_date 2022-05-01 \
--n_cpu 255
alphalink2-inference \
--model_device cuda:0 \
--data_dir data/alphalink_msas/H1142 \
--crosslinks data/H1142.pkl \
--bf16 \
--use_uniprot \
--save_raw_output \
--relax \
--output_dir data/alphalink_predictions/

# workflow command
alphalink2-wf --csv data/H1142.csv --output data/H1142.pkl \
--fasta_path data/H1142.fasta \
--output_dir results_wf/alphalink_msas/ \
--max_template_date 2022-05-01 \
--n_cpu 255 \
--model_device cuda:0 \
--data_dir results_wf/alphalink_msas/ \
--bf16 \
--use_uniprot \
--save_raw_output --relax \
--output_dir results_wf/alphalink_predictions/ \
--target_name H1142
````

Output folder will contain the relaxed and unrelaxed PDBs and a pickle file with the PAE map.

### Hardware requirements
GPU, ideally NVIDIA V100 and upwards. A100+ can make use of bfloat16 to predict larger targets.

 
## Citing this work

If you use the code, the model parameters, or the released data of AlphaLink2, please cite

    
```bibtex
@article {Stahl2023,
	author = {Kolja Stahl and Oliver Brock and Juri Rappsilber},
	title = {Modelling protein complexes with crosslinking mass spectrometry and deep learning},
	elocation-id = {2023.06.07.544059},
	year = {2023},
	doi = {10.1101/2023.06.07.544059},
	publisher = {Cold Spring Harbor Laboratory},
	abstract = {Scarcity of structural and evolutionary information on protein complexes poses a challenge to deep learning-based structure modelling. We integrated experimental distance restraints obtained by crosslinking mass spectrometry (MS) into AlphaFold-Multimer, by extending AlphaLink to protein complexes. Integrating crosslinking MS data substantially improves modelling performance on challenging targets, by helping to identify interfaces, focusing sampling, and improving model selection. This extends to single crosslinks from whole-cell crosslinking MS, suggesting the possibility of whole-cell structural investigations driven by experimental data.Competing Interest StatementThe authors have declared no competing interest.},
	URL = {https://www.biorxiv.org/content/early/2023/06/09/2023.06.07.544059},
	eprint = {https://www.biorxiv.org/content/early/2023/06/09/2023.06.07.544059.full.pdf},
	journal = {bioRxiv}
}
```

Any work that cites AlphaLink2 should also cite AlphaFold and Uni-Fold.

## Acknowledgements

AlphaLink2 is based on [Uni-Fold](https://github.com/dptech-corp/Uni-Fold) and fine-tunes the network weights of [AlphaFold](https://github.com/deepmind/alphafold/).

### Code License

While AlphaFold's and, by extension, Uni-Fold's source code is licensed under the permissive Apache License, Version 2.0, DeepMind's pre-trained parameters fall under the CC BY 4.0 license. Note that the latter replaces the original, more restrictive CC BY-NC 4.0 license as of January 2022

### Model Parameters License

The AlphaLink parameters are made available under the terms of the Creative Commons Attribution 4.0 International (CC BY 4.0) license. You can find details at: https://creativecommons.org/licenses/by/4.0/legalcode

### Third-party software

Use of the third-party software, libraries or code referred to in the [Acknowledgements](README.md/#acknowledgements) section above may be governed by separate terms and conditions or license provisions. Your use of the third-party software, libraries or code is subject to any such terms and you should check that you can comply with any applicable restrictions or terms and conditions before use.
