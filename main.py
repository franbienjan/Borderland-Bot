# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import discord
import os
import json
import leg01.jesters
import leg02.tickets
import leg05.eeaao
import leg06.pacific
import norse.norsemain
import utils.utils
from replit import db
from discord.ext import tasks
from datetime import datetime
from datetime import timedelta
from pytz import timezone
import Image
from PIL import Image
from io import BytesIO
from urllib.request import urlopen

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

officialRoles = json.load(open('official-roles.json'))
paramoreTVJson = json.load(open('paramore-tv.json'))

###############################################
##            TAR in Borderland              ##
##             Friday Bot Codes              ##
###############################################


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@tasks.loop(seconds = 120)
async def generateMarket():

    channel = client.get_channel(1076053510103244850)
    availableItems = norse.norsemain.generateMarket()
  
    time_now = datetime.now(timezone('Asia/Manila'))
    time_now = time_now + timedelta(minutes=2)
    validUntil = time_now.strftime("%H:%M:%S") 

    embedVar = discord.Embed(title=":basket: **MIDGARD MARKET** :basket:", description="", color=0x0F0000)
    embedVar.add_field(name='Valid Until', value=validUntil, inline=False)

    for item in availableItems:
      embedVar.add_field(name=item["description"] + " (" + item["keyword"] + ")", value= ":coin: " + str(item["price"]) + " Kroner", inline=False)

    await channel.send(embed=embedVar)

def tv_init(name):
  #with spare index
  db[name + "-tv"] = [False, False, False, False, False, False, False, False, False, False]
  return ":tv: You are now ready!"

async def display_tv_screens(data, name):

  output = ""
  screens = Image.open(urlopen("https://i.ibb.co/PWSjdn6/base-tv.png"))
  static = Image.open(urlopen("https://i.ibb.co/4Y6VZnP/static.png"))

  recordedChannels = db[name + "-tv"]

  if not recordedChannels[1]:
    screens.paste(static, (35, 67))
  if not recordedChannels[2]:
    screens.paste(static, (345, 67))
  if not recordedChannels[3]:
    screens.paste(static, (655, 67))
  if not recordedChannels[4]:
    screens.paste(static, (35, 360))
  if not recordedChannels[5]:
    screens.paste(static, (345, 360))
  if not recordedChannels[6]:
    screens.paste(static, (655, 360))
  if not recordedChannels[7]:
    screens.paste(static, (35, 648))
  if not recordedChannels[8]:
    screens.paste(static, (345, 648))
  if not recordedChannels[9]:
    screens.paste(static, (655, 648))

  with BytesIO() as image_binary:
                    screens.save(image_binary, 'PNG')
                    image_binary.seek(0)
                    await data.send(file=discord.File(fp=image_binary, filename='screens.png'))
  
