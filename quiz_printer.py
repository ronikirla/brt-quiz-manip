# Input the starting and ending seed of the quiz miner program here to create a "timeline" file of the quiz questions.
# Useful to figure out which seed to boot the game from and which seed you landed on in the quiz.

import json
import rng

MAX_LINES = 100000
LINES_AFTER_END = 1000

with open("questions.json") as fp:
    questions = json.load(fp)

def ask_seed(msg):
    inp = input(msg)
    try:
        return int(inp)
    except ValueError:
        return int(inp, 16)

rng.gRngState = ask_seed("Starting seed: ")
ending_seed = ask_seed("Ending seed: ")
filename = input("Filename: ")
if filename.split(".")[-1] != "txt":
    filename = filename + ".txt"

advances = 0
try:
    with open(filename, "w") as fp:
        print("Writing to file...")
        end = 0
        while end < LINES_AFTER_END:
            seed = rng.gRngState
            question = questions[rng.RandomCapped(len(questions))]
            if rng.gRngState == ending_seed:
                fp.write("--- ENDING SEED ---\n")
            fp.write(f"{seed:10d} ({hex(seed):10s}): {question['string']}\n")
            advances += 1
            if rng.gRngState == ending_seed or end > 0:
                end += 1
            elif advances > MAX_LINES:
                print("Warning: Did not succesfully run into the ending seed. Terminating.")
                exit()
except OSError:
    print("Encountered an error while writing to file.")
    exit()

print(f"Successfully wrote to file {filename}")