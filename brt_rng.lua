-- Use this lua script to see detailed information about the RNG and quiz data in-game
-- Question: Index/ID number of question that is currently being asekd
-- Question Frame: RNG Frame on which the question was generated
-- Question Seed: RNG Seed that resulted in the generated question
-- Advances: Number of RNG calls that happened during this frame
-- Offset: Difference in amount of advances from exepcted_advances per frame
-- Frame: Number of RNG advances total
-- A Press: Frame of your last A-button press

-- PAL 0x020DF704 NTSC 0x020E9FC0
rng_address = 0x020E9FC0
question_address = 0x021136DC
expected_advances = 2

function bytes_to_number(bytes)
    number = 0
    for i, v in ipairs(bytes) do
        number = number + v * 2^(8*(i-1))
    end
    return number
end

function init()
    prev_rng = bytes_to_number(memory.readbyterange(rng_address, 4))
    offset = 0
    frame = 0
    apress = -1
    apressed = false
    prev_question = memory.readbyte(question_address)
    question_frame = -1
    question_seed = -1
    print(string.format("Init seed: %x", prev_rng))
end

-- https://gist.github.com/MikuAuahDark/257a763f43efd00012a9afbe65932770
function dwordMultiply(a, b)
	a = a % 4294967296
	b = b % 4294967296
	local ah, al = math.floor(a / 65536), a % 65536
	local bh, bl = math.floor(b / 65536), b % 65536
	local high = ((ah * bl) + (al * bh)) % 65536
	return ((high * 65536) + (al * bl)) % 4294967296
end

-- https://github.com/pret/pmd-red/blob/master/src/random.c
function random16()
    prev_rng = dwordMultiply(1566083941, prev_rng) + 1
    return math.floor(prev_rng / 2^16)
end

function random()
    r1 = random16()
    r2 = random16()
    return (r1 * 2^16) + r2
end

init()

while true do
    emu.frameadvance()
    if joypad.get(0)["start"] and joypad.get(0)["select"] then
        init()
    end
    rng = bytes_to_number(memory.readbyterange(rng_address, 4))
    question = memory.readbyte(question_address)
    advances = 0
    while rng ~= prev_rng do
        prevprev_rng = prev_rng
        random()
        advances = advances + 1
        if advances > 10000 then
            advances = -1
            init()
            break
        end
    end
    if advances > 0 then
        offset = offset + advances - expected_advances
        frame = frame + advances
    end
    if prev_question ~= question then
        question_frame = frame - 1
        question_seed = prevprev_rng
    end
    if joypad.get(0)["A"] then
        if not apressed then
            apressed = true
            apress = frame
        end
    else
        apressed = false
    end
    prev_question = question
    gui.drawtext(0, 0, "Question: " .. question)
    gui.drawtext(0, 10, "Question Frame: " .. question_frame)
    gui.drawtext(0, 20, string.format("Question Seed: %x", question_seed))
    gui.drawtext(0, 153, "Advances: " .. advances)
    gui.drawtext(0, 163, "Offset: " .. offset)
    gui.drawtext(0, 173, "Frame: " .. frame)
    gui.drawtext(0, 183, "A Press: " .. apress)
end