import argparse
import random
import subprocess
import sys
from pathlib import Path

import tskit


def run(cmd, log):
    print(" ".join(map(str, cmd)), flush=True)

    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "w") as f:
        result = subprocess.run(
            list(map(str, cmd)),
            stdout=f,
            stderr=subprocess.STDOUT,
        )
    if result.returncode != 0:
        print(
            f"ERROR: command failed with exit code {result.returncode}: "
            f"{' '.join(map(str, cmd))}",
            file=sys.stderr,
        )
        print(f"See log: {log}", file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, result.args)


def write_fa(path, chrom, seq):
    with open(path, "w") as f:
        f.write(f">{chrom}\n")
        for i in range(0, len(seq), 80):
            f.write("".join(seq[i : i + 80]) + "\n")


def make_fastas(ts_path, out, chrom, flip_pct, seed):
    ts = tskit.load(str(ts_path))

    sites = []
    for variant in ts.variants():
        site = variant.site
        if len(site.mutations) != 1:
            continue

        anc = site.ancestral_state
        der = site.mutations[0].derived_state

        pos = int(site.position)
        if anc in "ACGT" and der in "ACGT" and anc != der and pos > 0:
            ancestral_count = int((variant.genotypes == 0).sum())
            derived_count = int((variant.genotypes == 1).sum())
            if ancestral_count > 0 and derived_count > 0:
                sites.append(
                    (
                        pos,
                        anc,
                        der,
                        ancestral_count,
                        derived_count,
                    )
                )

    random.seed(seed)

    n_flip = round(len(sites) * flip_pct)
    flips = set(random.sample(sites, n_flip))
    flipped_positions = {
        pos for pos, _anc, _der, _ancestral_count, _derived_count in flips
    }

    true = ["N"] * int(ts.sequence_length)
    fake = ["N"] * int(ts.sequence_length)

    for pos, anc, der, _ancestral_count, _derived_count in sites:
        fasta_index = pos - 1
        true[fasta_index] = anc
        fake[fasta_index] = der if pos in flipped_positions else anc

    write_fa(out / "true.fa", chrom, true)
    write_fa(out / "fake.fa", chrom, fake)

    with open(out / "flips.tsv", "w") as f:
        f.write("pos\tanc\tder\tancestral_count\tderived_count\n")
        for pos, anc, der, ancestral_count, derived_count in sorted(flips):
            f.write(
                f"{pos}\t{anc}\t{der}\t{ancestral_count}\t{derived_count}\n"
            )

    return len(sites), len(flips)


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Generate a simulated GRG plus true/fake ancestral FASTAs for "
            "grapp polarize instrumentation."
        )
    )
    ap.add_argument("--out", required=True)
    ap.add_argument("--samples", type=int, default=200_000)
    ap.add_argument("--length", type=int, default=5_000_000)
    ap.add_argument(
        "--chromosome",
        help=(
            "stdpopsim chromosome/contig to simulate, e.g. chr22. "
            "When set, --length is ignored and the full chromosome is simulated."
        ),
    )
    ap.add_argument(
        "--genetic-map",
        help=(
            "Optional stdpopsim genetic map ID, e.g. HapMapII_GRCh38. "
            "Requires --chromosome."
        ),
    )
    ap.add_argument("--flip-pct", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument(
        "--work-dir",
        type=Path,
        help=(
            "Directory for large generated files. Defaults to --out."
        ),
    )

    args = ap.parse_args()

    if args.samples <= 0:
        ap.error("--samples must be positive")
    if args.chromosome is None and args.length <= 0:
        ap.error("--length must be positive")
    if args.genetic_map is not None and args.chromosome is None:
        ap.error("--genetic-map requires --chromosome")
    if not 0 <= args.flip_pct <= 1:
        ap.error("--flip-pct must be between 0 and 1")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "logs").mkdir(parents=True, exist_ok=True)
    data_dir = out
    if args.work_dir is not None:
        data_dir = args.work_dir / out.name
    data_dir.mkdir(parents=True, exist_ok=True)

    chrom = args.chromosome or "sim"
    trees = data_dir / "sim.trees"
    polarized_grg = data_dir / "polarized.grg"
    true_fasta = data_dir / "true.fa"
    fake_fasta = data_dir / "fake.fa"

    popsim_cmd = ["stdpopsim", "HomSap"]
    if args.chromosome is not None:
        popsim_cmd.extend(["--chromosome", args.chromosome])
        if args.genetic_map is not None:
            popsim_cmd.extend(["--genetic-map", args.genetic_map])
    else:
        popsim_cmd.extend(["--length", args.length])
    popsim_cmd.extend(
        [
            "-d",
            "OutOfAfrica_2T12",
            "-s",
            args.seed,
            "-o",
            trees,
            f"EUR:{args.samples}",
        ]
    )

    run(popsim_cmd, out / "logs" / "popsim.log")

    ts = tskit.load(str(trees))
    left = 0
    right = int(ts.sequence_length)

    run(
        ["grg", "convert", trees, polarized_grg],
        out / "logs" / "convert.log",
    )

    n_sites, n_flips = make_fastas(
        trees,
        data_dir,
        chrom,
        args.flip_pct,
        args.seed,
    )

    with open(out / "summary.tsv", "w") as f:
        f.write(f"samples\t{args.samples}\n")
        f.write("population\tEUR\n")
        f.write(f"out_dir\t{out}\n")
        f.write(f"data_dir\t{data_dir}\n")
        f.write(f"chrom\t{chrom}\n")
        f.write(f"genetic_map\t{args.genetic_map or 'default'}\n")
        f.write(f"left\t{left}\n")
        f.write(f"right\t{right}\n")
        f.write(f"length\t{right - left}\n")
        f.write(f"flip_pct\t{args.flip_pct}\n")
        f.write(f"num_sites\t{n_sites}\n")
        f.write(f"num_flips\t{n_flips}\n")
        f.write(f"polarized_grg\t{polarized_grg}\n")
        f.write(f"input_grg\t{polarized_grg}\n")
        f.write(f"input_fasta\t{fake_fasta}\n")
        f.write(f"depolarization_fasta\t{fake_fasta}\n")
        f.write(f"truth_fasta\t{true_fasta}\n")

    print()
    print("Done")
    print(f"out: {out}")
    print(f"data: {data_dir}")
    print(f"sites: {n_sites}")
    print(f"flips: {n_flips}")
    print(f"INPUT_GRG={polarized_grg}")
    print(f"INPUT_FASTA={fake_fasta}")
    print(f"polarized_grg: {polarized_grg}")
    print(f"depolarization_fasta: {fake_fasta}")
    print(f"truth_fasta: {true_fasta}")
    print(f"logs: {out / 'logs'}")
    print(f"summary: {out / 'summary.tsv'}")


if __name__ == "__main__":
    main()