@client.event
async def on_message(message):

    content = message.content
    channel = message.channel
    author = message.author
    authorName = message.author.display_name
    guild = message.guild

    if author == client.user:
        return

    #*************************************************
    # Leg 11: Paramore
    #*************************************************
    if content == "$show-tv":
      await display_tv_screens(channel)
      return

    if content == "$paramore-thenews":
      reply = tv_init(authorName)
      await channel.send(reply)
      await display_tv_screens(channel, authorName)
      return

    if content.startswith("$turn-on-"):
      tvNum = int(content.split("$turn-on-", 1)[1])
      db[authorName + "-tv"][tvNum] = True
      await display_tv_screens(channel, authorName)
      return

    if content.startswith("$turn-off-"):
      tvNum = int(content.split("$turn-off-", 1)[1])
      db[authorName + "-tv"][tvNum] = False
      await display_tv_screens(channel, authorName)
      return

    if content == "$pull-lever":

      if db[authorName + "-tv"] == [False, True, True, False, True, True, False, False, False, True]:
        await channel.send("https://i.ibb.co/CPX9ygZ/success-tv.png")
      else:
        db[authorName + "-tv"] = [False, False, False, False, False, False, False, False, False, False]
        await display_tv_screens(channel, authorName)
      return
    
    #*************************************************
    # Leg 10: Norse Mythology
    #*************************************************
    # Initialize
    if content == "$norse-enter":
      await norse.norsemain.norse_welcome(guild, author)
      await channel.send("**" + authorName + "**, welcome to Asgard!")

    # Admin content to channel content to norse only
    if content == "$norse-mode-on":
      db["norse-only"] = True
      await channel.send("Norse World mode is ON. Only commands related to Norse Leg shall be recognized.")
      return

    if content == "$norse-mode-off":
      db["norse-only"] = False
      await channel.send("Norse World mode is OFF. Commands related to Norse leg shall not be recognized.")
      return

    if content == "$norse-gold-init":
      norse.norsemain.norse_gold_init()
      return

    if content == "$norse-market-init":
      generateMarket.start()
      return

    #if (authorName == 'Friday') and content.startswith("$"):
    if db["norse-only"] and content.startswith("$"):
      #Dispatch content to norsemain.py
      await norse.norsemain.norse_main(message)
      return

    #*************************************************
    # Leg 01: Jester's Duel
    #*************************************************
    if utils.utils.check_channel(channel.id, 'leg1-jesters'):
        if content.startswith('$draw-'):
            if db[authorName + '-01-win'] == True:
                await channel.send('**' + authorName + '**, you already won!')
                return
            if db[authorName + '-01-lock'] == 1:
                await channel.send('**' + authorName +
                                   '**, you cannot draw cards anymore.')
                return

            try:
                suit = content.split('$draw-', 1)[1]
                card = leg01.jesters.draw_card(suit)
            except:
                await channel.send(
                    '**' + authorName +
                    '**, we cannot understand your input. Try again.')
                return

            leg01.jesters.save_card(authorName, card)
            await channel.send('**' + authorName + '**, you drew: ' +
                               leg01.jesters.style_card(card))
            return

        if content == '$deck-show':
            if db[authorName + '-01-win'] == True:
                await channel.send('**' + authorName + '**, you already won!')
                return
            outputData = leg01.jesters.review_cards(authorName)
            await channel.send(embed=outputData)
            return

        if content == '$deck-reset':
            if db[authorName + '-01-win'] == True:
                await channel.send('**' + authorName + '**, you already won!')
                return
            leg01.jesters.reset_cards(authorName)
            await channel.send('**' + authorName +
                               '**, your cards have been reset.')
            return

        if content == '$deck-ready':
            if db[authorName + '-01-win'] == True:
                await channel.send('**' + authorName + '**, you already won!')
                return
            if leg01.jesters.check_cards(authorName):
                db[authorName + '-01-lock'] = 1
                await channel.send(
                    '**' + authorName +
                    '**, your deck is now locked. Choose a jester to challenge.'
                )
            else:
                await channel.send('**' + authorName +
                                   '**, you have a card missing in your deck.')
            return

        if content.startswith("$jester-"):
            if db[authorName + '-01-win'] == True:
                await channel.send('**' + authorName + '**, you already won!')
                return
            if leg01.jesters.lock_check_cards(authorName):
                jesterNo = content.split('$jester-', 1)[1]
                if not jesterNo.isdigit() or int(jesterNo) not in range(1, 21):
                    await channel.send(
                        '**' + authorName +
                        '**, invalid input. Choose a jester from 1-20 only.')
                    return
                if (db["jester-" + jesterNo] != ""):
                    await channel.send(
                        '**' + authorName +
                        '**, that jester has already been defeated. Choose another.'
                    )
                    return
                outputData = leg01.jesters.challenge(authorName, jesterNo)
                await channel.send(embed=outputData["embedMsg"])
            else:
                await channel.send(
                    '**' + authorName +
                    '**, your deck is not yet ready. Build and lock it first!')
            return

        if content == '$deck-start':

            leg01.jesters.player_init(authorName)
            await channel.send('**' + authorName +
                               '**, you may now start building!')
            return

        if content == '$deck-rb-advantage':
            if db[authorName + '-01-win'] == True:
                await channel.send('**' + authorName + '**, you already won!')
                return
            outputMsg = leg01.jesters.rb_advantage(authorName)
            await channel.send(embed=outputMsg)
            return

        if content == "$jesters-review":
            embedVar = leg01.jesters.review_jesters()
            await channel.send(embed=embedVar)
            return

        # ADMIN FUNCTIONS
        if check_role(author.roles, ["Admin"]):
            if content == '$jesters-reset':
                leg01.jesters.jesters_reset()
                await channel.send('**' + authorName +
                                   '**, all jesters have been reset.')
                return

    #*************************************************
    # Leg 02: Airport Booking System
    #*************************************************
    if content == '$leg2booking-singlesinferno':
        await utils.utils.move_member(guild, channel, 1074653254010552350,
                                      author)
        return

    if content == '$leg2-flightreset':
        leg02.tickets.clear_tickets()
        await channel.send("Tickets now available for booking.")
        return

    if utils.utils.check_channel(channel.id, 'leg2-airport'):
        if content == "$leg2-bookflight":
            embedResp = leg02.tickets.book_flight(authorName)
            await channel.send(embed=embedResp)
            return

        if content == '$leg2-flightlist':
            embedResp = leg02.tickets.view_flights()
            await channel.send(embed=embedResp)
            return
    
    #*************************************************
    # Leg 05: Everything Everywhere All At Once
    #*************************************************
    if content.startswith('$multiverse-'):
        data = leg05.eeaao.verse_jump(content)
        if data["status"]:
          await channel.send(data["image"])
          if leg05.eeaao.release_keyword(author.roles, data["keyword"]):
            embedVar = discord.Embed(title=" **:izakaya_lantern: " + authorName +
                             "'s Keyword** :izakaya_lantern:",
                             description="",
                             color=0x0F0000)
            embedVar.add_field(name='Variant', value=data["variant"], inline=False)
            embedVar.add_field(name='Keyword', value=data["keyword"], inline = False)
            await channel.send(embed=embedVar)
          
        return
      
    if content.startswith('$everythinglumpia-'):
        if leg05.eeaao.lumpia_attempt(author.roles, content):
          await channel.send("https://i.ibb.co/ZXLxr3D/everything-lumpia.png")
        else:
          await channel.send("**" + authorName + "**, try again!")
        return

    #*************************************************
    # Leg 06: Pacific Islands
    #*************************************************
    if content.startswith('$navigate-'):
        outputData = leg06.pacific.visit_island(content)
        await channel.send(outputData['statement'])
        await channel.send(outputData['coordinates'])
        return

    #1071355890835398676
    #1071360590074888242
    #1071371164804464671
    #1071398434290008104
    #1071429881788895342

    #*************************************************
    # Leg 09: Pyramid
    #*************************************************
    if content == '$leg9-pyramid':
        await utils.utils.move_member(guild, channel, officialRoles['PYRAMID_01'],
                                      author)
        return

    if content == '$leg9-pyramid-too':
        await utils.utils.move_member(guild, channel, officialRoles['PYRAMID_02'],
                                      author)
        return

    if content == '$leg9-pyramid-thr33':
        await utils.utils.move_member(guild, channel, officialRoles['PYRAMID_03'],
                                      author)
        return

    if content == '$leg9-pyramid-4':
        await utils.utils.move_member(guild, channel, officialRoles['PYRAMID_04'],
                                      author)
        return

    if content == '$leg9-pyramid-fifth':
        await utils.utils.move_member(guild, channel, officialRoles['PYRAMID_05'],
                                      author)
        return
    


# Function that checks whether user has valid roles
# NOTE: THIS IS NOT YET WORKING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def check_role(roles, targetRoles):
    #print(roles)
    #roleIds = []
    #map(lambda roleIds: roleIds['id'], roles)
    #print(roleIds)
    #print(set(roleIds).intersection(targetRoles))
    return True  #set(roles).intersection(targetRoles).len() > 0


try:
    client.run(os.getenv("TOKEN"))
except discord.HTTPException as e:
    if e.status == 429:
        print(
            "The Discord servers denied the connection for making too many requests"
        )
        print(
            "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
        )
    else:
        raise e
