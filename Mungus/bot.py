# bot.py

import json
import random
import discord
from discord.ext import commands
from enum import Enum
from datetime import datetime, timezone
import time

with open('../config.py', 'r') as config:
    tokens = json.load(config)
    TOKEN  = tokens['MUNGUS_TOKEN'] 

# Bot definitions
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='+', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('This bot is in the following guilds:')
    for guild in bot.guilds:
       print(' -', guild.name)
    await bot.change_presence(activity=discord.Game(name='scheduling! | +help'))

class Scheduling(commands.Cog):
    '''
    Feature requests:
     - auto send the poll every sunday
     - add a "consensus" command which reports the most popular day(s) and @s all the people who said they'd come
     - list the date in the message
    '''
    def __init__(self, bot):
        self.bot = bot
        self.weekdays = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday',
                         'friday', 'saturday']

    @commands.command(name='week', help='Create a simple scheduling poll for the next week.')
    async def week(self, ctx, message=None):
        time.sleep(0.5)
        await ctx.message.delete()
        time.sleep(0.5)

        msg = await ctx.send("\N{BAR CHART} " + message) if message else await ctx.send("\N{BAR CHART} Pick a day this week!")

        # Stolen from rachel - apparently a classic way to convert from UTC to PDT
        tomorrow = (datetime.now().weekday() + 2) % 7 # extra +1 because we want it to start tomorrow
        for emoji_name in self.weekdays[tomorrow:] + self.weekdays[:tomorrow]:
            emoji = discord.utils.get(ctx.message.guild.emojis, name=emoji_name)
            await msg.add_reaction(emoji)
        
        # Add the no_entry_sign emojiy.
        await msg.add_reaction("\N{NO ENTRY SIGN}")


bot.add_cog(Scheduling(bot))
bot.run(TOKEN)