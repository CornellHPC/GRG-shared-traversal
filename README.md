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

If you use the mutation mapping features, please cite "Cheaper by the Batch: Shared Traversal for Genotype Graph Editing". A preprint describing this work will be available soon (link TBD).

## Acknowledgments

The authors thank the members of the [ALPS Lab at Cornell University](https://giuliaguidi.github.io/hpcgroup/) for their feedback and discussion.

This research used resources from the National Energy Research Scientific Computing Center, a DOE Office of Science User Facility supported by the Office of Science of the U.S. Department of Energy under Contract No. DE-AC02-05CH11231, using NERSC award ASCR-ERCAP0030076. This material is based upon work supported by the National Science Foundation under Grant IIS-2435801.

This work used DeltaAI at the National Center for Supercomputing Applications (NCSA) through allocation CIS251351 from the Advanced Cyberinfrastructure Coordination Ecosystem: Services & Support (ACCESS) program, which is supported by U.S. National Science Foundation grants #2138259, #2138286, #2138307, #2137603, and #2138296.

The authors gratefully acknowledge All of Us participants for their contributions, without whom this research would not have been possible. In addition, we thank the National Institutes of Health All of Us Research Program for making available the participant data examined in this study. This study used data from the All of Us Research Program Controlled Tier Dataset CDRv8, available to authorized users on the Researcher Workbench.
