import json
import random
import discord
from replit import db

jestersStats = json.load(open('jesters-stats.json'))

# Leg 01 Global Variables
suits = ['hearts', 'spades', 'diamonds', 'clubs']


# Draws a card of chosen suit. Randomly generates a number from 1 to 13.
# $draw-hearts
# $draw-diamonds
# $draw-clubs
# $draw-spades
def draw_card(suit):
    if suit not in suits:
        raise ValueError('Choose a valid suit!')
    else:
        suitID = suits.index(suit)

    value = random.randrange(1, 14)
    return (value, suitID)


# Function to save drawn card
def save_card(name, card):
    value = card[0]
    suit = card[1]
    key = name + "-01-" + str(suit)
    db[key] = value
    return


# Style card
def style_card(card):
    faceCards = ['J', 'Q', 'K']
    value = str(card[0] if card[0] != 1 else "A") if card[0] < 11 else faceCards[card[0]-11]
    suit = card[1]
    return value + ":" + suits[suit] + ":"


# Function to get all cards drawn
def review_cards(name):
    faceCards = ['J', 'Q', 'K'] 
  
    if db[name + '-01-0'] == 0:
      heartValue = 'None'
    elif db[name + '-01-0'] > 10:
      heartValue = faceCards[db[name + '-01-0'] - 11]
    elif db[name + '-01-0'] == 1:
      heartValue = 'A'
    else:
      heartValue = str(db[name + '-01-0'])

    if db[name + '-01-1'] == 0:
      spadeValue = 'None'
    elif db[name + '-01-1'] > 10:
      spadeValue = faceCards[db[name + '-01-1'] - 11]
    elif db[name + '-01-1'] == 1:
      spadeValue = 'A'
    else:
      spadeValue = str(db[name + '-01-1'])

    if db[name + '-01-2'] == 0:
      diamondValue = 'None'
    elif db[name + '-01-2'] > 10:
      diamondValue = faceCards[db[name + '-01-2'] - 11]
    elif db[name + '-01-2'] == 1:
      diamondValue = 'A'
    else:
      diamondValue = str(db[name + '-01-2'])

    if db[name + '-01-3'] == 0:
      clubValue = 'None'
    elif db[name + '-01-3'] > 10:
      clubValue = faceCards[db[name + '-01-3'] - 11]
    elif db[name + '-01-3'] == 1:
      clubValue = 'A'
    else:
      clubValue = str(db[name + '-01-3'])

    embedMsg = discord.Embed(title=":game_die: **" + name +
                             "'s Current Deck** :game_die:",
                             description="",
                             color=0x0F0000)

    outputMsg = ':hearts: - ' + heartValue + '\n'
    outputMsg = outputMsg + ':spades: - ' + spadeValue + '\n'
    outputMsg = outputMsg + ':diamonds: - ' + diamondValue + '\n'
    outputMsg = outputMsg + ':clubs: - ' + clubValue + '\n'

    if 'None' in (heartValue, spadeValue, diamondValue, clubValue):
        outputMsg = outputMsg + '\nNot ready for battle!'
    elif 'None' not in (heartValue, spadeValue, diamondValue, clubValue):
        outputMsg = outputMsg + 'Your deck is now complete. If satisfied, lock it using ```$deck-ready```'
    else:
        outputMsg = outputMsg + 'Your card is now ready. Choose a jester to challenge using ```$jester-x```'

    embedMsg.add_field(name=name, value=outputMsg, inline=False)

    return embedMsg


# Reset cards
def reset_cards(name):
    db[name + '-01-lock'] = 0
    db[name + '-01-0'] = 0
    db[name + '-01-1'] = 0
    db[name + '-01-2'] = 0
    db[name + '-01-3'] = 0
    return


# Check if eligible for battle
def check_cards(name):
    return not (db[name + '-01-0'] == 0 or db[name + '-01-1'] == 0
                or db[name + '-01-2'] == 0 or db[name + '-01-3'] == 0)


# Lock cards (name)
def lock_cards(name):
    db[name + '-01-lock'] = 1


# Check if locked
def lock_check_cards(name):
    return db[name + '-01-lock'] == 1


