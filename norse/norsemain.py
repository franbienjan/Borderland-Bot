import json
import random
import discord
import utils.utils
import norse.wordle.wordle
from replit import db
from datetime import datetime

odinLessonsJson = json.load(open('norse-odin-lesson.json'))
weaponsJson = json.load(open('norse-items.json'))
landsJson = json.load(open('norse-rooms.json'))
marketItemsJson = json.load(open('norse-market-items.json'))
finalItemsJson = json.load(open('norse-final-items.json'))

# DB list
# norse-[name]-location = String. Current location of player.
# norse-[name]-items = Array. Current items of player.
# norse-[name]-money = Integer. Current money (kroner) of player.
# norse-[name]-crystals = Integer. Current items.
# norse-[name]-horse = Data. Exp = Integer; Age = String?
# norse-[name]-frozen = Boolean. If player is frozen, bot will ignore him.
# norse-[name]-frozenreason = String. The reason why player is frozen.
# -nidhogg-hp = Integer. HP of Nidhogg
# -found-tyr = Boolean. If tyr has been found already

# Crystals list:
# Crystal of ASGARD == obtained by defeating Idun
# Crystal of JOTUNHEIM == obtained by defeating Nidhogg and the fateweavers
# Crystal of
validCrystals = [
    'ASGARD', 'JOTUNHEIM', 'MIDGARD', 'NIDAVELLIR', 'HEL', 'MUSPELHEIM',
    'ALFHEIM', 'NIFLHEIM', 'VANAHEIM'
]

# Initialize. Doing this will reset everything.
async def norse_welcome(guild, author):
    name = author.display_name
    db["norse-" + name + "-location"] = "ASGARD"  #Default Asgard
    db["norse-" + name + "-items"] = [] #[]
    db["norse-" + name + "-money"] = 3000 #3000
    db["norse-" + name + "-crystals"] = [] #[]
    db["norse-" + name + "-horse-growth"] = -1 #-1
    db["norse-" + name + "-horse-exp"] = -1 #-1
    db["norse-" + name + "-frozen"] = False #False
    db["norse-" + name + "-frozenreason"] = "" #""
    db["norse-" + name + "-nidhogg-hp"] = 500 #500
    db["norse-" + name + "-hel-hp"] = 100 #100
    db["norse-" + name + "-found-tyr"] = False
    db["norse-" + name + "-husband"] = "" #""
    db["norse-" + name + "-trigger-ragnarok"] = False #False
    db["norse-" + name + "-faith"] = 0 #0
    db["norse-" + name + "-spear-imbue"] = "" #""
    db["norse-" + name + "-unlocked-locations"] = ["ASGARD"] #["ASGARD"]
    db["norse-" + name + "-hay"] = 0 #0
    db["norse-" + name + "-gysahl"] = 0 #0
    db["norse-" + name + "-cavern-loop"] = -1 #-1
    db["norse-" + name + "-sleipnir-gallop"] = -1 #-1

    # Give viewing access to ASGARD, MIDGARD, JOTUNHEIM, and MUSPELHEIM
    await utils.utils.add_role(guild, author, landsJson["ASGARD"]["roleId"])


# Initialize Gold Fountain. This is an admin function.
def norse_gold_init():
    time_now = datetime.now()
    current_hour = time_now.strftime("%H")
    current_minute = time_now.strftime("%M")
    db["norse-gold-fountain-hour"] = int(current_hour)
    db["norse-gold-fountain-minute"] = int(current_minute)
    norse.wordle.wordle.wordle_main_init()

    #I'm cheating this and also adding woodlands storing
    db["norse-woodlands-answer"] = []
    print(db["wordle-words"])
    return
  
# Main dispatcher
async def norse_main(data):

    channel = data.channel
    message = data.content
    author = data.author
    name = author.display_name

    playerData = get_player_data(name)

    if message == "$show-player-stats":
      embedReply = build_player_data(playerData)
      await channel.send(embed=embedReply)
      return

    # Block frozen players
    if (playerData["frozen"] == True):
        result = review_freeze(playerData, message)
        if result == False:
            await channel.send("**" + playerData["name"] +
                               "**, you are currently disabled due to: " +
                               playerData["frozenreason"])
            return

    # Dispatch to current room
    if playerData["location"] == 'ASGARD':

        if message == "$visit-halltreasure":
            await channel.send(visit_halltreasure())
            return

        if message == "$visit-valhalla":
            valhallaText = visit_valhalla()
            await channel.send(valhallaText[0])
            await channel.send(valhallaText[1])
            return

        if message == "$trigger-ragnarok":
            await channel.send(trigger_ragnarok(playerData))
            return

        if message == "$odin-lesson":
            lessonText = odin_lesson()
            await channel.send(lessonText)
            return

        if message == "$thor-shock":
            reply = thor_shock(playerData)
            await channel.send(reply)
            return

        if message == "$sif-cut":
            reply = sif_cut(playerData)
            await channel.send(reply)
            return

        if message.startswith("$find-tyr-"):
            slot = message.split('$find-tyr-', 1)[1]
            reply = find_tyr(playerData, int(slot))
            await channel.send(reply)
            return

        if message == "$challenge-idun":
            reply = challenge_idun(playerData)
            await channel.send(reply)
            return

        if message == "$challenge-idun-complete":
            reply = challenge_idun_complete(playerData)
            await channel.send(reply)
            return

        if message == "$claim-gold":
            reply = claim_gold(playerData)
            await channel.send(reply)
            return

        if message.startswith("$beat-nidhogg-"):
            weapon = message.split('$beat-nidhogg-')[1]
            reply = beat_nidhogg(playerData, weapon)
            await channel.send(reply)
            return

        if message == "$visit-well":
            reply = visit_well(playerData)
            await channel.send(reply)
            return

        if message.startswith("$fateweavers-"):
            answer = message.split("$fateweavers-")[1]
            reply = check_fateweavers(playerData, answer)
            await channel.send(reply)
            return

        if message == "$bifrost-to-midgard":
            reply = await norse_travel(data, playerData, "MIDGARD")
            await channel.send(reply)
            return

        if message == "$cross-to-utgard":
            reply = utgard_travel(playerData)
            await channel.send(reply)
            return

        if message.startswith("$fly-asgard-"):
            destination = message.split("$fly-asgard-", 1)[1]
            reply = await norse_travel(data, playerData, destination.upper())
            await channel.send(reply)
            return

        if message == "$ascend-checkin":
            reply = pitstop_checkin(playerData)
            await channel.send(reply)

    elif playerData["location"] == 'MIDGARD':

        if message == "$bifrost-to-asgard":
            reply = await norse_travel(data, playerData, "ASGARD")
            await channel.send(reply)
            return

        if message == "$visit-pub":
            reply = visit_pub()
            await channel.send(reply[0])
            await channel.send(reply[1])
            return

        if message.startswith("$marry-"):
            husband = message.split("$marry-", 1)[1]
            reply = marry(playerData, husband)
            await channel.send(reply)
            return

        if message.startswith("$heads-"):
            bet = message.split("$heads-", 1)[1]
            reply = heimdall_bet(playerData, "HEADS", int(bet))
            await channel.send(reply)
            return

        if message.startswith("$tails-"):
            bet = message.split("$tails-", 1)[1]
            reply = heimdall_bet(playerData, "TAILS", int(bet))
            await channel.send(reply)
            return

        if message == "$slay-jormungandr":
            reply = slay_jormungandr(playerData)
            await channel.send(reply)
            return

        if message == "$pray":
            reply = church_pray(playerData)
            await channel.send(reply)
            return

        if message == "$oiram-guide":
            reply = oiram_guide(playerData)
            await channel.send(reply)
            return

        if message.startswith("$imbue-"):
            item = message.split("$imbue-", 1)[1]
            reply = imbue(playerData, item.upper())
            await channel.send(reply)
            return

        if message == "$visit-market":
            reply = await visit_market(data, playerData)
            await channel.send(reply)
            return

        if message == "$ferry-to-jotunheim":
            reply = await norse_travel(data, playerData, "JOTUNHEIM")
            await channel.send(reply)
            return

        if message == "$rail-to-muspelheim":
            reply = await norse_travel(data, playerData, "MUSPELHEIM")
            await channel.send(reply)
            return

        if message == "$cart-to-nidavellir":
            reply = await norse_travel(data, playerData, "NIDAVELLIR")
            await channel.send(reply)
            return

        if message == "$assemble-skidbladnir":
            reply = assemble_skidbladnir(playerData)
            await channel.send(reply)
            return

        if message.startswith("$buy-"):
            if data.channel.id == 1076053510103244850:
              item = message.split("$buy-", 1)[1]
              reply = buy_item(playerData, item)
            else:
              reply = ":warning: You may only buy items at the Midgard Market thread!"
            await channel.send(reply)
            return

    elif playerData["location"] == 'ALFHEIM':

        if message.startswith("$fly-alfheim-"):
            destination = message.split("$fly-alfheim-", 1)[1]
            reply = await norse_travel(data, playerData, destination.upper())
            await channel.send(reply)
            return

        if message == "$talk-elfqueen":
            reply = elf_queen_talk(playerData)
            await channel.send(reply[0])
            await channel.send(reply[1])
            return

        if message == "$elfqueen-win":
            reply = elf_queen_win(playerData)
            await channel.send(reply)
            return

        if message == "$join-ahacup":
            await channel.send(aha_cup_join(playerData))
            return

        if message == "$ahacup-success":
            await channel.send(aha_cup_success(playerData))
            return

        if message == "$visit-stables":
            reply = visit_stables(playerData)
            await channel.send(reply[0])
            await channel.send(reply[1])
            return

        if message.startswith("$feed-"):
            food = message.split("$feed-", 1)[1]
            reply = feed_horse(playerData, food)
            await channel.send(reply)
            return

        if message == '$train-sleipnir':
            reply = train_horse(playerData)
            await channel.send(reply)
            return

    elif playerData["location"] == 'VANAHEIM':

        if message.startswith("$fly-vanaheim-"):
            destination = message.split("$fly-vanaheim-", 1)[1]
            reply = await norse_travel(data, playerData, destination.upper())
            await channel.send(reply)
            return

        if message == "$visit-garden":
          reply = await visit_garden(data, playerData)
          await channel.send(reply)
          return

        if message == "$enter-hall":
          reply = await enter_hall(data, playerData)
          await channel.send(reply)
          return

        if message.startswith('$enroll-'):
          package = message.split("$enroll-", 1)[1]
          await channel.send(enroll_horse(playerData, package))
          return

        if message.startswith('$buy-'):
          food = message.split('$buy-', 1)[1]
          await channel.send(buy_food(playerData, food))
          return

        if message == "$harvest-flowers":
          await channel.send(harvest_flowers(playerData))
          return

        if message == "$start-polishing":
          await channel.send(start_polishing(playerData))
          return 

        if message.startswith("$wordle-select-mirror "):
          input = int(message.split("$wordle-select-mirror ", 1)[1])
          await channel.send(select_mirror(playerData, input))
          return

        if message.startswith("$wordle-solve "):
          guess = message.split("$wordle-solve ", 1)[1]
          await channel.send(wordle_solve(playerData, guess))
          return

        if message == "$bejeweled-victory":
          await channel.send(wordle_win(playerData))
          return

    elif playerData["location"] == 'JOTUNHEIM':
        if message == "$ferry-to-midgard":
            reply = await norse_travel(data, playerData, "MIDGARD")
            await channel.send(reply)
            return

        if message == "$visit-woodlands":
            reply = await visit_woodlands(data, playerData)
            await channel.send(reply)
            return

        if message.startswith("$wood-"):
            answer = message.split("$wood-", 1)[1]
            answer = answer.split("-")
            reply = gather_wood(playerData, answer[0] + answer[1])
            await channel.send(reply)
            return

        if message == "$hack-trees":
            reply = hack_trees(playerData)
            await channel.send(reply)
            return

    elif playerData["location"] == 'MUSPELHEIM':
        if message == "$rail-to-midgard":
            reply = await norse_travel(data, playerData, "MIDGARD")
            await channel.send(reply)
            return

        if message == "$visit-tarvedron":
            await channel.send(visit_tarvedron())
            return

        if message.startswith('$horserace-'):
            answer = message.split('$horserace-', 1)[1]
            reply = horse_race(playerData, answer)
            await channel.send(reply)
            return

        if message == "$skate-to-niflheim":
            reply = await norse_travel(data, playerData, "NIFLHEIM")
            await channel.send(reply)
            return

        if message.startswith("$colorgame-"):
            color = message.split('-', 3)[1]
            bet = int(message.split('-', 3)[2])
            await channel.send(color_game(playerData, color, bet))
            return

    elif playerData["location"] == 'NIFLHEIM':
        if message == "$skate-to-muspelheim":
            reply = await norse_travel(data, playerData, "MUSPELHEIM")
            await channel.send(reply)

        if message.startswith("$place-"):
            item = message.split("$place-", 1)[1]
            await channel.send(place_statue(playerData, item))

        if message == "$sleipnir-to-hel":
            reply = await ride_to_hel(data, playerData, 0)
            await channel.send(reply)
            return

        if message.startswith("$gallop-chasm"):
            step = message.split("$gallop-chasm", 1)[1]
            reply = await ride_to_hel(data, playerData, int(step))
            await channel.send(reply)
            return

    elif playerData["location"] == 'NIDAVELLIR':
        if message == "$cart-to-midgard":
            reply = await norse_travel(data, playerData, "MIDGARD")
            await channel.send(reply)
            return

        if message == "$assemble-gungnir":
            reply = assemble_gungnir(playerData)
            await channel.send(reply)
            return

        if message == "$assemble-hammer":
            reply = assemble_hammer(playerData)
            await channel.send(reply)
            return

        if message.startswith("$minelevel-"):
            level = message.split("$minelevel-", 1)[1]
            await channel.send(mine_level(playerData, int(level)))
            return

        if message == "$visit-caverns":
            reply = await visit_caverns(data, playerData)
            await channel.send(reply)
            return

        if message == "$ride-coaster":
            await channel.send(cavern_coaster(playerData, 0))
            return

        if message.startswith("$face-loop"):
            step = message.split("$face-loop", 1)[1]
            await channel.send(cavern_coaster(playerData, int(step)))
            
    elif playerData["location"] == 'HEL':

        if message == "$battle-hel":
            await channel.send(battle_hel(playerData))
            return

        if message == "$shoot-balder":
            await channel.send(shoot_balder(playerData))
            return

        if message == "$sleipnir-to-niflheim":
            set_player_data(playerData["name"], "location", "NIFLHEIM")
            await channel.send(":horse_racing: Welcome to **NIFLHEIM!**")
            return
          
