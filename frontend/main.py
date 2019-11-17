import requests
import redis
import time
import threading
import json
import word_algorithm
import random
from queue import Queue
from tabulate import tabulate

r = redis.Redis(host='127.0.0.1', port=6379)
p = r.pubsub()

print("==============================")
print('Distributed Genetic Algorithms')
print("==============================")

name = input('Digite um nome: ')

print("\nComandos: ")
print(" list        -> listar tarefas")
print(" add [name]  -> criar tarefa [tsp|word]")
print(" join [id]   -> participar de uma tarefa")
print(" exit        -> sair da aplicação\n\n")

cmd = ''

tasks = []
best_solutions = []
is_solving = False


def genetic_thread(task_id, alg):

    def best_solution_callback(a):
        global best_solutions
        print("Nova solução encontrada por mim! Fitness: {}".format(
            a.fitness))
        if len(best_solutions) == 0 or a.fitness > best_solutions[-1]["fitness"]:
            # best_solutions.append(
            #     {"genome": a.genome, "fitness": a.fitness})
            # best_solutions = best_solutions[:20]

            # Publicar
            r.publish('task_' + str(task_id), json.dumps(
                {"status": "pending",  "fitness": a.fitness, "user_name": name, "genome": a.genome, "task_id": task_id}))

    alg.run(best_solution_callback=best_solution_callback)

    print(alg.best.genome)


def alg_to_id(name):
    return 1 if alg_name == 'tsp' else 2


def id_to_alg(id):
    return 'tsp' if id == 1 else 'word'


while cmd != 'exit':
    cmd = input('> ')

    if cmd.startswith('list'):
        data = requests.get('http://127.0.0.1:3333/task').json()
        tasks = data

        table = list(map(lambda k: [k["id"], k["user_name"], id_to_alg(
            k["algorithm_id"]), k["status"]], data))

        print(tabulate(table, headers=[
              "ID", "Usuário", "Algorítmo", "Status"]))

        print()

    elif cmd.startswith('add'):
        alg_name = cmd.split(' ')[1]

        requests.post('http://127.0.0.1:3333/task',
                      json={"user_name": name, "algorithm_id": alg_to_id(alg_name)})

    elif cmd.startswith('join'):
        task_id = int(cmd.split(' ')[1])
        best_solutions = requests.get(
            'http://127.0.0.1:3333/task/' + str(task_id) + '/best').json()

        print("Iniciando execução do algorítmo...")
        print("Aperte CTRL+c para sair")

        # print("Melhor solução atual: ", best_solutions)

        p.subscribe('task_' + str(task_id))

        input_queue = Queue()

        task = next(filter(lambda k: k["id"] == task_id, tasks))
        if task is not None:
            alg_id = task["algorithm_id"]

            alg = None

            population = int(input('Tamanho opulação: '))
            mutation = float(input('Taxa mutação: '))
            cross = float(input('Taxa cruzamento: '))

            if alg_id == 1:
                pass

            elif alg_id == 2:

                correct = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
                alg = word_algorithm.WordAlgorithm(
                    population, mutation, cross, 5, input_queue=input_queue, extra={"word_len": len(correct), "correct_word": correct})

            t = threading.Thread(target=genetic_thread,
                                 args=(task_id, alg))
            t.start()

            try:
                while True:
                    data = p.get_message()
                    if data and data["type"] == "message":
                        data = json.loads(data["data"].decode('utf-8'))
                        # Alguem completou
                        if data["status"] == "completed":
                            input_queue.put({"action": "stop_finished"})
                            break

                        # Alguem encontrou uma solução boa
                        else:
                            # Verificar se é melhor que as 20 salvas localmente
                            if len(best_solutions) == 0 or data["fitness"] > best_solutions[-1]["fitness"]:

                                if data["user_name"] != name:
                                    print("Nova solução encontrada por {}. Fitness: {}".format(
                                        data["user_name"], data["fitness"]))
                                best_solutions.append(
                                    {"genome": data["genome"], "fitness": data["fitness"]})
                                best_solutions = best_solutions[:20]

                                # 10% de chance de incluir na população
                                if random.random() < 0.1:
                                    input_queue.put(
                                        {"action": "insert", "genome": data["genome"]})

            except KeyboardInterrupt:
                input_queue.put({"action": "stop"})

            # for item in p.listen():
            #     print(item['data'])
