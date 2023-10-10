# brt-quiz-manip
**This repository contains the tools to create a personality quiz RNG-manipulation for Pokémon Mystery Dungeon: Blue Rescue Team. Additionally, it contains some pre-made manipulated save files for the most popular natures used in speedruns.**
## Pre-Made Manipulations

These manipulations are created for the US version of the game with a frame window of 5. For execution instructions, refer to the next section. If you want to make your own ones with different parameters, refer to the technical guide after that. These can probably be improved so feel free to try!
- [Hasty (DS)](/premade_manips/hasty_ds.sav)
- [Quirky (DS)](/premade_manips/quirky_ds.sav)
- [Relaxed (DS)](/premade_manips/relaxed_ds.sav)
- [Hasty (DeSmuME 0.9.11)](/premade_manips/hasty_emu.sav)
- [Quirky (DeSmuME 0.9.11)](/premade_manips/quirky_emu.sav)
- [Relaxed (DeSmuME 0.9.11)](/premade_manips/relaxed_emu.sav)

## How to Perform the Manipulation In-Game
This manipulation relies on an audio cue. For the best results, make sure that your setup does not have any audio delay. This means that you should not be listening to the game audio through a capture or a virtual audio device. On a console you would essentially turn up the volume from the speakers or listen through headphones directly connected to it.

1. Load the manipulated save file (according to your platform) using a save file manager or an emulator.
2. After booting the game, do not press any buttons as those affect the RNG. If you want to play in pixel-perfect mode on a 3DS, you can still hold start/select but need to release them quickly before the white flash ends.
3. The exception to this is L/R, you can use those buttons to skip the title screen at the end of the intro.
4. When you load into the main menu, start closely listening to the music.
5. On the first beat of the second measure, press A+B at the same time and hold them down until you get to the first question in the quiz.

This manipulation only guarantees that the first question is desirable. However, it employs some tricks to make it *more likely* to hit even more desirable questions. As a result, you should expect to get the correct nature from the quiz the majority of the time.