# Clean up DB calls
def get_player_data(name):
    return {
        "location": db["norse-" + name + "-location"],
        "items": db["norse-" + name + "-items"],
        "money": db["norse-" + name + "-money"],
        "crystals": db["norse-" + name + "-crystals"],
        "name": name,
        "frozen": db["norse-" + name + "-frozen"],
        "frozenreason": db["norse-" + name + "-frozenreason"],
        "nidhogg-hp": db["norse-" + name + "-nidhogg-hp"],
        "hel-hp": db["norse-" + name + "-hel-hp"],
        "found-tyr": db["norse-" + name + "-found-tyr"],
        "husband": db["norse-" + name + "-husband"],
        "trigger-ragnarok": db["norse-" + name + "-trigger-ragnarok"],
        "faith": db["norse-" + name + "-faith"],
        "spear-imbue": db["norse-" + name + "-spear-imbue"],
        "unlocked-locations": db["norse-" + name + "-unlocked-locations"],
        "horse-growth": db["norse-" + name + "-horse-growth"],
        "horse-exp": db["norse-" + name + "-horse-exp"],
        "hay": db["norse-" + name + "-hay"],
        "gysahl": db["norse-" + name + "-gysahl"],
        "cavern-loop": db["norse-" + name + "-cavern-loop"],
        "sleipnir-gallop": db["norse-" + name + "-sleipnir-gallop"]
    }


# Update Player Data
def set_player_data(name, trait, value):
    db["norse-" + name + "-" + trait] = value


# Add Money
def add_money(name, value):
    money = db["norse-" + name + "-money"] + value
    if money <= 0:
        money = 0
    db["norse-" + name + "-money"] = money
    return money


# Get Money
def get_money(name):
    return db["norse-" + name + "-money"]


# Adjust Nidhogg HP
def set_nidhogg(name, value):
    currentHp = db["norse-" + name + "-nidhogg-hp"] + value
    db["norse-" + name + "-nidhogg-hp"] = currentHp
    return currentHp


# Add Item
def add_item(name, item):
    currentItems = db["norse-" + name + "-items"]
    currentItems.append(item)
    db["norse-" + name + "-items"] = currentItems

# Get list of Items
def get_items(name):
    return db["norse-" + name + "-items"]


# Check if Player has item
def check_item(name, item):
    return item in db["norse-" + name + "-items"]


# Remove if Player has item
def remove_item(name, item):
    items = db["norse-" + name + "-items"]
    items.remove(item)
    db["norse-" + name + "-items"] = items


# Freeze Player
def freeze_player(name, value, reason):
    db["norse-" + name + "-frozen"] = value
    db["norse-" + name + "-frozenreason"] = reason


# Add Crystal
def add_crystal(name, crystalName):
    crystalList = db["norse-" + name + "-crystals"]
    if crystalName in validCrystals and crystalName not in crystalList:
        crystalList.append(crystalName)
        db["norse-" + name + "-crystals"] = crystalList


# Check Crystal
def check_crystal(crystalList, crystalName):
    return crystalName in crystalList


#**************************
# ASGARD ONLY
#**************************
def visit_halltreasure():

    hallTreasureText = """:coin: **HALL OF TREASURES** :coin:

You have been taught through history that the four treasures have been lost to conflicts, wars, and time, through the endless battles between the Æsir and the Vanir. This is a privilege to be part of the prophecy. You will need these someday:

THE 4 LEGENDARY ITEMS

**HARP**, its silky, velvety texture can only be procured from the hairs of a single royal bloodline. Some say that once placed in the right location, it will unlock a Crystal sealed away in a cold embrace.

**MJOLLNIR**, an extraordinary hammer capturing the essence of thunder, that can slay mythical reptiles of old folks and haunts. Some say that this weapon will lead to a new age as it will break the cycle of time.

**SKIDBLADNIR**, weaved from precise, magical hands, this light-as-a-feather sail can cross even the greatest rivers, and take you to the skies - to new realms that seemed unreachable before. 

**SPEAR OF GUNGNIR**, when imbued with the right plant essence, this spear will break an age-old curse, and unlock a Crystal that have been lost since its inception. However, the challenge is to find the raw material that would make this possible.

You may proceed and talk, visit, or do something within the vicinity of Asgard."""
    return hallTreasureText


def visit_valhalla():

    valhallaText1 = """:european_castle:  **VALHALLA** :european_castle: 

You now go through the gates and discover a council meeting between the Gods and Goddesses, your curiosity is piqued with the Crystal Room.

ODIN: My dear, the Crystal Room is open. It's coming... the end of times.
THOR: It's in the prophecy... DOOM.
ODIN: But this is our duty, we have to find these crystals before they are used to harm people.
FREYR: What's the lad doing here? *points to you*
ODIN: The Gods from the Wakarir x Crossover universe have brought you. YES!! You will be the one tasked to gather these crystals.
*You are shocked*
ODIN: My dear, you have the power to trigger the end of the world. Just complete the *9 Crystals* from the 9 Realms/Worlds connected by Yggdrasil, the life-giving tree.
FRIGG: They have sent... this person?!?!?! *cries* HOW WILL MY SON GET SAVED?!?!
ODIN: Trust in the higher power. They will complete this. Won't you?
*You are visibly shaken, but you have to nod*
ODIN: Once you have completed the NINE CRYSTALS - one from each realm, you can trigger the RAGNAROK - the end times. Make sure that you can DO THIS. We trust you."""

    valhallaText2 = """:gem:  **CRYSTAL ROOM -- RAGNAROK** :gem: 
*Once you have all 9 Crystals, you may trigger Ragnarok - the end times.*

To trigger Ragnarok, simply type `$trigger-ragnarok`

:speech_balloon:  **TALK TO THE AESIR** :speech_balloon: 

ODIN: Talk to me using `$odin-lesson` to know random facts about this world.
FRIGG: My beloved son, the most handsome, Balder, is in HEL. Please help him!
THOR: I don't have the time to talk to you. If you want a taste of my power, type `$thor-shock`
SIF: My husband, Thor, is so handsome. He likes to pulsate thunder through metals! What a long, long... thing. 
LOKI: Cut that bitch's hair, Sif. It's her only TREASURE. That royal wench is too much around here. To cut Sif's hair, type `$sif-cut`
FREYR: Let me tell you, I've been stuck here. The Aesir-Vanir wars took out all the Skidbladnir... and I couldn't go back to the sky realms, **ALFHEIM and VANAHEIM**"""

    return [valhallaText1, valhallaText2]


def trigger_ragnarok(playerData):

    reply = ""
    crystalCount = len(playerData['crystals'])
    if crystalCount == 9:
        reply = '**' + playerData[
            'name'] + '**, you have successfully triggered **Ragnarok**. The end is near, and you must complete the remaining quests in order to survive and live on through the end of times. Good luck! You are very close to the Pitstop.'
        set_player_data(playerData['name'], "trigger-ragnarok", True)
    else:
        reply = '**' + playerData['name'] + '**, you only have found **' + str(
            crystalCount) + '** out of **9** Crystals.'

    return reply


