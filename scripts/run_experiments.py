import argparse
import csv
import glob
import json
import os
import time
from importlib.machinery import SourceFileLoader


def load_algo_module():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "instances", "entrega1.py")
    return SourceFileLoader("entrega1_mod", path).load_module()


def parse_seeds(seeds_arg: str, num_seeds: int, start: int) -> list[int]:
    if seeds_arg:
        return [int(x) for x in seeds_arg.split(",") if x.strip()]
    return list(range(start, start + num_seeds))


def main():
    parser = argparse.ArgumentParser(description="Run batch experiments on heuristic assignment")
    parser.add_argument("--instances-glob", default="instances/instance*.json", help="Glob for instances")
    parser.add_argument("--methods", choices=["local", "no_local", "both"], default="both", help="Which methods to run")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--iters", type=int, default=1000)
    parser.add_argument("--seeds", default=None, help="Comma-separated seeds (overrides --num-seeds/--seed-start)")
    parser.add_argument("--num-seeds", type=int, default=5)
    parser.add_argument("--seed-start", type=int, default=1)
    parser.add_argument("--out", default="results/experiments.csv", help="CSV output path")
    args = parser.parse_args()

    mod = load_algo_module()

    inst_files = sorted(glob.glob(args.instances_glob))
    if not inst_files:
        print("No instances found for glob:", args.instances_glob)
        return 1

    seeds = parse_seeds(args.seeds, args.num_seeds, args.seed_start)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    header = [
        "instance",
        "method",
        "seed",
        "iters",
        "top_k",
        "C1",
        "C2",
        "C3",
        "runtime_sec",
    ]

    methods = ["local", "no_local"] if args.methods == "both" else [args.methods]

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)

        for inst_path in inst_files:
            with open(inst_path, "r", encoding="utf-8") as jf:
                instance = json.load(jf)

            base = os.path.basename(inst_path)
            for method in methods:
                for seed in seeds:
                    t0 = time.perf_counter()

                    # Constructive
                    assignment = mod.constructive_assignment(
                        instance, seed=seed, randomize=True, top_k_pref=args.top_k
                    )
                    # Local search
                    if method == "local":
                        assignment = mod.local_search_swaps(
                            instance, assignment, iters=args.iters, seed=seed
                        )
                    c1, c2, c3 = mod.score_solution_lex(instance, assignment)
                    dt = time.perf_counter() - t0

                    w.writerow([base, method, seed, args.iters if method == "local" else 0, args.top_k, c1, c2, c3, round(dt, 6)])
                    f.flush()

    print("Wrote:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

