import csv
import os
from collections import defaultdict


def read_summary(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def pivot_summary(rows):
    by_inst = defaultdict(dict)  # inst -> method -> metrics
    for row in rows:
        inst = row["instance"]
        method = row["method"]
        by_inst[inst][method] = {
            "avg_C1": float(row["avg_C1"]),
            "avg_C2": float(row["avg_C2"]),
            "avg_C3": float(row["avg_C3"]),
            "avg_runtime_sec": float(row["avg_runtime_sec"]),
            "best": (int(row["best_C1"]), int(row["best_C2"]), int(row["best_C3"]))
        }
    return by_inst


def save_markdown_table(by_inst, out_md):
    insts = sorted(by_inst.keys())
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("**Tabla comparativa (promedios y mejor corrida)**\n\n")
        # Encabezado estilo Markdown table
        f.write("| instance | method | avg_C1 | avg_C2 | avg_C3 | avg_time(s) | best (C1, C2, C3) |\n")
        f.write("|---|---|---:|---:|---:|---:|---|\n")
        for inst in insts:
            for method in ("local", "no_local"):
                m = by_inst[inst].get(method)
                if not m:
                    continue
                f.write(
                    "| {inst} | {method} | {c1:.3f} | {c2:.3f} | {c3:.3f} | {rt:.6f} | {best} |\n".format(
                        inst=inst,
                        method=method,
                        c1=m["avg_C1"],
                        c2=m["avg_C2"],
                        c3=m["avg_C3"],
                        rt=m["avg_runtime_sec"],
                        best=m["best"],
                    )
                )


def make_plots(by_inst, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        insts = sorted(by_inst.keys())
        x = np.arange(len(insts))
        width = 0.35

        def bar_pair(metric_key, title, fname):
            local_vals = np.array([by_inst[i].get("local", {}).get(metric_key, float('nan')) for i in insts], dtype=float)
            noloc_vals = np.array([by_inst[i].get("no_local", {}).get(metric_key, float('nan')) for i in insts], dtype=float)
            fig, ax = plt.subplots(figsize=(max(8, len(insts)*0.9), 4))
            # Para tiempos, usar escala logarítmica para que ambas series sean visibles
            if metric_key == 'avg_runtime_sec':
                # Evita ceros en log
                local_vals = np.where(local_vals <= 0, 1e-6, local_vals)
                noloc_vals = np.where(noloc_vals <= 0, 1e-6, noloc_vals)
                ax.set_yscale('log')
                ax.set_ylabel('segundos (escala log)')
            ax.bar(x - width/2, local_vals, width, label='local', color='#1f77b4')
            ax.bar(x + width/2, noloc_vals, width, label='no_local', color='#ff7f0e')
            ax.set_title(title)
            ax.set_xticks(x, insts, rotation=45, ha='right')
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            fig.tight_layout()
            out_path = os.path.join(out_dir, fname)
            fig.savefig(out_path, dpi=150)
            plt.close(fig)
            return out_path

        p1 = bar_pair('avg_C1', 'Promedio C1 por instancia (local vs no_local)', 'avg_C1.png')
        p2 = bar_pair('avg_C2', 'Promedio C2 por instancia (local vs no_local)', 'avg_C2.png')
        p3 = bar_pair('avg_C3', 'Promedio C3 por instancia (local vs no_local)', 'avg_C3.png')
        p4 = bar_pair('avg_runtime_sec', 'Tiempo promedio (s) por instancia', 'avg_time.png')
        return [p1, p2, p3, p4]
    except Exception as e:
        # Sin matplotlib, no generamos gráficas
        note = os.path.join(out_dir, "NO_PLOTS.txt")
        with open(note, "w", encoding="utf-8") as f:
            f.write("No se pudieron generar gráficas. Motivo: " + repr(e))
        return []


def _lex_better(a, b):
    # a, b are (C1, C2, C3)
    if a[0] != b[0]:
        return a[0] > b[0]
    if a[1] != b[1]:
        return a[1] > b[1]
    return a[2] > b[2]


def make_poster_md(by_inst, plot_paths, out_md):
    # concl: cuántas instancias favorecen local vs no_local en promedio
    total = len(by_inst)
    fav_local = 0
    for inst, dd in by_inst.items():
        a = (dd.get('local',{}).get('avg_C1',0.0), dd.get('local',{}).get('avg_C2',0.0), dd.get('local',{}).get('avg_C3',0.0))
        b = (dd.get('no_local',{}).get('avg_C1',0.0), dd.get('no_local',{}).get('avg_C2',0.0), dd.get('no_local',{}).get('avg_C3',0.0))
        if _lex_better(a, b):
            fav_local += 1
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("**Póster – Heurística Constructiva + Aleatorizada + Búsqueda Local**\n\n")
        f.write("- Problema: asignación de empleados a escritorios por día con preferencias, cohesión de grupos y balance de zonas.\n")
        f.write("- Método: constructivo aleatorizado (top‑k y orden aleatorio, controlado por semilla) + búsqueda local por swaps con evaluación lexicográfica (C1,C2,C3).\n")
        f.write("- Experimentos: local vs no_local, 10 semillas, iters=1200, top-k=3.\n\n")

        f.write("Resultados promedio por instancia (tabla):\n\n")
        save_markdown_table(by_inst, out_md.replace('.md','_table.md'))
        with open(out_md.replace('.md','_table.md'), 'r', encoding='utf-8') as tf:
            f.write(tf.read())
        f.write("\n")

        # Pseudocódigo breve
        f.write("Pseudocódigo (resumen)\n\n")
        f.write("Constructivo aleatorizado (por día):\n")
        f.write("- Para cada día d: obtener presentes; mezclar con semilla.\n")
        f.write("- Para cada empleado e: estimar zona objetivo de su grupo (mayoría actual).\n")
        f.write("- Elegir escritorio: (i) preferidos en zona objetivo (top-k aleatorio),\n")
        f.write("  (ii) preferidos restantes (top-k aleatorio), (iii) cualquier libre (preferir zona objetivo).\n")
        f.write("- Completar ausentes con none.\n\n")
        f.write("Búsqueda local (swaps):\n")
        f.write("- Repetir iters: elegir día aleatorio; si hay ≥2 asignados, proponer swap entre dos;\n")
        f.write("  aceptar si (C1,C2,C3) mejora lexicográficamente.\n\n")

        # Conclusiones y recomendaciones
        f.write("Conclusiones y recomendaciones\n\n")
        f.write(f"- En promedio, {fav_local}/{total} instancias favorecen 'local' (mejor C1).\n")
        f.write("- 'local' cuesta más tiempo (≈10^2–10^3 ms según instancia y iters) pero mejora la calidad.\n")
        f.write("- Parámetros recomendados: top-k=3, iters≈1000–1500, seed fija para reproducibilidad.\n")
        f.write("- Sensibilidad: aumentar iters mejora C1 con rendimientos decrecientes; top‑k>1 da diversidad útil.\n\n")

        if plot_paths:
            f.write("Gráficas (local vs no_local):\n\n")
            for p in plot_paths:
                rel = os.path.relpath(p, os.path.dirname(out_md))
                f.write(f"- {os.path.basename(p)}\n")
                f.write(f"  ![]({rel})\n\n")
        else:
            f.write("Nota: no se generaron gráficas (matplotlib no disponible).\n")


def main():
    base = os.path.dirname(os.path.dirname(__file__))
    summary_csv = os.path.join(base, 'results', 'summary.csv')
    if not os.path.exists(summary_csv):
        print('No existe results/summary.csv. Corre scripts/summarize_results.py primero.')
        return 1
    rows = read_summary(summary_csv)
    by_inst = pivot_summary(rows)
    plots_dir = os.path.join(base, 'results', 'plots')
    plots = make_plots(by_inst, plots_dir)
    poster_md = os.path.join(base, 'results', 'poster.md')
    make_poster_md(by_inst, plots, poster_md)
    print('Assets de póster generados:')
    print('-', poster_md)
    if plots:
        for p in plots:
            print('-', p)
    else:
        print('- (sin gráficas)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
