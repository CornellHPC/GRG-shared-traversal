# Cheaper by the Batch: Shared Traversal for Genotype Graph Editing

This repository collects the code artifacts for "Cheaper by the Batch: Shared Traversal for Genotype Graph Editing".

The core implementation is in [`grgl/`](grgl/), included as a submodule from [CornellHPC/grgl](https://github.com/CornellHPC/grgl). The polarization workflow used in the evaluation is in [`grapp/`](grapp/), included as a submodule from [CornellHPC/grapp](https://github.com/CornellHPC/grapp).

## Layout

- `grgl/`: core GRG library and batched mutation mapping implementation.
- `grapp/`: Python command-line workflow for allele polarization using GRGL.
- `generate_data.py`: simulated GRG and ancestral FASTA generation for polarization experiments.

## Setup

Initialize the pinned submodules:

```bash
git submodule update --init --recursive
```

Create one Python environment and install both projects into it. Install GRGL first so GRAPP uses the matching `pygrgl` build:

```bash
python3 -m venv .venv
source .venv/bin/activate
cd grgl
python setup.py bdist_wheel
python -m pip install --force-reinstall dist/*.whl
cd ..
cd grapp
python -m pip install .
cd ..
```

## Generate Simulated Data

After completing setup, install the simulation dependencies in the same environment:

```bash
python -m pip install stdpopsim tskit
```

Run `generate_data.py` from the repository root, with `stdpopsim` and `grg` available on your `PATH`. This example generates a small dataset using the human `OutOfAfrica_2T12` model and samples from its `EUR` population:

```bash
python generate_data.py --out data/example \
  --samples 100 --length 100000 --flip-pct 0.1 --seed 1
```

Options:

- `--out` is required and selects the output directory.
- `--samples` is passed to stdpopsim as `EUR:<samples>` (default: `200000`).
- `--length` sets the simulated sequence length in base pairs (default: `5000000`).
- `--chromosome` selects a full chromosome, such as `chr22`, and overrides `--length`.
- `--genetic-map` selects a stdpopsim map, such as `HapMapII_GRCh38`, and requires `--chromosome`.
- `--flip-pct` is the fraction of eligible sites whose ancestral allele is replaced with the derived allele in `fake.fa`, between 0 and 1 (default: `0.1`, or 10%).
- `--seed` controls simulation and flipped-site selection (default: `1`).
- `--work-dir` optionally puts the generated data in `<work-dir>/<out-directory-name>`. Logs and the summary remain under `--out`. Without this option, all files go under `--out`.

For example, to simulate a full chromosome with a genetic map and store large files separately:

```bash
python generate_data.py --out results/chr22 --work-dir scratch \
  --samples 100 --chromosome chr22 --genetic-map HapMapII_GRCh38
```

The generated data includes `sim.trees`, the converted `polarized.grg`, `true.fa` with the simulated ancestral alleles, `fake.fa` with the selected flips, and `flips.tsv` with flipped positions, alleles, and allele counts. FASTAs contain alleles only at eligible polymorphic A/C/G/T sites with one mutation and a positive integer position; other positions are `N`. The script also writes `summary.tsv` with parameters, counts, and file paths, plus command output in `logs/popsim.log` and `logs/convert.log`.

Use the fake ancestral FASTA to introduce polarization errors, then the true FASTA to restore the ancestral orientation:

```bash
grapp polarize data/example/polarized.grg data/example/fake.fa \
  -o data/example/depolarized.grg --keep-no-match
grapp polarize data/example/depolarized.grg data/example/true.fa \
  -o data/example/repolarized.grg --keep-no-match
```

`--keep-no-match` retains mutations at positions marked `N` in the generated FASTAs.

## Polarization Workflow

Polarize a GRG with an ancestral FASTA:

```bash
grapp polarize <input.grg> <ancestral.fa> -o <polarized.grg>
```

The FASTA must contain exactly one contig. Positions in the GRG are interpreted against that full ancestral sequence, so do not pass a sliced FASTA whose coordinates have been shifted.

Useful options:

```bash
grapp polarize <input.grg> <ancestral.fa> \
  -o <polarized.grg> \
  --map-batch-size 100 \
  --jobs 8 \
  --split-threshold 1000000 \
  --temp-dir <tmp-dir>
```

- `--map-batch-size` controls how many flipped mutations are processed per graph traversal; larger values can improve throughput but use more memory.
- `--jobs` runs split GRG parts in parallel.
- `--split-threshold` controls the base-pair range size used when splitting.
- `--temp-dir` stores split GRGs and intermediate polarized parts.
- `--keep-no-match` keeps mutations that cannot be matched to the ancestral sequence instead of dropping them.

For lower-level GRGL usage, see [`grgl/README.md`](grgl/README.md). For the full GRAPP command reference, see [`grapp/README.md`](grapp/README.md).

## Citation

If you use the mutation mapping features, please cite our preprint "Cheaper by the Batch: Shared Traversal for Genotype Graph Editing": 

```
@article{li2026graph,
  title={Cheaper by the Batch: Shared Traversal for Genotype Graph Editing},
  author={Li, Aaron and Li, Yifan and DeHaas, Drew and Guidi, Giulia},
  journal={arXiv preprint arXiv:2608.26488},
  year={2026}
}
```

## Acknowledgments

The authors thank the members of the [ALPS Lab at Cornell University](https://giuliaguidi.github.io/hpcgroup/) for their feedback and discussion.

This research used resources from the National Energy Research Scientific Computing Center, a DOE Office of Science User Facility supported by the Office of Science of the U.S. Department of Energy under Contract No. DE-AC02-05CH11231, using NERSC award ASCR-ERCAP0030076. This material is based upon work supported by the National Science Foundation under Grant IIS-2435801.

This work used DeltaAI at the National Center for Supercomputing Applications (NCSA) through allocation CIS251351 from the Advanced Cyberinfrastructure Coordination Ecosystem: Services & Support (ACCESS) program, which is supported by U.S. National Science Foundation grants #2138259, #2138286, #2138307, #2137603, and #2138296.

The authors gratefully acknowledge All of Us participants for their contributions, without whom this research would not have been possible. In addition, we thank the National Institutes of Health All of Us Research Program for making available the participant data examined in this study. This study used data from the All of Us Research Program Controlled Tier Dataset CDRv8, available to authorized users on the Researcher Workbench.