def odin_lesson():

    randomValue = random.randrange(1, 13)
    return "**LESSON: **" + odinLessonsJson[str(randomValue)]


def thor_shock(playerData):
    name = playerData["name"]
    if check_item(name, "MJOLLNIR"):
        return """:zap: Nothing happens."""
    elif check_item(name, "HAMMER"):
        remove_item(name, "HAMMER")
        add_item(name, "MJOLLNIR")
        return """:zap: The ***Hammer***, with Thor's thunder, has turned to the famed, legendary ***Mjollnir***! :hammer:"""
    else:
        return """:zap: You have been shocked with volts of lightning. However, you feel a tingling sensation, that one day, this thunder would make something legendary."""


def sif_cut(playerData):
    name = playerData["name"]
    if check_item(name, "HARP"):
        return """:scissors: There is no more need to cut that goddess' hair. You already have the **HARP**."""
    elif check_item(name, "CUTLASS") or check_item(name, "SCISSORS"):
        add_item(name, "HARP")
        return """:scissors: You now have a lock of Sif's hair. The silky smooth locks of her hair arranges itself into the legendary **HARP** that can break a magical seal in the right location."""
    else:
        return """:scissors: **Sif:** WAG MO AKONG HAWAAN NG KUTO YUCK CAN YOU PLEASE STOP BEING OBSESSED ABOUT MY BEAUTY? AND ... MY HAIR?!?!"""


def find_tyr(playerData, slot):

    name = playerData["name"]
    if slot == 13:
        return ":mag: You realize **Tyr** is on an **EVEN**-number location."
    elif slot == 20:
        if check_item(name, "CUTLASS"):
            return ":mag: You found nothing."
        add_item(name, "CUTLASS")
        return ":mag: You have found a :dagger: **CUTLASS**."
    elif slot == 64:
        #Should only be done once.
        if playerData["found-tyr"]:
            return ":mag: You found nothing."
        add_money(name, 2000)
        set_player_data(name, "found-tyr", True)
        return ":mag: You have found **Tyr** and the **2,000 Kroner** reward."
    elif slot == 79:
        if check_item(name, "SCISSORS"):
            return ":mag: You found nothing."
        add_item(playerData["name"], "SCISSORS")
        return ":mag: You have found :scissors: **SCISSORS**."
    elif slot == 86:
        return ":mag: You realize **Tyr** is not on a **NUMBER** divisible by 3."
    else:
        return ":mag: You found nothing."


def challenge_idun(playerData):

    #If player has beat idun before, block
    if check_crystal(playerData["crystals"], "ASGARD"):
        return "You have already defeated Idun."

    #Disable player from performing anything.
    freeze_player(playerData["name"], True, "IDUN_CHALLENGE")

    text = """
:gem:  **CRYSTAL OF ASGARD** :gem:
IDUN: I actually have chanced upon the **CRYSTAL of ASGARD**. Tyr doesn't know I have it - and I think I'm supposed to give it to you. But it wouldn't be fun if I can't play with you, right? So you have to play this **NORINORI** game I have prepared.

*It is known in the realm of Norse Mythology that the Aesir loves playing games*

Now, in this challenge, you must head to this website: https://www.puzzle-norinori.com/
After that, you must solve an **8x8 Normal Puzzle**
Once done, you must take a screenshot similar to the photo below. 
Make sure that the puzzle you are solving has not been solved by another player (NOTE: This will only happen if you copied each other). Make sure your puzzle number is unique, and only you know it.
Send in your **MESSENGER RACER GC**

Once done, you will obtain the **CRYSTAL OF ASGARD**. 
NOTE: You cannot do other actions such as going to other places during the time you are doing this. You can only leave this place once you are done with the challenge.

https://i.ibb.co/frk18d2/NORINORI.png"""

    return text


def challenge_idun_complete(playerData):

    # Check if idun has already been defeated before
    if check_crystal(playerData["crystals"], "ASGARD"):
        return "You already defeated Idun and obtained the :gem: **CRYSTAL OF ASGARD**."

    #Enable player
    freeze_player(playerData["name"], False, "")
    add_crystal(playerData["name"], 'ASGARD')

    text = """**IDUN:** Very well, adventurer. I just know you have it in you. Keep exploring and finding the Crystals from the rest of the worlds.

Congratulations! You have earned :gem: **CRYSTAL OF ASGARD** :gem: and added it to your inventory.
  """

    return text


# Review if player should be unfrozen
def review_freeze(playerData, message):
    return ((playerData["frozenreason"] == "IDUN_CHALLENGE" and message == "$challenge-idun-complete") or
            (playerData["frozenreason"] == "QUEENS_GAMBIT" and message == "$elfqueen-win") or 
            (playerData["frozenreason"] == "AHA_CUP" and message == "$ahacup-success") or
            (playerData["frozenreason"] == "CAVERN_COASTER" and message.startswith("$face-loop")) or
            (playerData["frozenreason"] == "SLEIPNIR_TO_HEL" and message.startswith("$gallop-chasm")) or
            (playerData["frozenreason"] == "BEJEWELED_GAME" and message.startswith("$wordle-")))


# Claim gold
def claim_gold(playerData):

    time_now = datetime.now()
    current_hour = int(time_now.strftime("%H"))
    current_minute = int(time_now.strftime("%M"))
    previous_hour = int(db["norse-gold-fountain-hour"])
    previous_minute = int(db["norse-gold-fountain-minute"])

    # claim if:
    # - If previously recorded time is ODD, at least 1 minute should have passed
    # - If previously recorded time is EVEN, at least 2 minutes should have passed

    if current_hour > previous_hour or (current_hour == previous_hour and (
        (previous_minute % 2 == 0 and previous_minute + 2 <= current_minute) or
        (previous_minute % 2 == 1 and previous_minute + 1 <= current_minute))):
        value = random.randrange(100, 601)
        add_money(playerData["name"], value)
        db["norse-gold-fountain-hour"] = current_hour
        db["norse-gold-fountain-minute"] = current_minute
        db["norse-gold-fountain-claimed"] = True
        return ":coin: You got **" + str(
            value) + "** Kroner!\nTotal amount: **" + str(
                get_money(playerData["name"])) + ' Kroner**'

    return ":coin: The Gold Fountain is currently empty. Wait until the gold replenishes. Try again later."


#Nidhogg
def beat_nidhogg(playerData, weapon):

    if playerData["nidhogg-hp"] < 1:
        return "**" + playerData[
            "name"] + "**, you have already defeated the Nidhogg. You can now visit the well by typing `$visit-well`"

    # TODO: FIX THIS. WEAPONS SHOULD BE PROPERLY ID'd
    validWeapons = ["cutlass", "staff", "hatchet", "dagger", "blade", "scythe", "axe"]
    moneyReceive = False

    if weapon not in validWeapons:
        return "**" + playerData["name"] + "**, invalid weapon input! Try again."

    if convert_keyword(weapon) not in playerData["items"]:
        return "**" + playerData["name"] + "**, you do not have that weapon in your inventory! Try again."

    randomType = weaponsJson[weapon]["type"]
    randomValues = weaponsJson[weapon]["value"]
    description = weaponsJson[weapon]["description"]

    if randomType == "set":
        pick = random.choice(randomValues)
        if pick == "50K":
            pick = 0
            add_money(playerData["name"], 50)
            moneyReceive = True
    elif randomType == "range":
        pick = random.randrange(randomValues[0], randomValues[1] + 1)

    remainingHP = set_nidhogg(playerData["name"], pick)

    reply = "You have attacked the Nidhogg with **" + description + "**. It gave **" + str(
        pick) + " HP** to the Nidhogg.\n**" + str(remainingHP) + "** HP left."

    if moneyReceive:
        reply = reply + "\n\n :coin: You also got *50 Kroner* from this fight!"

    if remainingHP < 1:
        set_nidhogg(playerData["name"], 0)
        reply = reply + "\n\nYou have defeated the Nidhogg. You can now visit the well by typing `$visit-well`"

    return reply


def visit_well(playerData):

    if playerData["nidhogg-hp"] >= 1:
        return "The Nidhogg hinders you from entering the root passage."

    wellText = """:hamsa: **WELL OF MIMIR** :hamsa: 

Mine-a: We are the fate weavers. Our part in the prophecy is to give the :gem:  **CRYSTAL OF JOTUNHEIM** :gem:  to the one who knows our creator well. These are our questions:

1.) Where would creator Arvin want to go back to?
a. Taiwan | b. Cotabato | c. Cavite | d. Boracay

2.) If you were to give creator Bry Z a blind date, which zodiac sign would it be knowing his preference?
a. Scorpio | b. Aries | c. Leo | d. Taurus

3.) What is creator Ellis' secret in his lumpia recipe?
a. Ellis adds raisins | b. Ellis makes lumpia wrapper from scratch | c. Ellis sings to soften them | d. Ellis uses Ajinomoto

4.) Which platform would you NOT see @foodaideals, according to creator Friday?
a. Instagram | b. Tiktok | c. Twitter | d. Facebook

5.) Roughly how many times does creator Carl leave the country in a year?
a. 2 to 4 times | b. 5 to 8 times | c. 9 to 12 times | d. More than 12 times

To answer, type command  `$fateweavers-12345` and replace 12345 with small letters of correct answer. (e.g. aaacc)

If you are unsure of your answers, try finding them first, and you can come back here and do this any time that you are in **ASGARD**.

❗ *NOTE: These questions are answerable, without knowing the hosts personally. There are certain entities who can point to those with knowledge of the creators - Arvin, Friday, Carl, Bry and Ellis*"""

    return wellText


def check_fateweavers(playerData, answer):

    if playerData["nidhogg-hp"] >= 1:
        return "I am not sure how you've found us, but the Nidhogg is still a threat. I suggest you beat that beast first."

    if check_crystal(playerData["crystals"], "JOTUNHEIM"):
        return "You already have earned the :gem: **CRYSTAL OF JOTUNHEIM** :gem:"

    text = "Your answer is incorrect."
    if answer == 'daccd':
        add_crystal(playerData["name"], 'JOTUNHEIM')
        text = "Congratulations! You have earned :gem: **CRYSTAL OF JOTUNHEIM** :gem: and added it to your inventory."

    return text


