# Cheaper by the Batch: Shared Traversal for Genotype Graph Editing

This repository collects the code artifacts for "Cheaper by the Batch: Shared Traversal for Genotype Graph Editing".

The core implementation is in [`grgl/`](grgl/), included as a submodule from [CornellHPC/grgl](https://github.com/CornellHPC/grgl). The polarization workflow used in the evaluation is in [`grapp/`](grapp/), included as a submodule from [CornellHPC/grapp](https://github.com/CornellHPC/grapp).

## Layout

- `grgl/`: core GRG library and batched mutation mapping implementation.
- `grapp/`: Python command-line workflow for allele polarization using GRGL.

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

If you use the mutation mapping features, please cite "Cheaper by the Batch: Shared Traversal for Genotype Graph Editing".

A preprint describing this work is available at TODO.
