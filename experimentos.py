"""Compara población, cruce y mutación en ocho configuraciones.

Cada una se repite con cinco semillas para comparar la variación.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
import csv
import json
import statistics
import argparse
from algoritmo_genetico import Settings, run_ga, exact_discrete_optimum


def experiment(output: Path, generations: int = 70):
    output.mkdir(parents=True, exist_ok=True)
    samples = []
    trajectories = {}
    seeds = [17, 29, 43, 71, 101]
    count = 0
    for n in [12, 50]:
        for pc in [0.6, 0.9]:
            for pm in [0.001, 0.025]:
                count += 1
                label = f'C{count}'
                for seed in seeds:
                    s = Settings(population_size=n, generations=generations,
                                 crossover_probability=pc, mutation_probability=pm,
                                 seed=seed, elitism=True, plateau_window=15)
                    r = run_ga(s)
                    samples.append({"config": label, "n": n, "pc": pc, "pm": pm,
                                    "seed": seed, "best": r['best_fitness'],
                                    "x": r['best_x'], "gap_pct": r['relative_gap_percent'],
                                    "stabilized": r['stabilization_generation'],
                                    "first_plateau": r['first_plateau_generation'],
                                    "runtime_s": r['runtime_seconds'],
                                    "diversity": r['final_diversity'],
                                    "unique_fraction": r['final_unique_fraction'],
                                    "premature": r['premature_convergence']})
                    trajectories[f'{label}_{seed}'] = r['history']
    groups = defaultdict(list)
    for r in samples:
        groups[r['config']].append(r)
    summary = []
    for label, rr in groups.items():
        vals = [v['best'] for v in rr]
        summary.append({"config": label, "n": rr[0]['n'], "pc": rr[0]['pc'],
                        "pm": rr[0]['pm'], "runs": len(rr), "mean_best": statistics.mean(vals),
                        "sd_best": statistics.stdev(vals),
                        "max_best": max(vals), "min_best": min(vals),
                        "mean_stabilization": statistics.mean(v['stabilized'] for v in rr),
                        "mean_runtime_s": statistics.mean(v['runtime_s'] for v in rr),
                        "mean_diversity": statistics.mean(v['diversity'] for v in rr),
                        "mean_gap_pct": statistics.mean(v['gap_pct'] for v in rr),
                        "premature_runs": sum(v['premature'] for v in rr)})
    for filename, data in [('repeticiones_40.csv', samples), ('resumen_8_configuraciones.csv', summary)]:
        with (output/filename).open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    (output/'historiales_40.json').write_text(json.dumps(trajectories, ensure_ascii=False), encoding='utf-8')
    (output/'resumen.json').write_text(json.dumps({'optimum': exact_discrete_optimum(),
         'seeds': seeds, 'generations': generations, 'summaries': summary}, indent=2), encoding='utf-8')
    print(f'{len(samples)} ejecuciones realizadas en {len(summary)} configuraciones; archivos en {output}')
    for row in summary:
        print(row['config'], 'n=', row['n'], 'Pc=', row['pc'], 'Pm=', row['pm'],
              'fitness:', round(row['mean_best'], 6), '±', round(row['sd_best'], 6),
              'prematura:', row['premature_runs'])
    try:
        import matplotlib.pyplot as plt
        from matplotlib.ticker import MaxNLocator
        plt.figure(figsize=(9, 4.9))
        for row in summary:
            keys = [f"{row['config']}_{seed}" for seed in seeds]
            avg = [statistics.mean(trajectories[k][g]['best'] for k in keys)
                   for g in range(generations+1)]
            plt.plot(range(generations+1), avg, label=f"{row['config']} (N={row['n']}, pm={row['pm']})", linewidth=1.8)
        plt.axhline(exact_discrete_optimum()['fitness'], color='black', ls='--', lw=1.5, label='Óptimo 16 bits')
        plt.xlabel('Generación'); plt.ylabel('Mejor aptitud acumulada (media de 5)')
        plt.title('Convergencia promedio por configuración'); plt.grid(alpha=.25); plt.legend(fontsize=8, ncol=2)
        plt.tight_layout(); plt.savefig(output/'convergencia_comparativa.png', dpi=180); plt.close()
        plt.figure(figsize=(9, 4.8))
        plt.bar([z['config'] for z in summary], [z['mean_best'] for z in summary],
                yerr=[z['sd_best'] for z in summary], capsize=5)
        plt.axhline(exact_discrete_optimum()['fitness'], color='black', ls='--', label='Óptimo')
        plt.ylim(1.5, max(z['max_best'] for z in summary) + .12)
        plt.ylabel('Mejor aptitud media ± desviación estándar'); plt.xlabel('Configuración')
        plt.title('Resultados de las cinco repeticiones'); plt.grid(axis='y', alpha=.25)
        plt.legend(); plt.tight_layout(); plt.savefig(output/'promedios_desviacion.png', dpi=180); plt.close()
        plt.figure(figsize=(9, 4.8))
        for row in summary:
            keys = [f"{row['config']}_{seed}" for seed in seeds]
            avg = [statistics.mean(trajectories[k][g]['diversity_hamming'] for k in keys)
                   for g in range(generations+1)]
            plt.plot(range(generations+1), avg, label=row['config'], linewidth=1.8)
        plt.xlabel('Generación'); plt.ylabel('Distancia Hamming normalizada (media)')
        plt.title('Diversidad genética media'); plt.grid(alpha=.25); plt.legend(ncol=4)
        plt.tight_layout(); plt.savefig(output/'diversidad_comparativa.png', dpi=180); plt.close()
    except ImportError:
        print('Gráficas no generadas: instala matplotlib.')
    return samples, summary


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='resultados')
    ap.add_argument('--generations', type=int, default=70)
    args = ap.parse_args()
    experiment(Path(args.out), args.generations)