# Challenge jester. Returns json.
def challenge(name, jesterNo):
    # Retrieve jester stats
    jesterStats = jestersStats[jesterNo]
    try:
        targetWins = 3 if db[name + '-01-rb'] else 4
    except:
        targetWins = 4
    valueHearts = db[name + '-01-0']
    valueSpades = db[name + '-01-1']
    valueDiamonds = db[name + '-01-2']
    valueClubs = db[name + '-01-3']
    statusHearts = 1 if valueHearts > jesterStats[0] else 0
    statusSpades = 1 if valueSpades > jesterStats[1] else 0
    statusDiamonds = 1 if valueDiamonds > jesterStats[2] else 0
    statusClubs = 1 if valueClubs > jesterStats[3] else 0
    statusAll = statusHearts + statusSpades + statusDiamonds + statusClubs >= targetWins

    embedMsg = discord.Embed(title=":black_joker: **" + name +
                             "'s Challenge Results** :black_joker:",
                             description="",
                             color=0x0F0000)
    embedMsg.add_field(name='Enemy',
                       value="Jester #" + str(jesterNo),
                       inline=False)
    if statusAll:
        outputMsg = "Congratulations! You have defeated the jester!"
        db['jester-' + jesterNo] = name
        db[name + '-01-win'] = True
    else:
        reset_cards(name)
        outputMsg = "Oh no! You lost! You lose all your cards to the jester. Try again!"
    embedMsg.add_field(name='Results', value=outputMsg, inline=False)

    outputMsg = style_card((valueHearts, 0)) + " - " + (
        "WIN :white_check_mark:" if statusHearts else "LOSE :x:") + "\n"
    outputMsg = outputMsg + style_card((valueSpades, 1)) + " - " + (
        "WIN :white_check_mark:" if statusSpades else "LOSE :x:") + "\n"
    outputMsg = outputMsg + style_card((valueDiamonds, 2)) + " - " + (
        "WIN :white_check_mark:" if statusDiamonds else "LOSE :x:") + "\n"
    outputMsg = outputMsg + style_card((valueClubs, 3)) + " - " + (
        "WIN :white_check_mark:" if statusClubs else "LOSE :x:") + "\n"

    embedMsg.add_field(name='Breakdown', value=outputMsg, inline=False)
    embedMsg.add_field(name='Target',
                       value=str(targetWins) + " suits to beat.",
                       inline=False)

    output = {"statusAll": statusAll, "embedMsg": embedMsg}
    return output


# Free all jesters.
def jesters_reset():
    for x in range(1, 21):
        db['jester-' + str(x)] = ""
    return

# Review all jesters
def review_jesters():
  embedMsg = discord.Embed(title=":black_joker: **Jester's Review** :black_joker:",
                             description="",
                             color=0x0F0000)
  defeatedMsg = ""
  freeMsg = ""
  for x in range(1, 21):
    if db['jester-' + str(x)] != "":
      defeatedMsg = defeatedMsg + "Jester " + str(x) + " - defeated by " + db['jester-' + str(x)] + "\n"
    else:
      freeMsg = freeMsg + str(x) + " "
      
  embedMsg.add_field(name = "Available Jesters", value=freeMsg, inline=False)
  embedMsg.add_field(name = "Defeated Jesters", value=defeatedMsg, inline=False)

  return embedMsg
    


# Initialize all players
def player_init(name):
    db[name + '-01-lock'] = 0
    db[name + '-01-0'] = 0
    db[name + '-01-1'] = 0
    db[name + '-01-2'] = 0
    db[name + '-01-3'] = 0
    db[name + '-01-rb'] = False
    db[name + '-01-win'] = False
    return


# Sets RB Advantage
def rb_advantage(name):
    db[name + '-01-rb'] = True
    embedMsg = discord.Embed(title="**" + name + "'s Roadblock Advantage**",
                             description="",
                             color=0xBE1600)
    outputMsg = "**" + name + "**, you may now only beat three (3) jesters instead of 4!"
    embedMsg.add_field(name='Congratulations!', value=outputMsg, inline=False)
    return embedMsg
