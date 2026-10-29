"""Pruebas sencillas para comprobar las funciones del algoritmo.

Ejecutar: py -m unittest test_algoritmo -v
"""
import unittest
import random
from algoritmo_genetico import (Settings, run_ga, decode, objective, fitness,
                                  MAX_INT, one_point_crossover, bit_mutation,
                                  exact_discrete_optimum)

class TestGeneticAlgorithm(unittest.TestCase):
    def test_domain(self):
        self.assertEqual(decode(0), -1.0)
        self.assertEqual(decode(MAX_INT), 2.0)
    def test_cross_no_change(self):
        self.assertEqual(one_point_crossover(1, 2, 0.0, random.Random(2)), (1, 2))
    def test_mutation_all_bits(self):
        self.assertEqual(bit_mutation(0, 1.0, random.Random(5)), MAX_INT)
    def test_objective(self):
        self.assertAlmostEqual(objective(0), 1.0)
    def test_elitism_monotonic(self):
        r = run_ga(Settings(population_size=12, generations=20, seed=3))
        best = [h['best'] for h in r['history']]
        self.assertTrue(all(a <= b for a, b in zip(best, best[1:])))
    def test_reproducible(self):
        s = Settings(population_size=12, generations=15, seed=39)
        a, b = run_ga(s), run_ga(s)
        self.assertEqual(a['best_chromosome'], b['best_chromosome'])
        self.assertEqual(a['history'], b['history'])
    def test_optimum_by_brute_force(self):
        o = exact_discrete_optimum()
        self.assertTrue(0 <= o['chromosome'] <= MAX_INT)
        self.assertAlmostEqual(o['fitness'], fitness(o['chromosome']))

if __name__ == '__main__':
    unittest.main()