def utgard_travel(playerData):

    if "SKIDBLADNIR" not in playerData["items"]:
        return "The waters are too dangerous for a mere boat. You cannot cross right now."

    if "SERPENT_BLOOD" not in playerData["items"]:
        return "A group of giants intercept you halfway upon crossing the river. They demand SERPENT'S BLOOD to allow you entry."

    return """:european_castle:  **UTGARD CASTLE** :european_castle:
*This is the tallest building in the mainland. The giants have constructed an impenetrable stronghold that can withstand even the greatest calamitous floods.*

GIANT DAGUL: You are the prophesied survivor of Ragnarok, please go up the castle roof and save yourself from the impending flood.

To ascend to the pitstop and check-in, type `$ascend-checkin`

WARNING: The last team to CHECK-IN may be ELIMINATED!"""


async def norse_travel(data, playerData, destination):

    name = playerData["name"]
    money = playerData["money"]
    items = playerData["items"]
    source = playerData["location"]

    # Bifrost: ASGARD to MIDGARD (50 Kroner)
    # Fly via Skidbladnir: ASGARD to ALFHEIM to VANAHEIM (Free, as long as have Skidbladnir)
    # Ferry: MIDGARD to JOTUNHEIM (100 Kroner)
    # Rail: MIDGARD to MUSPELHEIM (300 Kroner)
    # Cart: MIDGARD to NIDAVELLIR (but requires LUMINOUS_PENDANT)

    # Bifrost
    if (source, destination) == ('ASGARD', 'MIDGARD') or (
            source, destination) == ('MIDGARD', 'ASGARD'):
        if money < 50:
            return ":rainbow: You don't have sufficient funds. Try claiming in the fountain."

        currentMoney = add_money(name, -50)
        set_player_data(name, "location", destination)
        await exploreLand(data, playerData, destination)
        return ":rainbow: Welcome to **" + destination.title() + "**!\n:coin: Current money left: **" + str(currentMoney) + "** Kroner"
    elif destination in ['ASGARD', 'ALFHEIM', 'VANAHEIM'] and source in ['ASGARD', 'ALFHEIM', 'VANAHEIM']:
        # Sky territories
        if 'SKIDBLADNIR' not in items:
            return "You believe you can fly? ONLY WHEN PIGS FLY!"

        set_player_data(name, "location", destination)
        await exploreLand(data, playerData, destination)
        return ":cloud: Welcome to **" + destination.title() + "**!"
    elif (source, destination) == ('MIDGARD', 'JOTUNHEIM') or (source, destination) == ('JOTUNHEIM', 'MIDGARD'):
        if money < 100:
            return ":cruise_ship: You don't have sufficient funds."

        currentMoney = add_money(name, -100)
        set_player_data(name, "location", destination)
        await exploreLand(data, playerData, destination)
        return ":cruise_ship: Welcome to **" + destination.title() + "**!\n:coin: Current money left: **" + str(currentMoney) + "** Kroner"
    elif (source, destination) == ('MIDGARD', 'MUSPELHEIM') or (
            source, destination) == ('MUSPELHEIM', 'MIDGARD'):
        if money < 300 and source == 'MIDGARD':
            return ":station: Insufficient funds."

        currentMoney = add_money(name, -300) if source == 'MIDGARD' else playerData["money"]
        set_player_data(name, "location", destination)
        await exploreLand(data, playerData, destination)
        return ":station: Welcome to **" + destination.title(
        ) + "**!\n:coin: Current money left: **" + str(
            currentMoney) + "** Kroner"
    elif (source, destination) == ('MIDGARD', 'NIDAVELLIR') or (source, destination) == ('NIDAVELLIR', 'MIDGARD'):
        if 'LUMINOUS_PENDANT' not in playerData["items"]:
            return "Yikes! You cannot see anything at all! You need something that will give off light throughout. You cannot proceed to Nidavellir without it."

        set_player_data(name, "location", destination)
        await exploreLand(data, playerData, destination)
        return ":train: Welcome to **" + destination.title() + "**"
    elif (source, destination) == ('MUSPELHEIM', 'NIFLHEIM') or (source, destination) == ('NIFLHEIM', 'MUSPELHEIM'):
        if len(playerData['crystals']) < 5:
          return "The world is too cold and out-of-balance. You need to have at least 5 Crystals to cross."

        set_player_data(name, "location", destination)
        await exploreLand(data, playerData, destination)
        return ":roller_skate: Welcome to **" + destination.title() + "**!"
    else:
        return "Invalid transport command!"


#**************************
# MIDGARD ONLY
#**************************
def visit_pub():
    pubText1 = """:beers:  **INSIDE THE PUB** :beers: 

*gossip fills the air*
Maritess: XERPALMA is the hottest! He plays that thing called 'volleyball'. He is a big big bear that can warm me like a hearth in my home. He will get me through winter 'cause he makes me FEEL. THE. HEAT.
Myerkles: He is not in favor with the gods... but he's... really good... as good as EDONBURS. Damn, don't you love sailors? He even says he'd encountered elves through his journey!
Huweves: But you have no time to JUG-JUG, right Miss Myerkles?! Speaking of having a lot of time and a lot of friends... and friend requests, how about RANIKIM? Can definitely give you something with that career.
Savvado: BORING! Why marry someone like that? No one beats Jontanjesta when he won gameshow of the year... won something in the festival. He is an entertainer.
Gaylinggo: MGA BEKS!! PA MISS MISS KAU JAN MGA ACCLA LASUNAN?!?! PWEDE NAMAN SINGLE FOREVER.
Lunezz: MGA BAKS!! PILI PILI NA. LASING LANG 'YANG MGA YAN.
Viernezze: CHE! MAG-SHOPPING NA LANG US MGA GANDA. Meron daw crystal na tinda sa Market. EXCLUZZIVE?!?!

*you see a group of four men, each wanting to marry you.*
Xerpalma: TARA BABE PAKASAL NA US. SAKAY KITA HATID SUNDO.
Edonburs: DI AKO SEAMAN-LOLOKO. LOYALTY KO SA'YO BABE.
Ranikim: PLEASE ACCEPT MY MARRIAGE REQUEST :slight_smile:
Jontanjesta: TARA NA'T MAG JOGGING JOGGING! JOGJOGAN NA. """

    pubText2 = """Well, well, you can only marry once? Marry right! If you want to get married, choose between the four by typing any of these commands:
To marry Edonburs, `$marry-edonburs`
To marry Jontanjesta, `$marry-jontanjesta`
To marry Ranikim, `$marry-ranikim`
To marry Xerpalma, `$marry-xerpalma`

CHOOSE WISELY! 

:game_die: **HEIMDALL, Aesir of Humanity** :game_die:

HEIMDALL: Welcome to my abode! Humans love me. I'm here to give them entertainment. Gambling is one. If you want to take a chance, I will flip a coin. Just choose between HEADS or TAILS, by typing any of these commands (replace X with bet from 1 to 200 Krone):

`$heads-X` or `$tails-X`"""

    return [pubText1, pubText2]
def marry(playerData, husband):
    name = playerData["name"]
    if playerData["husband"] != "":
        return "You are already married to **" + playerData["husband"].title(
        ) + "**"

    set_player_data(name, "husband", husband)

    if husband == "edonburs":
        add_item(name, "LUMINOUS_PENDANT")
        reply = "You have married **EDONBURS**. You are now in possession of his most valued treasure, **LUMINOUS PENDANT**. This can give you access through Nidavellir. You can now go down that realm as this luminous pendant will give off an eternal light."
    elif husband == "jontanjesta":
        add_crystal(name, "MIDGARD")
        reply = "You have married **JONTANJESTA**. You are now in possession of his most valued treasure, :gem: **CRYSTAL OF MIDGARD** :gem:. Yes, he is in possession of this. You may choose not to buy from the Midgard Market as you have just added one crystal to your inventory."
    elif husband == "ranikim":
        add_item(name, "HARP")
        reply = "You have married **RANIKIM**. You are now in possession of Rani's most valued treasure, **HARP**. This is a magical musical instrument! This means, you no longer have to cut Sif's hair. You no longer need Scissors or Cutlass. You now have the item."
    elif husband == "xerpalma":
        money = add_money(name, -300)
        reply = "You have married **XERPALMA**. Sometimes, when the heart chooses - it chooses the path of hardship. Xerpalma is **NOT** in the favorable list of the Aesir. You are charged :coin: **300 Kroner** because he didn't pay his tab.\n\nCurrent money left: :coin: **" + str(
            money) + " Kroner**"
    else:
        set_player_data(name, "husband", "")
        reply = "**" + name + "**, trust us, your true love is among these four suitors. Try again and choose carefully."

    return reply
def heimdall_bet(playerData, pick, bet):

    if bet not in range(1, 201):
        return ":warning: **Heimdall**: You may only bet up to a maximum of 200 Kroner!"

    if bet > playerData["money"]:
        return ":warning: **Heimdall**: Your balance is **less** than your bet. The game will not go through."

    randomPick = random.choice(["HEADS", "TAILS"])
    reply = ":game_die: **Heimdall** flipped a coin... **" + randomPick.title(
    ) + "**!"

    if randomPick == pick:
        currentMoney = add_money(playerData["name"], bet)
        reply = reply + "\n:moneybag: Congratulations! You win **" + str(
            bet) + "** Kroner!"
    else:
        currentMoney = add_money(playerData["name"], bet * -1)
        reply = reply + "\n:x: Oh no! You lost! You lose **" + str(
            bet) + "** Kroner!"

    reply = reply + "\n\nCurrent Money: :coin: **" + str(
        currentMoney) + "** Kroner!"
    return reply


def slay_jormungandr(playerData):

    if "SERPENT_BLOOD" in playerData["items"]:
        return "You already have the slained the **Jormungandr** and obtained the :drop_of_blood: **Serpent's Blood**."

    if "MJOLLNIR" not in playerData["items"]:
        return "There's no way of slaying this gigantic serpent unless you have that... legendary weapon."

    if not playerData["trigger-ragnarok"]:
        return "You can slay the Jormungandr with your Mjollnir! HOWEVER, you can't beat fate yet - you can only beat it during the end of times."

    add_item(playerData["name"], "SERPENT_BLOOD")
    return "You have slained the **Jormungandr**! The ultra-rare :drop_of_blood: **Serpent's Blood** has been added to your inventory."

def church_pray(playerData):

    choices = ["50K", 2, 3, 5, 8]
    pick = random.choice(choices)
    name = playerData["name"]

    if pick == "50K":
        money = add_money(name, 50)
        return ":pray: The creators have given you :coin: **50 Kroner**\nCurrent Money: :coin: **" + str(money) + "** Kroner!"

    faith = playerData["faith"] + pick
    set_player_data(name, "faith", faith)
    reply = ":pray: Your prayers have been answered. You have gained **" + str(pick) + "** Faith.\nCurrent Faith: " + str(faith) + " :pray:"
    if faith >= 100:
      reply = reply + "\n:angel: You have now exceeded the faith limit. :angel:"
    return reply


