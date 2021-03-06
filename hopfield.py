import json
import random
import os
import numpy as np
import perceptron as p
import utils


# Build pattern array from txt file with '*', ' '
def get_pattern_array(filename: str) -> np.ndarray:
    pattern = []
    with open(filename) as file:
        for line in file:
            for car in line.strip('\n'):
                pattern.append(1 if car == '*' else -1)
    return np.array(pattern)

# Build pattern matrix from directory, len(pattern)
def pattern_matrix(dirpath: str, N: int) -> np.ndarray:
    file_list = os.listdir(pattern_dirpath)
    patterns = np.zeros((N, len(file_list)), dtype=int)
    letter_list = []
    for i, pattern_filename in enumerate(file_list):
        letter_list.append(pattern_filename)
        pattern_filepath = pattern_dirpath + '/' + pattern_filename
        patterns[:, i] = get_pattern_array(pattern_filepath)
    return letter_list, patterns

# Print side x side pattern from side x side lengthed array
def print_pattern(pattern: np.ndarray, side: int):
    for i in range(side * side):
        car = '*' if pattern[i] > 0 else ' '
        print(car, end='')
        if i != 0 and (i + 1) % side == 0:
            print('\n', end='')

# Generate pattern mutation from pattern using pm probability
def get_mutated_pattern(pattern: np.ndarray, pm: float) -> np.ndarray:
    mut_pattern = np.copy(pattern)
    for i in range(len(mut_pattern)):
        if random.random() < pm:
            mut_pattern[i] = mut_pattern[i] * -1
    return mut_pattern


# Pattern length is fixed
SIDE = 5
N = SIDE * SIDE
RED = "#FF0000"
GREEN = "#00FF00"

# read config file
with open("config.json") as file:
    config = json.load(file)

pattern_dirpath: str = config["hopfield"]["pattern_dir"]
pm: float = config["hopfield"]["mutation_prob"]
max_iterations: int = config["hopfield"]["max_iterations"]
plot_boolean: bool = config["plot"]

# Build pattern matrix, with [e1 e2 e3 ...], len(ei) = N
letter_list, patterns = pattern_matrix(pattern_dirpath, N)

# Calculate dot product between letters --> Closer to 0, more ortogonal
for i in range(len(patterns[0])):
    for j in range(i + 1, len(patterns[0])):
        print(f'Producto interno entre {letter_list[i]} y {letter_list[j]}: {np.dot(patterns[:, i], patterns[:, j])}')

# Get query pattern from available patterns
query_num = random.randint(0, patterns.shape[1] - 1)
query_pattern = get_mutated_pattern(patterns[:, query_num], pm)

# Initialize Hopfield perceptron
algo: p.HopfieldPerceptron = p.HopfieldPerceptron(patterns, query_pattern)

# Print initial query
print('------------------')
print_pattern(query_pattern, SIDE)
print('------------------')

# Iterate over hopfield
s: np.ndarray
count: int = 0
while not algo.is_over() and count < max_iterations:
    s = algo.iterate()
    print_pattern(s, SIDE)
    print('------------------')
    count += 1

# Print ending motive
if count >= max_iterations:
    print(f'Se ha alcanzado el {utils.string_with_color("l??mite de iteraciones", RED)} (probablemente por loop). Saliendo...')
else:
    spurious = True
    for i in range(patterns.shape[1]):
        if np.array_equal(s, patterns[:, i]):
            (correct, color) = ("es correcto", GREEN) if letter_list[i] == letter_list[query_num] else ("es incorrecto", RED)
            print(f'El estado final {utils.string_with_color(correct, color)}. Coincide con {letter_list[i]} ({count} iter) y era {letter_list[query_num]}.')
            spurious = False
            break
    if spurious:
        print(f'El estado final {utils.string_with_color("es esp??reo", RED)}. Deber??a coincidir con {letter_list[query_num]}.')

# Print energy values
print(f'\nEnergy values: \n{algo.energy}')

# If plot_boolean is true, generate plots
if plot_boolean:
    # Init plotter
    utils.init_plotter()

    # Plot energy = f(t)
    utils.plot_values(range(len(algo.energy)), 'iteration', algo.energy, 'energy', sci_y=False, ticks=range(len(algo.energy)))

    # Hold execution to show plots
    utils.hold_execution()
