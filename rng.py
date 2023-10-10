gRngState = 0

# https://github.com/pret/pmd-red/blob/master/src/random.c
def Random16():
    global gRngState
    gRngState = (1566083941 * gRngState + 1) & 0xFFFFFFFF
    # Simulate sign extension
    if gRngState > 0x7FFFFFFF:
        return 0xFFFF0000 | gRngState >> 16
    else:
        return gRngState >> 16

def Random():
    r1 = Random16()
    r2 = Random16()
    return (r1 << 16) | r2

def RandomCapped(cap):
    return (((Random() & 0xFFFF) * cap) >> 16) & 0xFFFF

# Go back 1 Random16() call
# Credit: StrikerX3
def prevRNG():
    global gRngState
    gRngState = ((gRngState - 1) * 1786162797) & 0xFFFFFFFF

# Advance arbitrary amount of calls forwards or backwards
def cycle(value):
    if value > 0:
        while value > 0:
            Random()
            value -= 1
    elif value < 0:
        while value < 0:
            for _ in range(2):
                prevRNG()
            value += 1