[Video demonstration of the manipulation](https://youtu.be/14Nf_Tt_MtU). It also shows the Lua-script  included in this repository.

## Technical Explanation: How to Create Your Own Manipulation
This game uses a fairly standard linear congrugential generator for random numbers. Thanks to a [decompilation project](https://github.com/pret/pmd-red/tree/master), the [code of the generator](https://github.com/pret/pmd-red/blob/master/src/random.c) can be easily inspected. The starting seed of the RNG is determined using the save file, and is kept even if using the in-game functionality for deleting the save. After that, the RNG is advanced either once or twice per frame, depending on inputs.

[A quiz manipulation for the sequel, Explorers of Time/Darkness/Sky](https://docs.google.com/document/d/1v8WhnH6qzFuBmy6WGALSMW32_YCgGIz3NyaibVwZAg4/edit?usp=sharing), was already discovered quite a while ago. In those games, the manipulation is pretty much trivial for two reasons: 1) the entry to the quiz can essentially be performed as a buffered input and 2) the entirety of the quiz is generated at once.

In Red/Blue Rescue team, neither of these are the case. Even though the starting seed is modifiable through a save file, there are no bufferable inputs, and the questions are generated as you go. This means that it would require frame-perfect timing (16.67 ms window!)  for every question of the quiz to always get the same result. With the button presses themselves additionally affecting the RNG, it was thought to be impossible for humans to perform.

However,  it still turns out to be very beneficial even to just manipulate the first question, which brings the required amount of frame-perfect inputs down to one. Guaranteeing just one correct question drastically increases the odds of getting a desired nature even if the rest of the quiz is random.

The second breakthrough comes from the fact that by simulating the RNG-algorithm, we can find long sequences of desired questions using brute-force. This allows us to make the frame-window of the manipulation much wider!

There's two more techniques we can use to further increase the odds of a successful quiz. First, the way the quiz works is the questions are divided into groups, with no two questions from the same group being asked. A lot of the time, there is one group that has a high amount of desired questions. We can use this information to our advantage by *not* picking that group to have the question we manipulate, as that leaves more desirable questions in the set of remaining questions that will be asked randomly. Second, the denisty of desirable questions in the seeds that follow our initial question can be analyzed. By brute-forcing over this too we can prioritize seeds that have a slightly higher likelihood of randomly running into the correct questions.

With the general explanation out of the way, we can move into the steps to create a quiz manipulation using the scripts in this repository.

### Step 1: [quiz_miner.py](quiz_miner.py)
Using this script, we can perform the heavy lifting and find the range of seeds with good questions. Honestly, this script could use a C++ implementation with parallelization but for now this one will suffice. Running it for an  extended time has diminishing returns anyway.  Some full 32-bit range runs are provided in [seed_miner_output_examples](seed_miner_output_examples/).

The script asks for the nature and desired categories. For the categories, I recommend looking in questions.json for the categories that have a single question that yields at most 2 points. For example, with Hasty these would be 6, 7, 10. The starting seed is just where the program starts searching and window width means how many consecutive desirable questions are searched for.

### Step 2: [quiz_printer.py](quiz_printer.py)
This script can be used to print a timeline of seeds and which questions they correspond to. Input the staring and ending seed given as the output of the previous step. Then specify the output filename.

### Step 3: [brt_rng.lua](brt_rng.lua)

Now it is time to figure out which seed to start from in the save file. This was perhaps the most difficult part to figure out. First, we need an offset from the moment you load the save file to the start of the quiz. This can be obtained using this Lua-script on the emulator DeSmuME. Here's what the script shows:
| Field |Explanation  |
|--|--|
| Question | The numerical index of the question that is being asked|
| Question Frame | The RNG frame (number of advances) that the question was asked on |
| Question Seed | The RNG seed that resulted in the asked question |
| Advances | The number of RNG advances that happened in this frame |
| Offset | Difference in number of advances from the expected 2 per frame (can be changed) |
| Frame | Current RNG frame (number of total advances)
| A press | The RNG frame of the last A-button press |

Here we are primarily interested in the question frame. This tells us the offset, we just need a consistent way to always hit the same frame. For this, I recommend taking the same steps as in the ready-made manipulations, but you could experiment with other methods, such as metronome timers.

You can copy my offset to skip this step, but it is platform-dependent due to varying load times. Using the US rom, DeSmuME 0.9.11 with the [optimal speedrun settings](https://docs.google.com/document/d/10J0slaIIrFMQxtR2daUAAVCgiexSQkAaTzEePZ3DyDc/edit?usp=sharing) and the timing method described above,  the number of advances is 818. DS is around 7 frames slower.

### Step 4: [seed_inverter.py](seed_inverter.py)
 Not only do you need the offset, but also the seed the game starts from is not simply the one inserted into the save file. Instead, the game calls the RNG twice and uses the results of those calls to re-seed it. So, an inverse function of this is implemented in this script.
 1. Find the midpoint of the consecutive questions from the output generated in step 2. You can Ctrl+F "ENDING SEED" to get to the last one.
 2. Go up as many lines as your discovered offset (using VSCode ctrl+G for exmaple).
 3. Input the seed number on the line you end up at into this script.
 4. Not every seed can be inverted. If unsuccessful, you could try an adjacent seed in the seed_printer output or generate an entirely different seed range based on what you found in step 1.

### Step 5: Input the Seed Into the Save File

Now that we finally have the desired seed, it is time to create a save file with the seed. Simply just hex-editing the seed into the save does not work, because it would cause a checksum mismatch. A more sophisticated solution could be developed for this, but the simplest way to achieve this is to create a cheat code in DesMuME that freezes the RNG and then deleting the save file with that code active.

1. Go to cheats and add an internal 4-byte code with the address `0x020E9FC0` (US) or `0x020DF704` (EU) and the value that was given as the "Desmume code" output of the previous step.
2. Make sure you are in a save file with actual data in it that can be deleted. Load any such save state/file if not.
3. Reset the game and do not touch any buttons as to not advance the RNG. If you press a button, it might change the number of advances per frame to become 2 instead of 1. This causes the result to be wrong as the cheat code only resets the value each frame.
4. Using the touchscreen, navigate through the main menu to delete your save data. Now the "deleted save" contains the correct seed and you can export it.
5. Remember to disable the cheat afterwards, otherwise you will falsely always hit the manip (and get the same RNG overall).
6. You can use the Lua-script to check whether the game loads the correct seed from the file, as it prints the initial seed to the console.


### Step 6: Verify It Works
Perform the manipulation, trying to hit as close as you can to the same frame as you did when determining the offset. You can use the output of quiz_printer.py to see which frame you hit. This is how I found the difference between emulator and console. Additionally, if you are performing the manipulation on an emulator, you can use brt_rng.lua to directly tell you which frame you hit.

If it does not work, you either made an error or got unlucky with creating the manipulation as there is a variance of about +/- 5 RNG calls before the quiz depending on the frame you hit. You can see this by paying attention to the offset value in the Lua-script. Addressing this is currently out of my skillset and the best solution is to just try to adjust the offset or the frame window of the manipulation. It is always possible to create a manipulation with a really wide frame window, but then the odds of finding good follow-up questions will not be quite as high.
