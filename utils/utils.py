import json

threads = json.load(open('official-threads.json'))
roles = json.load(open('official-roles.json'))

#Function that adds a role to the author to view a private channel.
async def move_member(guild, channel, roleId, author):

    role = guild.get_role(roleId)
    await author.add_roles(role)
    await channel.send('You have been added to a new channel. Go and check it!')

#Shortcut, but redundant in function
async def add_role(guild, author, roleId):

    role = guild.get_role(roleId)
    await author.add_roles(role)

# Function that checks whether the channel's valid inputs.
def check_channel(channelId, targetChannelName):
    return channelId in (threads[targetChannelName]['id'],
                         threads['lab']['id'])