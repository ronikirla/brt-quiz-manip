# Ask user for a desired nature and then simulate the RNG + quiz code of the game to find windows of consecutive RNG seeds with desired questions.
# If the question is in a desired category, it is enough for the yield to be equal to MINIMUM_DESIRED_POINTS, otherwise the yield must be greater.

import json
import rng

NUM_SEEDS = 0x100000000 / 2 # RNG gets called twice so only half of the 32-bit space
PROGRESS_REPORT_TRESHOLD = NUM_SEEDS // 100
MINIMUM_DESIRED_POINTS = 2
MIN_ANSWER_TIME = 20
MAX_ANSWER_TIME = 30
PRINTING_TRESHOLD = 0.9
SEED_BUFFER_SIZE = 3600

with open("questions.json") as fp:
    questions = json.load(fp)

natures = input("Desired nature(s): ").lower().split(",")

try:
    categories = list(map(lambda x: int(x), input("Desired categories: ").split(",")))
except ValueError:
    categories = []

inp = input("Starting seed: ")
try:
    rng.gRngState = int(inp)
except ValueError:
    rng.gRngState = int(inp, 16)

window_width = int(input("Window width: "))

advances = 0
consecutive = 0
record = 0
seed_buffer = []
progress = 0

desired_questions = []
acceptable_questions = []
for i, question in enumerate(questions):
    desired_category = len(categories) == 0 or question["group"] in categories
    for nature in natures:
        for answer in question["answers"].values():
            if nature in answer:
                if i not in acceptable_questions:
                    acceptable_questions.append(i)
                if answer[nature] >= MINIMUM_DESIRED_POINTS and desired_category or answer[nature] > MINIMUM_DESIRED_POINTS:
                    if i not in desired_questions:
                        desired_questions.append(i)
print(f"Desired questions (total {len(desired_questions)}):")
for nature in natures:
    for question_idx in desired_questions:
        question = questions[question_idx]
        answers = question["answers"]
        print(question["string"])
        def answer_points(answer):
            data = answer[1]
            if nature in data.keys():
                return data[nature]
            else:
                return 0
        correct_answer = max(answers.items(), key=answer_points)
        # why did i spend this much effort on pretty printing
        print(f" => {correct_answer[0]}", end=" ")
        print("(", end="")
        for i,nature_string in enumerate(correct_answer[1].items()):
            print(f"{nature_string[0]} +{nature_string[1]}", end="")
            if i < len(correct_answer[1]) - 1:
                print(", ", end="")
        print(")")


def print_progress():
    print("-" * 20)
    print(f"Progress: {progress / NUM_SEEDS * 100:.0f}% ({hex(rng.gRngState)})")

asked_questions = []
while advances < NUM_SEEDS:
    if SEED_BUFFER_SIZE > 0:
        seed_buffer.append(hex(rng.gRngState))
        if len(seed_buffer) > SEED_BUFFER_SIZE:
            seed_buffer.pop(0)
    asked_question = rng.RandomCapped(len(questions))
    asked_questions.append(asked_question)
    if asked_question in desired_questions:
        consecutive += 1
    else:
        # Calculate the odds of finding any question with points in the following seeds after finding a first question manip
        if consecutive >= window_width:
            asked_question_lengths = list(map(lambda idx: len(questions[idx]["string"]), asked_questions))
            min_advances = 2 * (min(asked_question_lengths) + MIN_ANSWER_TIME)
            max_advances = 2 * (max(asked_question_lengths) + MAX_ANSWER_TIME)
            save_state = rng.gRngState
            rng.cycle(min_advances) # It takes a bit to answer the first question so skip a few advances forward
            hits = 0
            for _ in range(max_advances - min_advances):
                if rng.RandomCapped(len(questions)) in acceptable_questions:
                    hits += 1
            rng.gRngState = save_state
            ratio = hits / (max_advances - min_advances)
            if ratio > record * PRINTING_TRESHOLD:
                print("-" * 20)
                if ratio > record:
                    record = ratio
                    print("New best!")
                print(f"{'Consecutive:':14s} {consecutive}")
                print(f"{'Ratio:':14s} {ratio*100:.2f}%")
                print(f"{'Advances:':14s} {advances}")
                if SEED_BUFFER_SIZE > 0:
                    print(f"{'Starting seed:':14s} {seed_buffer[0]}")
                print(f"{'Ending seed:':14s} {hex(rng.gRngState)}")
        consecutive = 0
        asked_questions = []
    advances += 1
    progress += 1
    if progress % PROGRESS_REPORT_TRESHOLD == 0:
        print_progress()
