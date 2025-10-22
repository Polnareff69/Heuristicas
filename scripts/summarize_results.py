import argparse
import csv
import os
from collections import defaultdict


def lex_better(a, b):
    # a, b are (C1, C2, C3)
    if a[0] != b[0]:
        return a[0] > b[0]
    if a[1] != b[1]:
        return a[1] > b[1]
    return a[2] > b[2]


def main():
    parser = argparse.ArgumentParser(description="Summarize experiments.csv")
    parser.add_argument("--in", dest="infile", default="results/experiments.csv")
    parser.add_argument("--out-csv", default="results/summary.csv")
    parser.add_argument("--out-md", default="results/summary.md")
    args = parser.parse_args()

    rows = []
    with open(args.infile, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            row["C1"] = int(row["C1"]) ; row["C2"] = int(row["C2"]) ; row["C3"] = int(row["C3"])
            row["iters"] = int(row["iters"]) ; row["top_k"] = int(row["top_k"]) ; row["runtime_sec"] = float(row["runtime_sec"])
            rows.append(row)

    by_key = defaultdict(list)  # (instance, method) -> rows
    for row in rows:
        by_key[(row["instance"], row["method"])].append(row)

    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    # Write CSV summary
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "instance", "method", "runs", "avg_C1", "avg_C2", "avg_C3", "best_C1", "best_C2", "best_C3", "avg_runtime_sec", "best_seed"
        ])
        summaries = {}
        for (inst, method), lst in sorted(by_key.items()):
            n = len(lst)
            avg_c1 = sum(r["C1"] for r in lst) / n
            avg_c2 = sum(r["C2"] for r in lst) / n
            avg_c3 = sum(r["C3"] for r in lst) / n
            avg_rt = sum(r["runtime_sec"] for r in lst) / n
            best = lst[0]
            for r in lst[1:]:
                if lex_better((r["C1"], r["C2"], r["C3"]), (best["C1"], best["C2"], best["C3"])):
                    best = r
            w.writerow([
                inst, method, n,
                round(avg_c1, 3), round(avg_c2, 3), round(avg_c3, 3),
                best["C1"], best["C2"], best["C3"], round(avg_rt, 6), best["seed"]
            ])
            summaries[(inst, method)] = {
                "avg": (avg_c1, avg_c2, avg_c3),
                "best": (best["C1"], best["C2"], best["C3"]),
                "avg_rt": avg_rt,
            }

    # Write Markdown summary for quick view
    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write("**Resumen de Experimentos**\n\n")
        insts = sorted({inst for (inst, _) in summaries.keys()})
        for inst in insts:
            f.write(f"**{inst}**\n")
            f.write("- local:   ")
            s_local = summaries.get((inst, "local"))
            if s_local:
                f.write(f"avg={tuple(round(x,3) for x in s_local['avg'])}, best={s_local['best']}, avg_time={round(s_local['avg_rt'],6)}s\n")
            else:
                f.write("(sin corridas)\n")
            f.write("- no_local: ")
            s_nol = summaries.get((inst, "no_local"))
            if s_nol:
                f.write(f"avg={tuple(round(x,3) for x in s_nol['avg'])}, best={s_nol['best']}, avg_time={round(s_nol['avg_rt'],6)}s\n")
            else:
                f.write("(sin corridas)\n")
            # Conclusión breve por instancia
            if s_local and s_nol:
                better = "local" if lex_better(s_local["avg"], s_nol["avg"]) else "no_local"
                f.write(f"- Conclusión: promedio lexicográfico favorece {better}.\n\n")
        
    print("Wrote:", args.out_csv)
    print("Wrote:", args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

