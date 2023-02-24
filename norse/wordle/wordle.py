# ******************************
# LEG 07: Lake Chad
# Wordle
#
# [wordle-words]: list of wordle of words available to all
# [team-wordle-words-taken]: list of wordle words owned by a team
# [team-wordle-words-wrong]: list of wordle words owned by a team
# [team-wordle-words-curr]: current wordle word team is solving
# [team-wordle-words-try]: current wordle word attempt number
# [team-wordle-guess]: TRUE if guessing, otherwise FALSE if selecting a booth
# ******************************
import typing

from replit import db

# LEG 07 Wordle Words
wordleRange = 30
wordleTryLimit = 4
wordleWinCondition = 3
wordleBoothVisitLimit = 15
wordleWords = [
  'FLICK',
  'DIZZY',
  'CHARM',
  'GYROS',
  'CANAL',
  'DONUT',
  'GROPE',
  'ANVIL',
  'INGOT',
  'ELDER',
  'PASTA',
  'CHUNK',
  'FENCE',
  'GORGE',
  'PARTY',
  'POUCH',
  'SPADE',
  'DEPTH',
  'SNUCK',
  'BRISK',
  'BROOM',
  'SLIME',
  'GAUZE',
  'APPLE',
  'ERROR',
  'THYME',
  'MELON',
  'AZURE',
  'JOINT',
  'WEARY'
]

def displayWordleLetters(data):
  for index in range(0, 5):
    if data[index] == "*":
      data[index] = ":green_square:"
    elif data[index] == "-":
      data[index] = ":orange_square:"
    else:
      data[index] = ":white_large_square:"
  return ' '.join(data)

def find_all_char_positions(word: str, char: str) -> typing.List[int]:
  """Given a word and a character, find all the indices of that character."""
  positions = []
  pos = word.find(char)
  while pos != -1:
      positions.append(pos)
      pos = word.find(char, pos + 1)
  return positions

# test cases for find_all_char_positions
# find_all_char_positions("steer", "e") => [2, 3]
# find_all_char_positions("steer", "t") => [1]
# find_all_char_positions("steer", "q") => []

def compare(expected: str, guess: str) -> typing.List[str]:
    """Compare the guess with the expected word and return the output parse."""
    # the output is assumed to be incorrect to start,
    # and as we progress through the checking, update
    # each position in our output list
    output = ["_"] * len(expected)
    counted_pos = set()

    # first we check for correct words in the correct positions
    # and update the output accordingly
    for index, (expected_char, guess_char) in enumerate(zip(expected, guess)):
        if expected_char == guess_char:
            # a correct character in the correct position
            output[index] = "*"
            counted_pos.add(index)

    # now we check for the remaining letters that are in incorrect
    # positions. in this case, we need to make sure that if the
    # character that this is correct for was already
    # counted as a correct character, we do NOT display
    # this in the double case. e.g. if the correct word
    # is "steer" but we guess "stirs", the second "S"
    # should display "_" and not "-", since the "S" where
    # it belongs was already displayed correctly
    # likewise, if the guess word has two letters in incorrect
    # places, only the first letter is displayed as a "-".
    # e.g. if the guess is "floss" but the game word is "steer"
    # then the output should be "_ _ _ - _"; the second "s" in "floss"
    # is not displayed.
    for index, guess_char in enumerate(guess):
        # if the guessed character is in the correct word,
        # we need to check the other conditions. the easiest
        # one is that if we have not already guessed that
        # letter in the correct place. if we have, don't
        # double-count
        if guess_char in expected and \
                output[index] != "*":
            # first, what are all the positions the guessed
            # character is present in
            positions = find_all_char_positions(word=expected, char=guess_char)
            # have we accounted for all the positions
            for pos in positions:
                # if we have not accounted for the correct
                # position of this letter yet
                if pos not in counted_pos:
                    output[index] = "-"
                    counted_pos.add(pos)
                    # we only count the "correct letter" once,
                    # so we break out of the "for pos in positions" loop
                    break
    # return the list of parses
    return output

def wordle_main_init():
  db["wordle-words"] = wordleWords

def wordle_player_init(name):
  db[name + "-wordle-start"] = True
  db[name + "-wordle-words-taken"] = []
  db[name + "-wordle-words-wrong"] = []
  db[name + "-wordle-words-curr"] = -1
  db[name + "-wordle-words-try"] = 0
  db[name + "-wordle-guess"] = False
  db[name + "-wordle-visited"] = 0

