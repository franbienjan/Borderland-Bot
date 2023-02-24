import discord
from replit import db

# Sign-up on earliest available flight.
def book_flight(name):

  setImage = True
  if check_if_booked(name):
    #do something
    airline = "Invalid. You already have a booked ticket."
    color = 0xFF0000
    setImage = False
  else:
    queueNo = db["leg2-flights-counter"]
    db["leg2-flights-" + str(queueNo)] = name
    db["leg2-flights-counter"] = queueNo + 1
    airline = ""
    image = ""
    if queueNo in range(0,3):
      airline = "Asiana Airlines (+0 minutes)"
      image = 'https://i.ibb.co/yffFnxS/Asiana.png'
      color = 0xFF0000
    elif queueNo in range(3,7):
      airline = "Korean Air (+3 minutes)"
      image = 'https://i.ibb.co/Zf9Cqnz/Korean-Air.png'
      color = 0x00008B
    elif queueNo == 7:
      airline = "Jin Air (+6 minutes)"
      image = 'https://i.ibb.co/pnJGNys/Jin-Air.png'
      color = 0xA020F0
    elif queueNo in range(8, 10):
      airline = "Jeju Air (+6 minutes)"
      image = 'https://i.ibb.co/mCDQh4k/Jeju-Air.png'
      color = 0xFFA500
    elif queueNo in range(10, 16):
      airline = "Air Seoul (+9 minutes)"
      image = 'https://i.ibb.co/SvMjLkr/Air-Seoul.png'
      color = 0x2e8b57
    else:
      airline = "Invalid."

  embedMsg = discord.Embed(title=":airplane_small: **" + name +
                             "'s Booked Ticket** :airplane_small:",
                             description="",
                             color=color)
  
  embedMsg.add_field(name='Airline', value=airline, inline=False)
  if setImage:
    embedMsg.set_image(url = image)
  return embedMsg

def clear_tickets():
  db["leg2-flights-counter"] = 0
  for x in range(0, 16):
    db["leg2-flights-" + str(x)] = ''
  return

def view_flights():
  embedMsg = discord.Embed(title=":airplane: **Flight List** :airplane:",
                             description="",
                             color=0x89CFF0)
  asianaList = ""
  koreanList = ""
  jinList = ""
  jejuList = ""
  seoulList = ""
  
  for x in range(0, 15):
    try:
      if x in range(0, 3):
        asianaList = asianaList + db["leg2-flights-" + str(x)] + "\n"
      elif x in range(3, 7):
        koreanList = koreanList + db["leg2-flights-" + str(x)] + "\n"
      elif x == 7:
        jinList = db["leg2-flights-" + str(x)] + "\n"
      elif x in range(8, 10):
        jejuList = jejuList + db["leg2-flights-" + str(x)] + "\n"
      elif x in range(10, 15):
        seoulList = seoulList + db["leg2-flights-" + str(x)] + "\n"
    except:
      continue
  
  embedMsg.add_field(name="Asiana Airlines (+0 minutes)", value=asianaList, inline=False)
  embedMsg.add_field(name="Korean Air (+3 minutes)", value=koreanList, inline=False)
  embedMsg.add_field(name="Jin Air (+6 minutes)", value=jinList, inline=False)
  embedMsg.add_field(name="Jeju Air (+6 minutes)", value=jejuList, inline=False)
  embedMsg.add_field(name="Air Seoul (+9 minutes)", value=seoulList, inline=False)

  return embedMsg

def check_if_booked(name):
  for x in range(0, 16):
    if db["leg2-flights-" + str(x)] == name:
      return True
  return False