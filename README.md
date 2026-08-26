# Cheaper by the Batch: Shared Traversal for Genotype Graph Editing

This repository collects the code artifacts for "Cheaper by the Batch: Shared Traversal for Genotype Graph Editing".

The core implementation is in [`grgl/`](grgl/), included as a submodule from [CornellHPC/grgl](https://github.com/CornellHPC/grgl). The polarization workflow used in the evaluation is in [`grapp/`](grapp/), included as a submodule from [CornellHPC/grapp](https://github.com/CornellHPC/grapp).

## Layout

- `grgl/`: core GRG library and batched mutation mapping implementation.
- `grapp/`: Python command-line workflow for allele polarization using GRGL.

## Cloning

Clone this repository with submodules:

```bash
git clone --recurse-submodules <artifact-repo-url>
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

## Code Versions

The submodules pin exact code versions:

```text
grgl:  0ce2f0bb0ca21c6c675f311765d72d3e92b16519  batch-paper
grapp: e25244762f0b35157695a8973538feec0ce7880b  polarization
```

You can verify the checked-out versions with:

```bash
git submodule status
```

## Running

See [`grgl/README.md`](grgl/README.md) for GRGL installation and mutation mapping details. See [`grapp/README.md`](grapp/README.md) for the `grapp polarize` workflow.

## Citation

If you use the mutation mapping features, please cite "Cheaper by the Batch: Shared Traversal for Genotype Graph Editing".

A preprint describing this work is available at TODO.