def select_mirror(name, boothNo):
  # *************** SELECT MIRROR ****************************

  if db[name + "-wordle-start"] != True:
    return ":warning: **" + name + "**, begin this game by typing: `$start-polishing`"
    
  if db[name + "-wordle-guess"] == True:
    return ":warning: **" + name + "**, you must solve your current word before switching!"

  if len(db[name + "-wordle-words-taken"]) >= wordleWinCondition:
    return ":warning: **" + name + "**, you already completed this game!"
  
  if boothNo < 1 or boothNo > wordleRange:
    return ":warning: **" + name + "**, invalid input."

  wordleWordAnswer = db["wordle-words"][boothNo - 1]

  if boothNo in db[name + "-wordle-words-wrong"]:
    return ":warning: **" + name + "**, you are not allowed in this mirror. Choose another."

  if wordleWordAnswer == "":
    return ":warning: **" + name + "**, this booth is already won by another team! Choose another mirror."

  db[name + "-wordle-words-curr"] = boothNo
  db[name + "-wordle-words-try"] = wordleTryLimit
  db[name + "-wordle-guess"] = True
  
  return "**" + name + "**, you selected word Mirror #" + str(boothNo) + ". Your team may now start solving."

def wordle_solve(name, wordGuess):

  if db[name + "-wordle-start"] != True:
    return ":warning: **" + name + "**, begin this game by typing: `$start-polishing`"
  
  if db[name + "-wordle-guess"] == False or db[name + "-wordle-words-curr"] == -1:
    return ":warning: **" + name + "**, you must first select a mirror!"

  currWordleBoothNo = db[name + "-wordle-words-curr"]
  currWordleTryNo = db[name + "-wordle-words-try"]

  wordCorrect = db["wordle-words"][currWordleBoothNo - 1]

  if wordCorrect == "":
    db[name + "-wordle-words-curr"] = -1
    db[name + "-wordle-words-try"] = 4
    db[name + "-wordle-guess"] = False
    return ":warning: **" + name + "**, this word is taken. Choose another mirror."

  if len(wordGuess) != 5 or wordGuess.isalpha() == False:
    return ":warning: **" + name + "**, invalid input."
  
  # Correct input, let us check
  guessList = compare(wordCorrect, wordGuess)
  win = guessList.count("*") == 5

  currWordleTryNo = currWordleTryNo - 1
  db[name + "-wordle-words-try"] = currWordleTryNo
  outputMsg = "**" + name + "**, you guessed **" + wordGuess + "**:\n"
  outputMsg = outputMsg + displayWordleLetters(guessList) + "\n"

  if win == True:
    db["wordle-words"][currWordleBoothNo - 1] = ""
    correctWords = db[name + "-wordle-words-taken"]
    correctWords.append(str(currWordleBoothNo) + " - " +  wordCorrect)
    db[name + "-wordle-words-taken"] = correctWords
    db[name + "-wordle-guess"] = False
    db[name + "-wordle-words-curr"] = 0
    db[name + "-wordle-words-try"] = 4
    if len(correctWords) < wordleWinCondition:
      outputMsg = outputMsg + "Congratulations! Go to the next mirror!\n"
    else:
      outputMsg = outputMsg + "Congratulations, **" + name + "**!\n"
    outputMsg = outputMsg + "# of Correct Words: " + str(len(correctWords)) + " out of " + str(wordleWinCondition) + "\n"
  else:
    if currWordleTryNo <= 0:
      wrongWords = db[name + "-wordle-words-wrong"]
      wrongWords.append(currWordleBoothNo)
      db[name + "-wordle-words-wrong"] = wrongWords
      db[name + "-wordle-guess"] = False
      outputMsg = outputMsg + "**" + name + "**, you have reached the try limit for this word! Find another station!\n"
      attempts = db[name + "-wordle-visited"]
      db[name + "-wordle-visited"] = attempts + 1
      outputMsg = outputMsg + "# of Correct Words: " + str(len(db[name + "-wordle-words-taken"])) + " out of " + str(wordleWinCondition) + "\n"
    else:
      outputMsg = outputMsg + "Attempts left: **" + str(currWordleTryNo) + "**"

  return outputMsg

  