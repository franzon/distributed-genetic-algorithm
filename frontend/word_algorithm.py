import genetic_algorithm


import string
import random


class WordAlgorithm(genetic_algorithm.GeneticAlgorithm):
    def make_individual(self):
        s = ''
        for i in range(self.extra["word_len"]):
            s += random.choice(string.ascii_lowercase + ' ')
        return genetic_algorithm.Individual(s)

    def fitness(self, a):
        score = 0
        for i in range(len(a.genome)):
            if a.genome[i] == self.extra["correct_word"][i]:
                score += 1
        return score

    def crossover(self, a, b):
        point = random.randrange(len(a.genome))
        x = a.genome[:point] + b.genome[point:]
        y = b.genome[:point] + a.genome[point:]
        return [genetic_algorithm.Individual(x), genetic_algorithm.Individual(y)]

    def mutate(self, a):
        for i in range(len(a.genome)):
            if random.random() < self.mutation_rate:
                x = random.choice(string.ascii_lowercase + ' ')
                a.genome = a.genome[:i] + x + a.genome[i + 1:]

        return a
