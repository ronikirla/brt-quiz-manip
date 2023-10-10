# For a given starting seed, figure out the seed to store in the save data using brute force

import rng

NUM_SEEDS = 0x100000000
PROGRESS_REPORT_TRESHOLD = NUM_SEEDS // 100

inp = input("Output seed: ")
try:
    target = int(inp)
except ValueError:
    target = int(inp, 16)

msb = target >> 16
for i in range(0x10000):
    testSeed = (msb << 16) | i
    rng.gRngState = testSeed
    nextSeed = rng.Random16()
    if msb << 16 | nextSeed == target:
        rng.cycle(-1)
        print(f"Input seed: {hex(rng.gRngState)}")
        rng.cycle(-1)
        print(f"Desmume code: {rng.gRngState}")
        exit()

print("Could not find input seed")