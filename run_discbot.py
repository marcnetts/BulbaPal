import bulbapal #local
import discord

import os
from dotenv import load_dotenv
load_dotenv()
MYTOKEN = os.environ['MYTOKEN']
WIKIBOT_CHANNEL = os.environ['WIKIBOT_CHANNEL']

client = discord.Client()

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
      return
  if message.channel.id == int(os.getenv('WIKIBOT_CHANNEL')):
    returnedMsg = bulbapal.bulbaParse(message.content)
    if returnedMsg == '💥':
      await message.add_reaction('💥')
    elif message.content == '-help':
      await message.channel.send(returnedMsg.replace('.\n','.\n```\n')+'```')
    elif returnedMsg != None:
      await message.channel.send(returnedMsg[:2000])

client.run(os.getenv('MYTOKEN'))