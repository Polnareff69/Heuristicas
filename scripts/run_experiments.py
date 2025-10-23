import argparse
import csv
import glob
import json
import os
import time
from importlib.machinery import SourceFileLoader


def load_module_from(path: str, name: str):
    path = os.path.normpath(path)
    if not os.path.isabs(path):
        # resolve relative to repository root (one level above scripts/)
        base = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base, path)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return SourceFileLoader(name, path).load_module()


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
    parser.add_argument("--algo-ils", default="../instances/entrega2_ILS.py", help="Path to ILS module (used for 'local')")
    parser.add_argument("--algo-sa", default="../instances/entrega2.py", help="Path to SA module (used for 'no_local')")
    args = parser.parse_args()

    # Load algorithm modules (ILS and SA)
    try:
        ils_mod = load_module_from(args.algo_ils, "ils_mod")
    except Exception as e:
        print("Warning: could not load ILS module:", e)
        ils_mod = None
    try:
        sa_mod = load_module_from(args.algo_sa, "sa_mod")
    except Exception as e:
        print("Warning: could not load SA module:", e)
        sa_mod = None

    inst_files = sorted(glob.glob(args.instances_glob))
    if not inst_files:
        print("No instances found for glob:", args.instances_glob)
        return 1

    seeds = parse_seeds(args.seeds, args.num_seeds, args.seed_start)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    header = [
        "instance",
        "method",   # will be 'ILS' or 'SA'
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

                    # select module and label
                    if method == "local":
                        mod = ils_mod
                        method_label = "ILS"
                    else:
                        mod = sa_mod
                        method_label = "SA"

                    if mod is None:
                        print(f"Skipping {base} {method_label}: module not available")
                        continue

                    # Constructive (expect constructive_assignment present)
                    try:
                        assignment = mod.constructive_assignment(
                            instance, seed=seed, randomize=True, top_k_pref=args.top_k
                        )
                    except Exception as e:
                        print("Constructive failed for", base, method_label, ":", e)
                        continue

                    # Apply search depending on method
                    try:
                        if method == "local":
                            # prefer local_search_swaps for ILS
                            if hasattr(mod, "local_search_swaps"):
                                assignment = mod.local_search_swaps(instance, assignment, iters=args.iters, seed=seed)
                        else:
                            # prefer simulated_annealing for SA
                            if hasattr(mod, "simulated_annealing"):
                                # try common signatures; modules should adapt
                                try:
                                    assignment = mod.simulated_annealing(assignment, mod.score_solution_lex, getattr(mod, "generar_vecino_swap_simple", None),
                                                                         T_inicial=200.0, T_final=1.0, alpha=0.95, iter_por_temp=args.iters)
                                except Exception:
                                    try:
                                        assignment = mod.simulated_annealing(assignment, iter_por_temp=args.iters)
                                    except Exception:
                                        assignment = mod.simulated_annealing(assignment, args.iters)
                    except Exception as e:
                        print("Search failed for", base, method_label, ":", e)

                    # Score
                    try:
                        c1, c2, c3 = mod.score_solution_lex(instance, assignment)
                    except Exception as e:
                        print("Scoring failed for", base, method_label, ":", e)
                        c1 = c2 = c3 = 0

                    dt = time.perf_counter() - t0

                    w.writerow([base, method_label, seed, args.iters if method == "local" else args.iters, args.top_k, c1, c2, c3, round(dt, 6)])
                    f.flush()

    print("Wrote:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

