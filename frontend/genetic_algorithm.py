'''
Descrição: Classe genética para um algoritmo genético
Autor: Jorge Rossi
Data: 23/11/2019
'''

import abc
import random
import copy


class Individual:
    def __init__(self, genome):
        self.genome = genome
        self.fitness = 0


class GeneticAlgorithm(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, population_size=50, mutation_rate=0.01, crossover_rate=0.5, tournament_k=3, inject_individual_callback=None, check_solution_callback=None, input_queue=None,  extra=None):
        super().__init__()
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.tournament_k = tournament_k
        self.inject_individual_callback = inject_individual_callback
        self.check_solution_callback = check_solution_callback
        self.extra = extra
        self.input_queue = input_queue

        self.population = []

        for i in range(population_size):
            self.population.append(self.make_individual())

        self.best = self.population[0]

    @abc.abstractmethod
    def make_individual(self):
        raise NotImplementedError

    @abc.abstractmethod
    def fitness(self, a):
        raise NotImplementedError

    def _select(self):

        if self.inject_individual_callback is not None:
            tmp = self.inject_individual_callback()
            if tmp is not None:
                self.population.append(tmp)

        for i in range(len(self.population)):
            self.population[i].fitness = self.fitness(self.population[i])

        new_population = []

        for i in range(len(self.population)//2):
            selected_for_tournament = []
            for j in range(self.tournament_k):
                rnd = random.choice(self.population)
                selected_for_tournament.append(rnd)

            selected_for_tournament = sorted(
                selected_for_tournament, key=lambda k: k.fitness, reverse=True)

            new_population.append(selected_for_tournament[0])

        self.population = sorted(
            new_population, key=lambda k: k.fitness, reverse=True)

    @abc.abstractmethod
    def crossover(self, a, b):
        raise NotImplementedError

    @abc.abstractmethod
    def mutate(self, a):
        raise NotImplementedError

    def _crossover(self):
        childs = []
        for i in range(len(self.population)):
            a = self.population[random.randrange(len(self.population))]
            b = self.population[random.randrange(len(self.population))]

            if random.random() < self.crossover_rate:
                childs.extend(self.crossover(a, b))
            else:
                childs.extend([a, b])
        self.population = childs

    def _mutate(self):
        for i in range(len(self.population)):
            self.population[i] = self.mutate(self.population[i])

    def run(self, best_solution_callback=None):
        i = 0
        while True:

            try:
                data = self.input_queue.get(False)
                if data["action"] == "stop":
                    return
                elif data["action"] == "insert":
                    print("Inserindo indivíduo de outro processo")
                    self.population.append(Individual(data["genome"]))

            except:
                pass
            finally:
                if i % 100 == 0:
                    print("Geração", i)
                self._select()

                if self.population[0].fitness > self.best.fitness:
                    self.best = copy.deepcopy(self.population[0])

                    if best_solution_callback is not None:
                        best_solution_callback(self.best)

                    if self.check_solution_callback is not None:
                        stop = self.check_solution_callback(self.best)

                        if stop:
                            break

                self._crossover()
                self._mutate()
                i += 1
