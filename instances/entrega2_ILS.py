# Entrega 2 - Constructivo + Recocido Simulado + ILS
# Autores: [Alejandro Arango, Juan Jose Munoz]
# Universidad EAFIT - 2025

import json
import os
import sys
import random
import math
import copy
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional

# ---------- Utilidades ----------
def build_desk_to_zone(desks_z: Dict[str, List[str]]) -> Dict[str, str]:
    d2z = {}
    for z, desks in desks_z.items():
        for d in desks:
            d2z[d] = z
    return d2z

def employee_group(emp: str, employees_g: Dict[str, List[str]]) -> Optional[str]:
    for g, members in employees_g.items():
        if emp in members:
            return g
    return None

def employees_present_today(day: str, days_e: Dict[str, List[str]], employees: List[str]) -> List[str]:
    if not days_e:
        return employees[:]
    return [e for e in employees if day in days_e.get(e, [])]

# ---------- 1) Método constructivo + aleatorización ----------
def constructive_assignment(instance: dict, seed: int = 42, randomize: bool = True, top_k_pref: int = 3) -> Dict[str, Dict[str, Optional[str]]]:
    rng = random.Random(seed)
    employees = instance["Employees"]
    desks = instance["Desks"]
    days = instance.get("Days", [])
    desks_e = instance.get("Desks_E", {})
    employees_g = instance.get("Employees_G", {})
    days_e = instance.get("Days_E", {})
    desks_z = instance.get("Desks_Z", {})
    d2z = build_desk_to_zone(desks_z)

    assignment: Dict[str, Dict[str, Optional[str]]] = {day: {} for day in days}

    for day in days:
        present = employees_present_today(day, days_e, employees)
        if randomize:
            rng.shuffle(present)
        used_desks = set()
        group_zone_count = defaultdict(Counter)

        for e in present:
            g = employee_group(e, employees_g)
            target_zone = group_zone_count[g].most_common(1)[0][0] if (g and group_zone_count[g]) else None

            pref_list = desks_e.get(e, [])
            pref_avail = [d for d in pref_list if d not in used_desks]
            pref_avail_target = [d for d in pref_avail if d2z.get(d) == target_zone] if target_zone else pref_avail[:]

            chosen = None
            if pref_avail_target:
                chosen = rng.choice(pref_avail_target[:min(top_k_pref, len(pref_avail_target))]) if randomize else pref_avail_target[0]
            elif pref_avail:
                chosen = rng.choice(pref_avail[:min(top_k_pref, len(pref_avail))]) if randomize else pref_avail[0]
            else:
                free_desks = [d for d in desks if d not in used_desks]
                free_target = [d for d in free_desks if d2z.get(d) == target_zone] if target_zone else free_desks[:]
                pool = free_target if free_target else free_desks
                chosen = rng.choice(pool) if (randomize and pool) else (pool[0] if pool else None)

            assignment[day][e] = chosen
            if chosen:
                used_desks.add(chosen)
                if g:
                    z = d2z.get(chosen)
                    if z:
                        group_zone_count[g][z] += 1

        for e in employees:
            assignment[day].setdefault(e, None)

    return assignment

# ---------- 2) Puntaje lexicográfico ----------
def score_solution_lex(instance: dict, assignment: Dict[str, Dict[str, Optional[str]]]) -> Tuple[int, int, int]:
    desks_e = instance.get("Desks_E", {})
    employees_g = instance.get("Employees_G", {})
    desks_z = instance.get("Desks_Z", {})
    d2z = build_desk_to_zone(desks_z)
    days = instance.get("Days", [])
    employees = instance.get("Employees", [])

    c1_pref_hits, c2_group_cohesion, c3_balance = 0, 0, 0

    for day in days:
        for e in employees:
            d = assignment[day].get(e)
            if d and d in desks_e.get(e, []):
                c1_pref_hits += 1
        for g, members in employees_g.items():
            z_count = Counter()
            for e in members:
                d = assignment[day].get(e)
                if d:
                    z = d2z.get(d)
                    if z:
                        z_count[z] += 1
            if z_count:
                c2_group_cohesion += z_count.most_common(1)[0][1]
        z_occ = Counter()
        for e in employees:
            d = assignment[day].get(e)
            if d:
                z = d2z.get(d)
                if z:
                    z_occ[z] += 1
        if z_occ:
            mx, mn = max(z_occ.values()), min(z_occ.values())
            c3_balance += -(mx - mn)
    return (c1_pref_hits, c2_group_cohesion, c3_balance)