def oiram_guide(playerData):
    if playerData["money"] < 50:
        return ":book: You do not have enough Kroner with you!"

    guide = [
        "You need Faith to beat the goddess Hel, in the realm of... Hel. The more faith you have, the higher the chance of beating her.",
        "When you imbue the Spear of Gungnir with mistletoe, it can break Balder's curse in Hel.",
        "Market Guide: The Crystal of Midgard will sell at the market for as low as 750 Kroner, and as high as 2250 Kroner",
        "You can cut Sif's hair using either a SCISSOR or a CUTLASS. As soon as you get it, it will become the legendary HARP ",
        "Placing the harp on Ymir's statue will cause it to break the sound shield of the Crystal, and give you the Crystal of Niflheim.",
        "To answer the tricky questions on the Well of Mimir, all you have to do is keep asking Odin, and he will give you new information regarding creators and these worlds for free.",
        "When Ragnarok comes, some jokingly said that you can actually survive on the rooftop of Utgard Castle because it's just -that- tall when it floods.",
        "If you have FIRE AXE, you will yield more Krone in your lumberjack activities. CHARMED SCYTHE will yield you more Krone in your farming activities.",
        "The Hammer can turn into Mjollnir if you let Thor's thunder course through it. "
    ]

    currentMoney = add_money(playerData["name"], -50)
    return ":book: " + random.choice(
        guide) + "\nCurrent Money: :coin: **" + str(currentMoney) + "** Kroner"


def imbue(playerData, item):

    if item not in ["HYACINTH", "IVY", "MISTLETOE"]:
        return ":warning: Incorrect vat selection."

    if "SPEAR_OF_GUNGNIR" not in playerData["items"]:
        return "Nothing happens. You need the right kind of legendary weapon to imbue the powers of these herbs."

    set_player_data(playerData["name"], "spear-imbue", item)
    return ":test_tube: You have successfully imbued the Spear of Gungnir with **" + item.title(
    ) + "**!"


async def visit_market(data, playerData):

    await exploreLand(data, playerData, "MIDGARD-MARKET")
    return "You have been added to the **Midgard Market** thread. Go and check it out!"

async def visit_woodlands(data, playerData):

    await exploreLand(data, playerData, "WOODLANDS")
    return "You have been added to the **Jotunheim Woodlands** thread. Go and check it out!"

async def exploreLand(data, playerData, location):

    unlockedLocations = playerData["unlocked-locations"]
    if location not in unlockedLocations:
        unlockedLocations.append(location)
        set_player_data(playerData["name"], "unlocked-locations", unlockedLocations)
        await utils.utils.add_role(data.guild, data.author, landsJson[location]["roleId"])

def gather_wood(playerData, answer):

    solvedAnswers = db["norse-woodlands-answer"]
    name = playerData["name"]

    if answer in ['1m', '2e', '3d', '4i', '5n', '6a', '7b', '8o', '9g']:
      if answer not in solvedAnswers: 
        add_item(name, "ELMWOOD")
        solvedAnswers.append(answer)
        db["norse-woodlands-answer"] = solvedAnswers
        return ":wood: **" + name + "**, congratulations! You have added **Elmwood** to your inventory."
      else:
        return ":x: **" + name + "**, this wood is taken already! Try another one."
    else:
      return ":x: Incorrect!"

def hack_trees(playerData):

  multiplier = 1 if "FIRE_AXE" not in playerData["items"] else 1.5
  name = playerData["name"]
  pick = random.randrange(1, 101)
  money = 0
  
  if pick in range(1, 31):
    # UNSUCCESSFUL (30%)
    reply = ":x: **" + name + "**, you are not successful in cutting down the tree!"
  elif pick in range(31, 56):
    # PINE (25%)
    money = 50 * multiplier
    reply = ":evergreen_tree: **" + name + "**, you exchanged **Pine** for :coin: **" + str(money) + "** Kroner"
  elif pick in range(56, 76):
    # MAPLE (20%)
    money = 80 * multiplier
    reply = ":evergreen_tree: **" + name + "**, you exchanged **Maple** for :coin: **" + str(money) + "** Kroner"
  elif pick in range(76, 86):
    # OAK (10%)
    money = 160 * multiplier
    reply = ":evergreen_tree: **" + name + "**, you exchanged **Maple** for :coin: **" + str(money) + "** Kroner"
  elif pick in range(86, 101):
    # REDWOOD (15%)
    add_item(name, "REDWOOD")
    reply = ":evergreen_tree: **" + name + "**, you have added the :wood: **Redwood** to your inventory."
  else:
    reply = "It won't even reach this point. But let's catch it."

  money = int(money)
  currentMoney = add_money(playerData["name"], money)
  if money > 0:
    reply = reply + "\nCurrent money: **" + str(currentMoney) + "** Kroner"
  return reply

def visit_tarvedron():
  return """
:musical_note:  **TAR VEDRON** :musical_note: 

Lalisa:  BLACKPINK IN YOUR AREA! HORSE 7 FINISHES AFTER HORSE 1!
Rose: BLACKPINK IN YOUR AREA! HORSE 8 IS SLOWER THAN HORSE 3!
Jennie: BLACKPINK IN YOUR AREA! HORSE 6 FINISHES RIGHT AFTER HORSE 4!
Jisoo: BLACKPINK IN YOUR AREA! THE SUM OF THE HORSE NUMBERS APPEARING IN THE TOP 3 IS EQUAL TO 12.
Toni: BLACKFAKE IN YOUR AREA! WATCH TONI VLOGS ON ALLTV! MANIWALA KAYO SAKEN 31M!
Mikee Quintos: MAKE ME YOUR APHRODITE! HORSE 1 NASA TOP 3!!!
Venushurrah: MAJOR MAJOR! PERO HORSE 5 CAN'T BEAT HORSE 3. TAYA NA MGA FOLLOWERS
Wil: GANITO TAYO. SA MADALING USAPAN MGA KA-ALLTV, MAS MABILIS YUNG KABAYO NG DOS KESA SA SINGKO, PERO MAS MABAGAL ANG DOS SA PTV YUNG NUMERO KWATRO NA KABAYO.
Zephanie: GUYS, MAS MATAAS NUMERO NG TOP 1 AND TOP 2 KESA SA TOP 3. PANOTES"""

def horse_race(playerData, answer):

  if "MUSPELHEIM" in playerData["crystals"]:
    return ":horse: You already won the Horse Race and the :gem: **Crystal of Muspelheim**"
    
  if playerData["money"] < 75:
    return ":warning: You don't have enough money to do this. You need at least :coin: **75 Kroner**"

  currentMoney = add_money(playerData["name"], -75)
  if answer == '381':
    add_crystal(playerData["name"], "MUSPELHEIM")
    reply = ":horse: Congratulations! :gem: **CRYSTAL OF MUSPELHEIM** :gem: has been added to your inventory."
  else:
    reply = ":horse::x: Incorrect! You have lost :coin: **75** Kroner!"
    
  return reply + "\nCurrent money left: :coin: **" + str(currentMoney) + "** Kroner!"
def color_game(playerData, color, bet):

  if bet not in range(100, 501):
    return ":warning: Bet is not within range. Please try again."
  
  if bet > playerData["money"]:
    return ":warning: Insufficient funds."

  colorList = ['red', 'white', 'blue', 'green', 'yellow', 'purple']
  if color not in colorList:
    return ":warning: Invalid color selected. Please try again."

  add_money(playerData["name"], -1 * bet)
  picks = random.choices(colorList, k=3)
  count = picks.count(color)
  winnings = (count + 1) * bet if count != 0 else 0
  currentMoney = add_money(playerData["name"], winnings)

  reply = "You bet: :coin: " + str(bet) + " Kroner"
  reply = reply + "\nResults: :" + picks[0] + "_circle: :" + picks[1] + "_circle: :" + picks[2] + "_circle:"
  reply = reply + "\n\nYou bet on color **" + color + "**. There's **" + str(count) + "** :" + color + "_circle: that appeared."
  reply = reply + "\nYou won :coin: **" + str(winnings) + "** Kroner."
  reply = reply + "\nCurrent Money: :coin: **" + str(currentMoney) + "** Kroner."
  return reply
  
#******************************
# ALPHEIM
#******************************

def elf_queen_talk(playerData):
  #Disable player from performing anything.
  freeze_player(playerData["name"], True, "QUEENS_GAMBIT")
  
  elftext1 = """:woman_elf: **ELF QUEEN'S GAMBIT** :woman_elf: 

Elverbano: My daughters have gone out of the world, and out of the bounds of my influence. I guess they're growing up. I just want a reminder of them - perhaps, I can give you their **LUMINOUS PENDANT** because elves grow luminous themselves as they grow older. They don't need the protection of the pendant. You can use this to explore very dark, wet, and damp places where fire would go out, and humans can't see clear.

My only request is that you draw one of my daughters:

**TASK**: Take a picture of any of the following daughters of the Elf Queen: (1) Alex Gonzaga, (2) Toni Gonzaga, (3) Jam Magno, (4) Mocha Uson, (5) Imelda Marcos, (6) Sara Duterte, (7) Juliana Parizcova Segovia, (8) Karla Estrada, (9) Imee Marcos, (10) Liza Araneta-Marcos, (11) Cynthia Villar and (12) Loren Legarda."""
  
  elftext2 = """Choose one of them, and then draw that exact image BY HAND. You can use pencil, pen, or any art material to do so. Make sure that your drawing is RECOGNIZABLE and NOT HASTILY DONE. You must then do this - make a 1x3 or 3x1 collage showing these:
(1) A selfie of you with your completed drawing
(2) Reference Photo of the particular daughter
(3) Close-Up / Comparison Photo of the drawing of the daughter.

Once approved, you will receive the **LUMINOUS PENDANT**
 However, you have to account that this task is **FIRST COME, FIRST SERVED**.  If a daughter has been done, you cannot draw it anymore. However, there's no way of knowing who did what. You'll just know after drawing if it is TAKEN or NOT.

In addition, you cannot do other commands while doing this task. You are frozen here until you finish."""

  #If player has the Luminous Pendant already, show an additional message
  if "LUMINOUS_PENDANT" in playerData["items"]:
      freeze_player(playerData["name"], False, "")
      elftext2 = elftext2 + "\n\n\n:star2::star2::star2::star2::star2:\n:woman_elf: **Elverbano:** But oh! I've noticed that you already have the **Luminous Pendant.** No need to do this task then. Good luck in your journey!"

  return[elftext1, elftext2]

def elf_queen_win(playerData):
  # Check if idun has already been defeated before
    if "LUMINOUS_PENDANT" in playerData["items"]:
      return "You already have the **Luminous Pendant**."

    #Enable player
    freeze_player(playerData["name"], False, "")
    add_item(playerData["name"], "LUMINOUS_PENDANT")

    text = """Congratulations! Queen Elverbano approves your artistic portrayal of her daughter. You have now received a **LUMINOUS PENDANT**"""

    return text

