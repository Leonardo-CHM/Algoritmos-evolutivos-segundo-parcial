"""Algoritmo genético de 16 bits para buscar el máximo de la función.

Las gráficas se generan con Matplotlib; los cálculos usan Python estándar.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from bisect import bisect_left
from itertools import accumulate
import argparse
import json
import math
from pathlib import Path
import random
import time

BITS = 16
MAX_INT = (1 << BITS) - 1
LOWER, UPPER = -1.0, 2.0


def decode(chromosome: int) -> float:
    """Pasa el cromosoma binario a un valor del intervalo [-1, 2]."""
    return LOWER + (UPPER - LOWER) * chromosome / MAX_INT


def objective(x: float) -> float:
    """Función que utilizamos para medir la aptitud."""
    return x * math.sin(10.0 * math.pi * x) + 1.0


def fitness(chromosome: int) -> float:
    return objective(decode(chromosome))


def exact_discrete_optimum() -> dict:
    """Busca el mejor resultado entre los 65 536 cromosomas posibles."""
    best = max(range(MAX_INT + 1), key=fitness)
    return {"chromosome": best, "bits": f"{best:016b}",
            "x": decode(best), "fitness": fitness(best)}


@dataclass(frozen=True)
class Settings:
    population_size: int = 30
    generations: int = 80
    crossover_probability: float = 0.80
    mutation_probability: float = 0.01  # por bit
    seed: int = 42
    elitism: bool = True
    plateau_window: int = 15

    def validate(self) -> None:
        if self.population_size < 4 or self.population_size % 2:
            raise ValueError("population_size debe ser par y >= 4")
        if self.generations < 1:
            raise ValueError("generations debe ser >= 1")
        for key in ('crossover_probability', 'mutation_probability'):
            if not 0.0 <= getattr(self, key) <= 1.0:
                raise ValueError(f"{key} debe estar entre 0 y 1")
        if self.plateau_window < 1:
            raise ValueError("plateau_window debe ser >= 1")


def roulette(population: list[int], values: list[float], rng: random.Random) -> int:
    """Elige un padre por ruleta; ajusta los pesos si hay aptitudes negativas."""
    offset = max(0.0, -min(values)) + 1.0e-12
    weights = [v + offset for v in values]
    total = sum(weights)
    threshold = rng.random() * total
    j = bisect_left(list(accumulate(weights)), threshold)
    return population[min(j, len(population)-1)]


def one_point_crossover(a: int, b: int, probability: float,
                        rng: random.Random) -> tuple[int, int]:
    if rng.random() >= probability:
        return a, b
    cut = rng.randrange(1, BITS)
    mask = (1 << (BITS - cut)) - 1
    return ((a & ~mask) | (b & mask), (b & ~mask) | (a & mask))


def bit_mutation(value: int, probability: float, rng: random.Random) -> int:
    for bit in range(BITS):
        if rng.random() < probability:
            value ^= 1 << bit
    return value


def diversity(population: list[int]) -> tuple[float, float]:
    """Mide la diferencia entre cromosomas y la cantidad de valores distintos."""
    n = len(population)
    distance = sum(2 * k * (n-k) / (n*(n-1))
                   for k in (sum(bool(ch & (1 << bit)) for ch in population)
                             for bit in range(BITS))) / BITS
    return distance, len(set(population)) / n


def run_ga(settings: Settings) -> dict:
    settings.validate()
    rng = random.Random(settings.seed)
    t0 = time.perf_counter()
    population = [rng.randrange(MAX_INT+1) for _ in range(settings.population_size)]
    history = []
    best_ever_chrom = None
    best_ever = -math.inf
    last_improvement = 0
    first_plateau = None
    for gen in range(settings.generations + 1):
        values = [fitness(ch) for ch in population]
        k = max(range(len(population)), key=lambda i: values[i])
        gen_best = values[k]
        if gen_best > best_ever + 1e-12:
            best_ever = gen_best
            best_ever_chrom = population[k]
            last_improvement = gen
        d, distinct = diversity(population)
        history.append({"generation": gen, "best": best_ever,
                        "generation_best": gen_best,
                        "mean": sum(values)/len(values),
                        "diversity_hamming": d, "unique_fraction": distinct})
        if first_plateau is None and gen-last_improvement >= settings.plateau_window:
            first_plateau = gen
        if gen == settings.generations:
            break
        offspring = []
        while len(offspring) < settings.population_size:
            a = roulette(population, values, rng)
            b = roulette(population, values, rng)
            c, d_child = one_point_crossover(a, b, settings.crossover_probability, rng)
            offspring.extend([bit_mutation(c, settings.mutation_probability, rng),
                              bit_mutation(d_child, settings.mutation_probability, rng)])
        if settings.elitism:
            # Si los hijos son peores, conservamos al mejor padre.
            offspring_values = [fitness(ch) for ch in offspring]
            worst = min(range(len(offspring)), key=lambda i: offspring_values[i])
            if values[k] > offspring_values[worst]:
                offspring[worst] = population[k]
        population = offspring
    elapsed = time.perf_counter() - t0
    opt = exact_discrete_optimum()
    last = history[-1]
    # Marcamos convergencia prematura cuando hay estancamiento,
    # poca diversidad y una diferencia importante frente al óptimo discreto.
    premature = (first_plateau is not None and
                 (opt['fitness'] - best_ever)/opt['fitness'] > 0.005 and
                 last['diversity_hamming'] < 0.20)
    return {"settings": asdict(settings), "best_chromosome": best_ever_chrom,
            "best_bits": f"{best_ever_chrom:016b}",
            "best_x": decode(best_ever_chrom), "best_fitness": best_ever,
            "optimum_discrete": opt, "absolute_gap": opt['fitness']-best_ever,
            "relative_gap_percent": 100*(opt['fitness']-best_ever)/opt['fitness'],
            "last_improvement_generation": last_improvement,
            "first_plateau_generation": first_plateau,
            "stabilization_generation": last_improvement,
            "premature_convergence": premature,
            "final_diversity": last['diversity_hamming'],
            "final_unique_fraction": last['unique_fraction'],
            "runtime_seconds": elapsed, "history": history}


def main():
    ap = argparse.ArgumentParser(description='AG binario para maximizar x*sin(10*pi*x)+1')
    ap.add_argument('--config', default='config.json', help='Archivo JSON de parámetros')
    ap.add_argument('--out', default='salida_basica', help='Carpeta de salida')
    args = ap.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding='utf-8'))
    result = run_ga(Settings(**cfg))
    target = Path(args.out)
    target.mkdir(parents=True, exist_ok=True)
    (target/'resultado.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    import csv
    with (target/'historial.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=result['history'][0]); writer.writeheader(); writer.writerows(result['history'])
    print(f"Mejor x: {result['best_x']:.8f} | f(x)={result['best_fitness']:.8f}")
    print(f"Óptimo discreto: f(x)={result['optimum_discrete']['fitness']:.8f}")
    print(f"Brecha: {result['relative_gap_percent']:.5f}%")
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(9, 5))
        plt.plot([h['generation'] for h in result['history']],
                 [h['best'] for h in result['history']], label='Mejor hasta ahora')
        plt.plot([h['generation'] for h in result['history']],
                 [h['mean'] for h in result['history']], label='Media de la población', alpha=.8)
        plt.axhline(result['optimum_discrete']['fitness'], linestyle='--', label='Óptimo discreto')
        plt.xlabel('Generación'); plt.ylabel('Aptitud f(x)'); plt.title('Convergencia del algoritmo genético')
        plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(target/'convergencia.png', dpi=170)
        plt.close()
        print('Gráfica: ' + str(target/'convergencia.png'))
    except ImportError:
        print('Instala matplotlib para generar la gráfica: pip install -r requirements.txt')


if __name__ == '__main__':
    main()