# ---------- Recocido Simulado ----------
def generar_vecino_swap(assignment, instance):
    days = instance.get("Days", [])
    employees = instance.get("Employees", [])
    new = {d: m.copy() for d, m in assignment.items()}
    if not days:
        return new
    day = random.choice(days)
    assigned_today = [e for e in employees if new[day].get(e) is not None]
    if len(assigned_today) < 2:
        return new
    a, b = random.sample(assigned_today, 2)
    new[day][a], new[day][b] = new[day][b], new[day][a]
    return new

def simulated_annealing(solucion_inicial, evaluar, generar_vecino,
                        T_inicial=200.0, T_final=1.0, alpha=0.95, iter_por_temp=100):
    S = copy.deepcopy(solucion_inicial)
    mejor = copy.deepcopy(S)
    valor_S = evaluar(S)
    valor_mejor = valor_S
    T = T_inicial

    while T > T_final:
        for _ in range(iter_por_temp):
            vecino = generar_vecino(S)
            valor_vecino = evaluar(vecino)
            delta = valor_vecino - valor_S

            if delta > 0 or random.random() < math.exp(delta / T):
                S = copy.deepcopy(vecino)
                valor_S = valor_vecino

                if valor_S > valor_mejor:
                    mejor = copy.deepcopy(S)
                    valor_mejor = valor_S

        T *= alpha

    return mejor

# ---------- ILS: Iterated Local Search ----------
def local_search_swaps_hillclimb(instance: dict, assignment: Dict[str, Dict[str, Optional[str]]],
                                 evaluar, iters: int = 500, seed: Optional[int] = None) -> Dict[str, Dict[str, Optional[str]]]:
    if seed is not None:
        random.seed(seed)
    S = {d: m.copy() for d, m in assignment.items()}
    val_S = evaluar(S)
    days = instance.get("Days", [])
    employees = instance.get("Employees", [])

    for _ in range(iters):
        if not days:
            break
        day = random.choice(days)
        assigned_today = [e for e in employees if S[day].get(e) is not None]
        if len(assigned_today) < 2:
            continue
        a, b = random.sample(assigned_today, 2)
        vecino = {d: m.copy() for d, m in S.items()}
        vecino[day][a], vecino[day][b] = vecino[day][b], vecino[day][a]
        val_v = evaluar(vecino)
        if val_v > val_S:
            S = vecino
            val_S = val_v
    return S

def perturbation_k_swaps(assignment: Dict[str, Dict[str, Optional[str]]],
                         instance: dict, k: int = 3, seed: Optional[int] = None) -> Dict[str, Dict[str, Optional[str]]]:
    if seed is not None:
        random.seed(seed)
    S = {d: m.copy() for d, m in assignment.items()}
    days = instance.get("Days", [])
    employees = instance.get("Employees", [])
    if not days:
        return S
    for _ in range(k):
        day = random.choice(days)
        assigned_today = [e for e in employees if S[day].get(e) is not None]
        if len(assigned_today) < 2:
            continue
        a, b = random.sample(assigned_today, 2)
        S[day][a], S[day][b] = S[day][b], S[day][a]
    return S