def aha_cup_join (playerData):

  #If player has crystal, no need to do again.
  if "ALFHEIM" in playerData["crystals"]:
    return "You already have the :gem: **Crystal of Alfheim**"
    
  #Disable player from performing anything.
  freeze_player(playerData["name"], True, "AHA_CUP")
  
  text = """:guitar: **A-HA CUP** :guitar: 

Norway has produced quality music throughout its history as a country - but in this day and age, with over a billion streams in Spotify, **"Take On Me"** by a-ha is the most celebrated song from Norway. It is one of the most nostalgic pieces of sounds, and has been adapted in covers, played in radios, but could very well be part of an early morning jogging routine.

**TASK:** Wearing fitness or athleisure attire, trying to recreate the look/style of the dancer, and then perform his steps for the chorus of Take On Me (0:55 to 1:17). We need to see you wear appropriate clothes, as you perform the right steps. There will be strict judging because the routine is straightforward. Orientation (your use of left/right) doesn't matter. Pwede magkabali baliktad as long as you do the steps right. Also, you should look like kabisado mo ang steps by heart - and not looking at your screen. We need to see energy and performance worthy performance.
https://www.youtube.com/watch?v=b6yFRXvvsSg

Once approved, the hosts will give you the :gem: **CRYSTAL OF ALFHEIM** :gem:.
In addition, you cannot do other commands while doing this task. You are frozen here until you finish."""

  return text

def aha_cup_success(playerData):
  # Check if idun has already been defeated before
    if "ALFHEIM" in playerData["crystals"]:
      return "You already have the :gem: **Crystal of Alfheim**"

    #Enable player
    freeze_player(playerData["name"], False, "")
    add_crystal(playerData["name"], "ALFHEIM")

    text = """You have won the legendary A-HA cup! Now, Take on Me! Take this home! You've been given the **CRYSTAL OF ALFHEIM** for fielding your success in the Performing Arts."""

    return text

def visit_stables(playerData):

  if playerData["horse-growth"] == -1:
    set_player_data(playerData["name"], "horse-growth", 0)
    set_player_data(playerData["name"], "horse-exp", 0)
    
  stableText1 = """:horse: **SLEIPNIR** :horse: 

Sleipnir: *neighs sweetly*
Caretaker: What a loving colt - when it becomes a horse! It will be one of the best.
Sleipnir: *neighs cheekily*
Caretaker: You are a hung horse... you can do anything.
*You were shocked at the comment*

Caretaker: Your goal for Sleipnir, is to someday use it in your adventure. You can ride it through the most evil terrain imaginable. Of course, you'll still be using public transporation most of the time. But Sleipnir shall one day, be prophesied to take you to the right path, when that moment comes."""
  stableText2 = """**FOOD**
You can feed it with **hay** or **gysahl**. Gysahl is costlier, but would boost Sleipnir's growth. Hay is cheaper, but would take more time for the horse to build its mass. Gysahl is brimming with magic from Vanaheim, that's why it's like that.

**GROWTH AND ADULTHOOD**
Once Sleipnir has reached at least 100 Growth, Young Sleipnir would become **ADULT SLEIPNIR** and would be part of your journey.

**TRAINING**
Sleipnir can be trained at young or adult. However, if Sleipnir is young, the options are limited for where to train. For adult and faster training, there are training schools out there in other realms of the Yggdrasil. However, training builds strength. If it is strong enough, you can even reach the furthest realm - Hel.

To **FEED** Sleipnir, type any of these commands [that you have]: `$feed-hay` or `$feed-gysahl`
To **TRAIN** Sleipnir, type this command: `$train-sleipnir`"""

  return [stableText1, stableText2]

def feed_horse(playerData, food):

  if food not in ['hay', 'gysahl']:
    return ":warning: Invalid food input."

  if playerData["horse-growth"] == -1:
    return ":warning: You do not have a horse yet."

  if playerData["horse-growth"] >= 100:
    return ":horse: Sleipnir is already an **adult**. No need to feed."

  foodCount = playerData[food]
  if foodCount == 0:
    return ":warning: There's no **" + food + "** available. Please restock."

  horse = playerData["horse-growth"]
  if food == "hay":
    pick = random.randrange(3, 13)
  elif food == "gysahl":
    pick = random.randrange(15, 36)
  newHorseGrowth = horse + pick

  reply = ""
  if newHorseGrowth >= 100:
    reply = ":tada: :horse: Sleipnir has become an **adult!** :tada:\n"

  set_player_data(playerData["name"], food, foodCount - 1)
  set_player_data(playerData["name"], "horse-growth", newHorseGrowth)
  return reply + ":horse: The horse has gained **" + str(pick) + "** growth. The total growth is now **" + str(newHorseGrowth) + "**."

def train_horse(playerData):
  if playerData["horse-exp"] == -1:
    return ":warning: You do not have a horse yet."
    
  pick = random.choice([0, 1, 2, 3, 4])
  horseExp = playerData["horse-exp"]
  newHorseExp = horseExp + pick
  set_player_data(playerData["name"], "horse-exp", newHorseExp)

  if pick == 0:
    reply = ":racehorse: Sleipnir has **gained 0 EXP** as it is not in the mood."
  elif pick == 1:
    reply = ":racehorse: Sleipnir has **gained 1 EXP** as it learns a new routine."
  elif pick == 2:
    reply = ":racehorse: Sleipnir has **gained 2 EXP** as it loves you so much!"
  elif pick == 3:
    reply = ":racehorse: Sleipnir has **gained 3 EXP** because of its good mood and enthusiasm!"
  else:
    reply = ":racehorse: Sleipnir has **gained 4 EXP** because it is HORNY"

  if newHorseExp >= 100:
    reply = reply + "\n:horse: You have reached the experience limit of 100."
    
  return reply + "\nTotal Horse Exp: " + str(newHorseExp)

async def visit_garden(data, playerData):

  unlockedLocations = playerData["unlocked-locations"]
  if "LAVENDER-GARDEN" not in unlockedLocations:
          unlockedLocations.append("LAVENDER-GARDEN")
          set_player_data(playerData["name"], "unlocked-locations", unlockedLocations)
          await utils.utils.add_role(data.guild, data.author, landsJson["LAVENDER-GARDEN"]["roleId"])
  return "You have been added to the **Lavender Garden** thread. Go and check it out!"

async def enter_hall(data, playerData):

  unlockedLocations = playerData["unlocked-locations"]
  if "BEJEWELED-HALL" not in unlockedLocations:
          unlockedLocations.append("BEJEWELED-HALL")
          set_player_data(playerData["name"], "unlocked-locations", unlockedLocations)
          await utils.utils.add_role(data.guild, data.author, landsJson["BEJEWELED-HALL"]["roleId"])
  return "You have been added to the **Bejeweled Hall** thread. Go and check it out!"

def enroll_horse(playerData, package):
  growth = playerData["horse-growth"]
  if growth == -1:
    return ":horse: You don't have a horse to enroll."

  if growth < 100:
    return ":horse: You cannot enroll Sleipnir! He's still a young horse."

  if package == 'a':
    cost = 300
    minExp = 15
    maxExp = 40
  elif package == 'b':
    cost = 600
    minExp = 30
    maxExp = 60
  elif package == 'c':
    cost = 900
    minExp = 45
    maxExp = 80
  else:
    return ":warning: Incorrect package selected."

  if playerData["money"] < cost:
    return ":warning: Insufficient funds. Please collect enough funds."

  currentMoney = add_money(playerData["name"], -1 * cost)
  pick = random.randrange(minExp, maxExp + 1)
  exp = playerData["horse-exp"] + pick
  set_player_data(playerData["name"], "horse-exp", exp)
  
  reply = ":racehorse: Under Package :regional_indicator_" + package + ": "
  reply = "Sleipnir gained **" + str(pick) + "** EXP and now has a total of **" + str(exp) + "** EXP."

  if exp >= 100:
    reply = reply + "\n:horse: You have reached the experience limit of 100."
    
  return reply + "\nTotal Horse Exp: " + str(exp) + "\nCurrent Money: :coin: **" + str(currentMoney) + "** Kroner."

def buy_food(playerData, food):
  name = playerData["name"]
  if food not in ["hay", "gysahl"]:
    return ":warning: **" + name + "**, incorrect item bought."

  cost = 50 if food == "hay" else 200
  if playerData["money"] < cost:
    return ":warning: **" + name + "**, insufficient funds."

  currentMoney = add_money(playerData["name"], -1 * cost)
  count = playerData[food] + 1
  set_player_data(playerData["name"], food, count)

  return ":ear_of_rice: You bought **" + food + "**! You currently have: **" + str(count) + "**\nCurrent Money: :coin: **" + str(currentMoney) + "** Kroner."

def harvest_flowers(playerData):

  multiplier = 1 if "CHARMED_SCYTHE" not in playerData["items"] else 1.5
  pick = random.randrange(1, 101)
  name = playerData["name"]
  money = 0
  
  if pick in range(1, 11):
    # ROTTEN (10%)
    reply = ":wilted_rose: **" + name + "**, your harvest is poor and rotten!"
  elif pick in range(11, 36):
    # CARNATIONS (25%)
    money = 30 * multiplier
    reply = ":blossom: **" + name + "**, you sold **Carnations** and earned :coin: **" + str(money) + "** Kroner"
  elif pick in range(36, 56):
    # LAVENDER (20%)
    money = 50 * multiplier
    reply = ":blossom: **" + name + "**, you sold **Lavender** and earned :coin: **" + str(money) + "** Kroner"
  elif pick in range(56, 76):
    # PEONY (20%)
    money = 80 * multiplier
    reply = ":blossom: **" + name + "**, you sold **Peony** and earned :coin: **" + str(money) + "** Kroner"
  elif pick in range(76, 91):
    # ROSE (15%)
    money = 130 * multiplier
    reply = ":rose: You sold **Rose** and earned :coin: **" + str(money) + "** Kroner"
  elif pick in range(91, 101):
    # POPPY (10%)
    money = 200 * multiplier
    reply = ":blossom: **" + name + "**, you sold **Poppy** and earned :coin: **" + str(money) + "** Kroner"
  else:
    reply = "It won't even reach this point. But let's catch it."

  money = int(money)
  currentMoney = add_money(playerData["name"], money)
  if money > 0:
    reply = reply + "\nCurrent money: **" + str(currentMoney) + "** Kroner"
  return reply

def assemble_skidbladnir(playerData):

  items = playerData["items"]
  if "SKIDBLADNIR" in items:
    return ":warning: You already have a **Skidbladnir**!"
  
  if "SCREW" not in items or "SAIL" not in items or "ELMWOOD" not in items:
    return ":x: You do not have enough materials to build the **Skidbladnir**!"

  add_item(playerData["name"], "SKIDBLADNIR")
  remove_item(playerData["name"], "SCREW")
  remove_item(playerData["name"], "SAIL")
  remove_item(playerData["name"], "ELMWOOD")

  return ":cloud: You are now ready to sail the sea and reach the skies! Your *Skidbladnir* is now available."

def assemble_gungnir(playerData):

  items = playerData["items"]
  name = playerData["name"]
  if "SPEAR_OF_GUNGNIR" in items:
    return ":warning: You already have a **Spear of Gungnir**!"

  if ("REDWOOD" in items and items.count("GOLD_INGOT") >= 1 and items.count("BRONZE_INGOT") >= 3 and items.count("SILVER_INGOT") >= 4 and items.count("PLATINUM_INGOT") >= 2):
    remove_item(name, "REDWOOD")
    remove_item(name, "GOLD_INGOT")
    remove_item(name, "BRONZE_INGOT")
    remove_item(name, "BRONZE_INGOT")
    remove_item(name, "BRONZE_INGOT")
    remove_item(name, "SILVER_INGOT")
    remove_item(name, "SILVER_INGOT")
    remove_item(name, "SILVER_INGOT")
    remove_item(name, "SILVER_INGOT")
    remove_item(name, "PLATINUM_INGOT")
    remove_item(name, "PLATINUM_INGOT")
    add_item(name, "SPEAR_OF_GUNGNIR")
    return ":gungnir: You received the **SPEAR OF GUNGNIR**"

  return ":x: You do not have enough materials to create the **SPEAR OF GUNGNIR**!"

def assemble_hammer(playerData):

  items = playerData["items"]
  name = playerData["name"]
  if "HAMMER" in items:
    return ":warning: You already have a **HAMMER**!"

  if (items.count("GOLD_INGOT") >= 2 and items.count("BRONZE_INGOT") >= 4 and items.count("SILVER_INGOT") >= 3 and items.count("PLATINUM_INGOT") >= 1):
    remove_item(name, "GOLD_INGOT")
    remove_item(name, "GOLD_INGOT")
    remove_item(name, "BRONZE_INGOT")
    remove_item(name, "BRONZE_INGOT")
    remove_item(name, "BRONZE_INGOT")
    remove_item(name, "BRONZE_INGOT")
    remove_item(name, "SILVER_INGOT")
    remove_item(name, "SILVER_INGOT")
    remove_item(name, "SILVER_INGOT")
    remove_item(name, "PLATINUM_INGOT")
    add_item(name, "HAMMER")
    return ":hammer: You received the **HAMMER**"

  return ":x: You do not have enough materials to create the **HAMMER**!"

def mine_level(playerData, level):

  name = playerData["name"]
  cost = 0
  bronzeChance = 0
  silverChance = 0
  goldChance = 0
  platinumChance = 0
  
  if level == 1:
    cost = 20
    bronzeChance = 30
    silverChance = 20
    goldChance = 12
    platinumChance = 5
  elif level == 2:
    cost = 45
    bronzeChance = 45
    silverChance = 27
    goldChance = 16
    platinumChance = 8
  elif level == 3:
    cost = 75
    bronzeChance = 60
    silverChance = 33
    goldChance = 22
    platinumChance = 13
  else:
    return ":warning: Invalid level input!"

  money = playerData["money"]
  if money < cost:
    return ":warning: Insufficient funds."

  currentMoney = add_money(name, -1 * cost)
  bronzePick = random.randrange(1, 101)
  silverPick = random.randrange(1, 101)
  goldPick = random.randrange(1, 101)
  platinumPick = random.randrange(1, 101)

  minedItemsCount = 0
  reply = ":pick: You have mined the following: "
  
  if bronzePick <= bronzeChance:
    reply = reply + "\n- Bronze Ingot"
    minedItemsCount = minedItemsCount + 1
    add_item(name, "BRONZE_INGOT")

  if silverPick <= silverChance:
    reply = reply + "\n- Silver Ingot"
    minedItemsCount = minedItemsCount + 1
    add_item(name, "SILVER_INGOT")

  if goldPick <= goldChance:
    reply = reply + "\n- Gold Ingot"
    minedItemsCount = minedItemsCount + 1
    add_item(name, "GOLD_INGOT")

  if platinumPick <= platinumChance:
    reply = reply + "\n- Platinum Ingot"
    minedItemsCount = minedItemsCount + 1
    add_item(name, "PLATINUM_INGOT")

  if minedItemsCount == 0:
    reply = reply + "\nNothing!"

  reply = reply + "\n\nCurrent money left: :coin: **" + str(currentMoney) + "** Kroner"
  return reply

async def visit_caverns(data, playerData):
  await exploreLand(data, playerData, "CAVERN-COASTER")
  return "You have been added to the **Cavern Coaster** thread. Go and check it out!"

def cavern_coaster(playerData, step):

  name = playerData["name"]

  if check_crystal(playerData["crystals"], "NIDAVELLIR"):
      return "**" + name + "**, you already obtained the :gem: **CRYSTAL OF NIDAVELLIR**."

  previousLoop = playerData["cavern-loop"]
  if step != 0 and previousLoop == -1:
    return ":warning: **" + name + "**, you must ride the coaster first!"
  if step != previousLoop + 1:
    return ":warning: **" + name + "**, you have to finish the coaster ride sequentially! Your next Loop: " + str(previousLoop + 1)

  chance = 0
  total = 0
  reply = ""
  
  if step == 0:
    #Disable player from performing anything.
    freeze_player(name, True, "CAVERN_COASTER")
    set_player_data(name, "cavern-loop", 0)
    return ":roller_coaster: **" + name + "**, buckle up! You are now onboard the **CAVERN COASTER.**\nFor **Loop #1**, there is a 6 out of 7 chance of success."
  elif step == 1:
    chance = 6
    total = 7
    reply = ":roller_coaster: **" + name + "**, you survived Loop #1!\nFor **Loop #2**, there is 5 in 6 chance of success.\nTo face it, type this: `$face-loop2`"
  elif step == 2:
    chance = 5
    total = 6
    reply = ":roller_coaster: **" + name + "**, you survived Loop #2!\nFor **Loop #3**, there is 4 in 5 chance of success.\nTo face it, type this: `$face-loop3`"
  elif step == 3:
    chance = 4
    total = 5
    reply = ":roller_coaster: **" + name + "**, you survived Loop #3!\nFor **Loop #4**, there is 3 in 4 chance of success.\nTo face it, type this: `$face-loop4`"
  elif step == 4:
    chance = 3
    total = 4
    reply = ":roller_coaster: **" + name + "**, you survived Loop #4!\nFor **Loop #5**, there is 2 in 4 chance of success.\nTo face it, type this: `$face-loop5`"
  elif step == 5:
    chance = 2
    total = 4
    reply = "**" + name + "**, congratulations! You have claimed the :gem: **CRYSTAL OF NIDAVELLIR** along with :coin: **300** Krone."

  pick = random.randrange(1, total + 1)
  if pick <= chance:
    set_player_data(name, "cavern-loop", step)
    if step == 5:
      currentMoney = add_money(name, 300)
      reply = reply + "\nCurrent money: :coin: **" + str(currentMoney) + "** Kroner"
      freeze_player(playerData["name"], False, "")
      add_crystal(playerData["name"], 'NIDAVELLIR')
  else:
    #Unfreeze
    reply = ":roller_coaster::x: **" + name + "**, you are unsuccessful in clearing the loop. You may go back to Step 1 and try again!"
    freeze_player(playerData["name"], False, "")
    set_player_data(name, "cavern-loop", -1)
    
  return reply

def place_statue(playerData, item):

  if "NIFLHEIM" in playerData["crystals"]:
    return "You already have the :gem: **CRYSTAL OF NIFLHEIM** :gem:"

  if item.upper() not in playerData["items"]:
    return ":warning: You don't have that item in your inventory."

  if item.upper() == "HARP":
    add_crystal(playerData["name"], "NIFLHEIM")
    return "The sound barrier has been destroyed as Ymir's hands delicately play the harp. Then, the :gem: **CRYSTAL OF NIFLHEIM** is revealed and goes to your inventory"
  else:
    return "Nothing happens."

async def ride_to_hel(data, playerData, step):

  name = playerData["name"]

  previousLoop = playerData["sleipnir-gallop"]
  print(previousLoop)
  if step != 0 and previousLoop == -1:
    return ":warning: **" + name + "**, you must ride :horse: Sleipnir first!"
  if step != previousLoop + 1:
    return ":warning: **" + name + "**, you must gallop over chasms sequentially! Your next chasm: " + str(previousLoop + 1)

  horseExp = playerData["horse-exp"]
  horseExp = horseExp if horseExp < 100 else 100
  temporaryDecreaseExp = 0
  reply = ""
  
  if step == 0:
    #Disable player from performing anything.
    freeze_player(name, True, "SLEIPNIR_TO_HEL")
    set_player_data(name, "sleipnir-gallop", 0)
    return ":carousel_horse: **" + name + "**, saddle up! You are now riding **Sleipnir.**\nTo jump over **Chasm #1**, type: `$gallop-chasm1`"
  elif step == 1:
    temporaryDecreaseExp = 0
    reply = ":carousel_horse: For **Chasm #2**, Sleipnir's EXP is temporarily reduced by 5 EXP.\nTo cross it, type in your Individual Discord: `$gallop-chasm2`"
  elif step == 2:
    temporaryDecreaseExp = 5
    reply = ":carousel_horse: For **Chasm #3**, Sleipnir's EXP is temporarily reduced by 15 EXP.\nTo cross it, type in your Individual Discord: `$gallop-chasm3`"
  elif step == 3:
    temporaryDecreaseExp = 15
    reply = ":carousel_horse: For **Chasm #4**, Sleipnir's EXP is temporarily reduced by 25 EXP.\nTo cross it, type in your Individual Discord: `$gallop-chasm4`"
  elif step == 4:
    temporaryDecreaseExp = 25
    reply = ":carousel_horse: Congratulations! You have managed to enter the realm of *Hel*!"

  tempExp = (horseExp - temporaryDecreaseExp)
  if tempExp < 0:
    tempExp = 0

  pick = random.randrange(1, 101)
  if step > 4:
    pick = 100
  if pick <= tempExp:
    set_player_data(name, "sleipnir-gallop", step)
    if step == 4:
      await exploreLand(data, playerData, "HEL")
      freeze_player(playerData["name"], False, "")
      set_player_data(playerData["name"], "location", "HEL")
      set_player_data(name, "sleipnir-gallop", -1)
      reply = reply + "\nYou have been added to the **Hel** thread. Go and check it out!"
      #Do exploration of Hel here
  else:
    #Unfreeze
    reply = ":carousel_horse::x: **" + name + "**, Sleipnir still needs more training!!"
    freeze_player(playerData["name"], False, "")
    set_player_data(name, "sleipnir-gallop", -1)
    
  return reply