def iterated_local_search(instance: dict,
                          initial: Dict[str, Dict[str, Optional[str]]],
                          evaluar,
                          local_search_func,
                          perturb_func,
                          max_iters: int = 20,
                          ls_iters: int = 500,
                          perturb_k: int = 3,
                          seed: Optional[int] = None) -> Dict[str, Dict[str, Optional[str]]]:
    if seed is not None:
        random.seed(seed)
    S = local_search_func(instance, initial, evaluar, iters=ls_iters, seed=seed)
    best = copy.deepcopy(S)
    best_val = evaluar(best)

    for _ in range(max_iters):
        S_p = perturb_func(S, instance, k=perturb_k, seed=None)
        S_p = local_search_func(instance, S_p, evaluar, iters=ls_iters, seed=None)
        val_p = evaluar(S_p)
        if val_p > best_val:
            best = copy.deepcopy(S_p)
            best_val = val_p
            S = S_p
        else:
            S = S_p
    return best

# ---------- Validación y reporte ----------
def validate_assignment(instance: dict, assignment: Dict[str, Dict[str, Optional[str]]]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    days = instance.get("Days", [])
    employees = set(instance.get("Employees", []))
    desks = set(instance.get("Desks", []))

    for day in days:
        if day not in assignment:
            errors.append(f"Falta el día en la solución: {day}")
            continue

        mapping = assignment[day]
        missing = [e for e in employees if e not in mapping]
        if missing:
            errors.append(f"Día {day}: faltan empleados {missing}")

        used = [d for d in mapping.values() if d is not None]
        bad = [d for d in used if d not in desks]
        if bad:
            errors.append(f"Día {day}: escritorios inexistentes {sorted(set(bad))}")
        seen, dup = set(), set()
        for d in used:
            if d in seen:
                dup.add(d)
            else:
                seen.add(d)
        if dup:
            errors.append(f"Día {day}: escritorios duplicados {sorted(dup)}")

    return (len(errors) == 0, errors)

def report_assignment(instance: dict, assignment: Dict[str, Dict[str, Optional[str]]]) -> None:
    desks_e = instance.get("Desks_E", {})
    employees_g = instance.get("Employees_G", {})
    desks_z = instance.get("Desks_Z", {})
    d2z = build_desk_to_zone(desks_z)
    days = instance.get("Days", [])
    employees = instance.get("Employees", [])

    total_c1 = total_c2 = total_c3 = 0
    print("Reporte por día:")
    for day in days:
        c1 = 0
        for e in employees:
            d = assignment[day].get(e)
            if d and d in desks_e.get(e, []):
                c1 += 1
        c2 = 0
        for g, members in employees_g.items():
            z_count = Counter()
            for e in members:
                d = assignment[day].get(e)
                if d:
                    z = d2z.get(d)
                    if z:
                        z_count[z] += 1
            if z_count:
                c2 += z_count.most_common(1)[0][1]
        z_occ = Counter()
        for e in employees:
            d = assignment[day].get(e)
            if d:
                z = d2z.get(d)
                if z:
                    z_occ[z] += 1
        c3 = 0
        if z_occ:
            mx, mn = max(z_occ.values()), min(z_occ.values())
            c3 = -(mx - mn)
        assigned = sum(1 for e in employees if assignment[day].get(e) is not None)
        print(f"- {day}: asignados={assigned} | C1={c1} C2={c2} C3={c3}")
        total_c1 += c1
        total_c2 += c2
        total_c3 += c3
    print(f"Totales: C1={total_c1} C2={total_c2} C3={total_c3}")

# ---------- MAIN ----------
if __name__ == "__main__":
    parser = __import__("argparse").ArgumentParser(description="Entrega 2 - Constructivo + Recocido Simulado / ILS")
    parser.add_argument("--in", dest="infile", default="instance1.json",
                        help="Archivo de instancia (ej: instance1.json)")
    parser.add_argument("--outdir", default="solutions",
                        help="Carpeta de salida (se creará si no existe)")
    parser.add_argument("--seed", type=int, default=42, help="Semilla para aleatorización")
    parser.add_argument("--top-k", type=int, default=3, help="Top-k preferencias a muestrear")
    parser.add_argument("--iters", type=int, default=1000, help="Iteraciones por temperatura (annealing)")
    parser.add_argument("--tinit", type=float, default=200.0, help="Temperatura inicial (annealing)")
    parser.add_argument("--tfinal", type=float, default=1.0, help="Temperatura final (annealing)")
    parser.add_argument("--alpha", type=float, default=0.95, help="Factor de enfriamiento (annealing)")
    parser.add_argument("--stdout", action="store_true",
                        help="Imprime la solución por stdout en lugar de escribir archivo")
    parser.add_argument("--report", action="store_true", help="Imprime un reporte por día y totales")
    parser.add_argument("--validate", action="store_true", help="Valida la solución antes de guardar")
    parser.add_argument("--ils", action="store_true", help="Usar ILS en vez de recocido simulado")
    parser.add_argument("--ils-iters", type=int, default=20, help="Iteraciones superiores de ILS")
    parser.add_argument("--ls-iters", type=int, default=500, help="Iteraciones de búsqueda local en cada ILS")
    parser.add_argument("--perturb-k", type=int, default=3, help="Número de swaps en la perturbación ILS")
    args = parser.parse_args()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    instance_file = os.path.join(BASE_DIR, args.infile)
    _out_raw = os.path.expanduser(os.path.expandvars(args.outdir))
    out_dir = _out_raw if os.path.isabs(_out_raw) else os.path.join(BASE_DIR, _out_raw)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"solution_{os.path.splitext(os.path.basename(args.infile))[0]}_result.json")

    print("--Script: ", __file__,"--")
    print("--BASE_DIR:", BASE_DIR,"--")
    print("--CWD:", os.getcwd(),"--")
    print("--Leyendo:", instance_file,"--")
    print("--Salida en:", out_file,"--")

    if not os.path.isfile(instance_file):
        print("ERROR: no encuentro la instancia:", instance_file)
        print("Archivos en la carpeta:", os.listdir(BASE_DIR))
        sys.exit(1)

    with open(instance_file, "r", encoding="utf-8") as f:
        instance = json.load(f)

    # Construcción inicial
    assignment = constructive_assignment(
        instance, seed=args.seed, randomize=True, top_k_pref=args.top_k
    )

    # Función de evaluación lexicográfica priorizada
    def _score(s):
        c1, c2, c3 = score_solution_lex(instance, s)
        return c1 * 10000 + c2 * 100 + c3

    before = score_solution_lex(instance, assignment)

    # Fijar semilla global
    random.seed(args.seed)

    if args.ils:
        assignment = iterated_local_search(
            instance,
            assignment,
            evaluar=_score,
            local_search_func=local_search_swaps_hillclimb,
            perturb_func=perturbation_k_swaps,
            max_iters=args.ils_iters,
            ls_iters=args.ls_iters,
            perturb_k=args.perturb_k,
            seed=args.seed
        )
    else:
        assignment = simulated_annealing(
            assignment,
            evaluar=_score,
            generar_vecino=lambda s: generar_vecino_swap(s, instance),
            T_inicial=args.tinit, T_final=args.tfinal, alpha=args.alpha, iter_por_temp=args.iters
        )

    after = score_solution_lex(instance, assignment)
    print("Puntaje antes (C1, C2, C3):", before)
    print("Puntaje después (C1, C2, C3):", after)

    if args.validate:
        ok, errs = validate_assignment(instance, assignment)
        if ok:
            print("Validación: OK")
        else:
            print("Validación: errores encontrados:")
            for e in errs:
                print(" -", e)
            sys.exit(2)

    if args.report:
        report_assignment(instance, assignment)

    if args.stdout:
        print(json.dumps(assignment, ensure_ascii=False, indent=2))
    else:
        try:
            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(assignment, f, ensure_ascii=False, indent=2)
            print("-Solución guardada en:", out_file)
        except Exception as e:
            print("No pude escribir el archivo de salida:", e)
            print("Directorio existe?", os.path.isdir(os.path.dirname(out_file)), "->", os.path.dirname(out_file))
            raise

    print("Fin.")