def battle_hel(playerData):

    if "HEL" in playerData["crystals"]:
      return "You already have the :gem: **CRYSTAL OF HEL** :gem:"
      
    helHP = playerData["hel-hp"]
    if helHP <= 0:
      return "You have defeated **HEL** with your undying faith in the creators. You must now shoot Balder by typing in your Individual Discord: `$shoot-balder`"

    faith = playerData["faith"]
    pick = random.randrange(1, 101)
    if pick <= faith: 
      set_player_data(playerData["name"], "hel-hp", 0)
      return "You have defeated **HEL** with your undying faith in the creators. You must now shoot Balder by typing in your Individual Discord: `$shoot-balder`"
    
    set_player_data(playerData["name"], "location", "NIFLHEIM")
    return "You have been thrown back to **NIFLHEIM**. Get stronger. Have more faith."

def shoot_balder(playerData):

  if "HEL" in playerData["crystals"]:
    return "You already have the :gem: **CRYSTAL OF HEL** :gem:" 

  helHp = playerData["hel-hp"]
  items = playerData["items"]
  if helHp > 0:
    return "Beat Hel first before doing anything to Balder!"
  if helHp == 0 and "SPEAR_OF_GUNGNIR" not in items:
    return "You don't have the right legendary weapon to shoot Balder!"
  if helHp == 0 and "SPEAR_OF_GUNGNIR" in items and playerData["spear-imbue"] != "MISTLETOE":
    return "You have the right weapon, however Balder remains immune. You need something else."
  if helHp == 0 and "SPEAR_OF_GUNGNIR" in items and playerData["spear-imbue"] == "MISTLETOE":
    add_crystal(playerData["name"], "HEL")
    return "Congratulations! You broke the curse, you now have the :gem: **CRYSTAL OF HEL** :gem: in your inventory."


def generateMarket():

  # Generate based on occurrence
  availableItems = []
  marketItem = {}

  for item in marketItemsJson:
    pick = random.random()
    if pick <= marketItemsJson[item]["appearanceRate"]: 
      pricePick = random.choice(marketItemsJson[item]["price"])
      itemValue = {
        "id" : item,
        "keyword" : marketItemsJson[item]["keyword"],
        "price" : pricePick,
        "description" : marketItemsJson[item]["description"]
      }
      marketItem[item] = itemValue
      availableItems.append(itemValue)

  
  db["norse-marketplace"] = marketItem
  
  return availableItems

def buy_item(playerData, item):
  validItems = ["sail", "screw", "crystal", "scissors", "cutlass", "platinum", "gold", "silver", "bronze", "redwood", "staff", "hatchet", "dagger", "blade", "scythe", "axe"]
  name = playerData["name"]

  if item not in validItems:
    return ":warning: **" + name + "**, that item is not available!"

  availableItem = db["norse-marketplace"]
  itemId = convert_keyword(item)

  try:
    boughtItem = availableItem[itemId]
    price = boughtItem["price"]
    if playerData["money"] < price:
      return ":x: **" + name + "**, you do not have enough money to purchase that."
    currentMoney = add_money(name, -1 * price)
    if itemId == "CRYSTAL_MIDGARD":
      add_crystal(name, "MIDGARD")
    else:
      add_item(name, itemId)
    availableItem.pop(itemId)
    db["norse-marketplace"] = availableItem
    reply = ":basket: **" + name + "**, you purchased **" + boughtItem["description"].title() + "**!"
    reply = reply + "\nCurrent money: :coin: **" + str(currentMoney) + "** Kroner"
    return reply
  except:
    return ":x: **" + name + "**, that item is no longer available!"

def convert_keyword(item):

  if item == "sail":
    return "SAIL"
  elif item == "screw":
    return "SCREW"
  elif item == "crystal":
    return "CRYSTAL_MIDGARD"
  elif item == "scissors":
    return "SCISSORS"
  elif item == "cutlass":
    return "CUTLASS"
  elif item == "platinum":
    return "PLATINUM_INGOT"
  elif item == "gold":
    return "GOLD_INGOT"
  elif item == "silver":
    return "SILVER_INGOT"
  elif item == "bronze":
    return "BRONZE_INGOT"
  elif item == "redwood":
    return "REDWOOD"
  elif item == "staff":
    return "BLACK_OAK_STAFF"
  elif item == "hatchet":
    return "STONE_HATCHET"
  elif item == "dagger":
    return "OSMIUM_DAGGER"
  elif item == "blade":
    return "FURY_BLADE"
  elif item == "scythe":
    return "CHARMED_SCYTHE"
  elif item == "axe":
    return "FIRE_AXE"
  else:
    return "NOT_FOUND"

def build_player_data(playerData):

  name = playerData["name"]

  crystalList = ""
  for crystal in playerData["crystals"]:
    crystalList = crystalList + "Crystal of " + crystal.title() + "\n"
    
  itemList = ""
  legendaryItemList = ""
  
  for item in playerData["items"]:
    description = finalItemsJson[item]["description"]
    if item in ('MJOLLNIR', 'SKIDBLADNIR', 'HARP', 'SPEAR_OF_GUNGNIR'):
      if item == 'SPEAR_OF_GUNGNIR' and playerData["spear-imbue"] != "":
        description = description + " (" + playerData["spear-imbue"].title() + ")"
      legendaryItemList = legendaryItemList + description + "\n"
      continue
    if item.endswith("_INGOT"):
      #Skip. To be added later.
      continue
    itemList = itemList + description + "\n"

  for metal in ["BRONZE", "SILVER", "GOLD", "PLATINUM"]:
    count = playerData["items"].count(metal + "_INGOT")
    if count != 0:
      itemList = itemList + finalItemsJson[metal + "_INGOT"]["description"] + " x" + str(count) + "\n"
    
  embedVar = discord.Embed(title=":man_superhero: **" + name.upper() + "'s PLAYER STATS** :man_superhero:", description="", color=0x0F0000)
  embedVar.add_field(name=':map: LOCATION', value=playerData["location"].title(), inline=False)
  embedVar.add_field(name=':coin: MONEY', value=playerData["money"], inline=True)
  embedVar.add_field(name=':gem: CRYSTALS (' + str(len(playerData["crystals"])) + '/9)', value=crystalList, inline=False)
  embedVar.add_field(name=':briefcase: ITEMS', value=itemList, inline=False)
  embedVar.add_field(name=':sparkles: LEGENDARY ITEMS', value=legendaryItemList, inline=False)

  if playerData["husband"] != "":
    embedVar.add_field(name=':man: SPOUSE', value=playerData["husband"], inline=True)
  if playerData["faith"] > 0:
    embedVar.add_field(name=':pray: FAITH', value=playerData["faith"], inline=True)
  if playerData["horse-growth"] > 0 or playerData["horse-exp"] > 0:
    embedVar.add_field(name=':horse: SLEIPNIR STATS', value="Growth: " + str(playerData["horse-growth"]) + "\nExperience: " + str(playerData["horse-exp"]), inline=True)
  if playerData["hay"] > 0 or playerData["gysahl"] > 0 or playerData["horse-growth"] > 0:
    embedVar.add_field(name=':ear_of_rice: HORSE FOOD', value="Hay: " + str(playerData["hay"]) + "\nGysahl: " + str(playerData["gysahl"]), inline=True)
  if playerData["nidhogg-hp"] < 500:
    hp = playerData["nidhogg-hp"]
    embedVar.add_field(name=":snake: NIDHOGG'S HP", value=":skull_crossbones:" if hp <= 0 else hp, inline=True)

  if name.upper() == "ALEX":
    embedVar.set_thumbnail(url = 'https://i.ibb.co/71kKPsj/Alex.png')
  elif name.upper() == "JIVE":
    embedVar.set_thumbnail(url = 'https://i.ibb.co/HNNJzJK/Jive.png')
  elif name.upper() == "KYLE":
    embedVar.set_thumbnail(url = 'https://i.ibb.co/MkxwYJS/KyleC.png')
  elif name.upper() == "VINCE":
    embedVar.set_thumbnail(url = 'https://i.ibb.co/zhHRRTp/Vince.png')
  elif name.upper() == "WERO":
    embedVar.set_thumbnail(url = 'https://i.ibb.co/3R1YHMY/Wero.png')
  else:
    embedVar.set_thumbnail(url = 'https://i.ibb.co/x2K8YCQ/borderland-logo-sq.png')
    
  return embedVar
def pitstop_checkin(playerData):

  if (len(playerData["crystals"]) == 9 and playerData["trigger-ragnarok"] == True and "SERPENT_BLOOD" in playerData["items"]):
    reply = "Congratulations! Screenshot this message and send to your FB GC."
  else:
    reply = "I don't know how you got here, but please finish leg."

  return reply

def start_polishing(playerData):
  #If player has beat idun before, block
  if check_crystal(playerData["crystals"], "VANAHEIM"):
      return "You already obtained the :gem: **CRYSTAL OF VANAHEIM**."

  #Disable player from performing anything.
  freeze_player(playerData["name"], True, "BEJEWELED_GAME")

  norse.wordle.wordle.wordle_player_init(playerData["name"])

  return "**" + playerData["name"] + "**, you polished up real nice! To begin, select a mirror (see instructions)."

def select_mirror(playerData, input):
  # Check if idun has already been defeated before
  if check_crystal(playerData["crystals"], "VANAHEIM"):
      return "You already obtained the :gem: **CRYSTAL OF VANAHEIM**."
    
  return norse.wordle.wordle.select_mirror(playerData["name"], input)

def wordle_solve(playerData, answer):
  # Check if idun has already been defeated before
  if check_crystal(playerData["crystals"], "VANAHEIM"):
      return "You already obtained the :gem: **CRYSTAL OF VANAHEIM**."
    
  output = norse.wordle.wordle.wordle_solve(playerData["name"], answer)
  if len(db[playerData["name"] + "-wordle-words-taken"]) >= 3:
    output = output + wordle_win(playerData) 
  if db[playerData["name"] + "-wordle-visited"] >= 15:
    wordle_win(playerData)
    output = "You used too much magic already! For your efforts, you have received the :gem: **CRYSTAL OF VANAHEIM** :gem: and added it to your inventory."

  return output

def wordle_win(playerData):
  # Check if idun has already been defeated before
  if check_crystal(playerData["crystals"], "VANAHEIM"):
      return "You already obtained the :gem: **CRYSTAL OF VANAHEIM**."

  #Enable player
  freeze_player(playerData["name"], False, "")
  add_crystal(playerData["name"], 'VANAHEIM')

  return """Congratulations! You have earned the :gem: **CRYSTAL OF VANAHEIM** :gem: and added it to your inventory."""
  