# bot.py

import json
import random
import discord
from discord.ext import commands
from enum import Enum
import copy

with open('../config.py', 'r') as config:
    tokens = json.load(config)
    TOKEN  = tokens['TIMING_TOKEN'] 

# Constants
PREFIX = 'ace'
NONE  = 'None'
BETA  = 'Beta'
ALPHA = 'Alpha'

START_INFO = [
        '- DAWNBREAKER STARFLEET detected on TERRA CALISTO',
        '- THE CELESTITES detected on AEGIS',
        '- METEOR MARAUDERS detected on ORCOTH',
        '- NEO NOVACO detected on NOVA VICTORIA'
]

def next(al):
    if al == NONE:
        return BETA
    elif al == BETA:
        return ALPHA
    return None

def code_format(s, type='diff'):
    return "```" + type + "\n" + s + "```"

# Bot definitions
bot = commands.Bot(command_prefix='+')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('This bot is in the following guilds:')
    for guild in bot.guilds:
       print(' -', guild.name)
    await bot.change_presence(activity=discord.Game(name='all things radar | +help'))

async def get_member(id):
    members = bot.get_all_members()
    for m in bot.get_all_members():
        print(m.id)
        if m.id == id:
            return m
    return None

class Login(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.passwords = {ALPHA: 'acedefae', BETA: 'aceade'} # default
        self.attempts = 0

    @commands.command(name='reset', help='Resets # of attempts.', hidden=True)
    #@commands.has_any_role('Staff', 'Builder')
    async def reset(self, ctx):
        m = await get_member(ctx.author.id)
        print(m.nickname)
        self.attempts = 0

    @commands.command(name='set', help='Sets the password for level A or B', hidden=True)
    @commands.has_any_role('Staff', 'Builder')
    async def set_pwd(self, ctx, level, message: str):
        if level != ALPHA and level != BETA: 
            await ctx.send("Make sure to specify which level you want to set the password for (alpha or beta).")
            return
        self.passwords[level] = PREFIX + message.lower()
        self.attempts = 0
        await ctx.send(f'Set {level} password to: `{self.passwords[level]}`')

    def get_access_level(self, ctx):
        for role in ctx.author.roles:
            if role.name == "Access Level Alpha":
                return ALPHA
            if role.name == "Access Level Beta":
                return BETA
        return NONE

    async def upgrade_access(self, ctx):
        al = self.get_access_level(ctx)
        beta  = discord.utils.get(ctx.channel.guild.roles, name='Access Level Beta')
        alpha = discord.utils.get(ctx.channel.guild.roles, name='Access Level Alpha')

        if al == NONE:
            await ctx.author.add_roles(beta)
            await ctx.send(code_format(f'Correct Authentication. Elevated {ctx.author.nick}\'s access levels. Type +help to see new abilities.\n\nThere is [1] higher access level available.', 'ini'))
        elif al == BETA:
            await ctx.author.remove_roles(beta)
            await ctx.author.add_roles(alpha)
            await ctx.send(code_format(f'Correct Authentication. Elevated {ctx.author.nick}\'s access levels. Type +help to see new abilities.\n\nThere are [0] higher acces levels available.', 'ini'))

    @commands.command(name='try', help='Attempt a login.')
    async def take_turn(self, ctx, guess: str):
        if type(ctx.channel) == discord.channel.DMChannel:
            await ctx.send(code_format("This bot does not support DMs. Please send all of your commands in the server."))
            return

        al = next(self.get_access_level(ctx))
        if al == None:
            await ctx.send(code_format("+ User has achieved the highest available access level."))
            return

        self.attempts += 1
        pwd = self.passwords[al]

        if len(guess) > len(pwd):
            await ctx.send(code_format("- ERROR: Password entry exceeded max length."))
            return

        guess = guess.lower()
        time_spent = random.uniform(0, 0.1)
        time_unit = 10
        for i in range(min(len(guess), len(pwd))):
            if guess[i] == pwd[i]:
                time_spent += time_unit
            else:
                break

        if guess == pwd:
            await self.upgrade_access(ctx)
            return

        response = f'- ERROR: Incorrect Authentication for Access Level {al}.\nProcessing time: ' + str(time_spent) + " cycs"
        if self.attempts > 3 and self.attempts <= 6:
            response += f'\n\n+ NOTE: Excessive login attempts registered. Remember that all passwords begin with the mandatory prefix \"{PREFIX}\" and are made up of characters in the range a-f.'
        elif self.attempts > 6 and self.attempts <= 9:
            response += f'\n\n+ NOTE: Password attempts are processed in order from front to back.'
        elif self.attempts > 9 and self.attempts <= 12:
            response += f'\n\n+ NOTE: Authentication system reminders can be accessed using the `+hint` command.'
        await ctx.send(code_format(response))

    @commands.command(name='hint', help='Helpful tips about the authentication system.', hidden=True)
    async def hint(self, ctx):
        response =  f'+ NOTE: Excessive login attempts registered. Remember that all passwords begin with the mandatory prefix \"{PREFIX}\" and are made up of characters in the range a-f.'
        response += f'\n\n+ NOTE: Password attempts are processed in order from front to back.'
        await ctx.send(code_format(response))


class Radar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.info = copy.deepcopy(START_INFO)

    @commands.command(name='add', help='Add a line of info to the radar system. Surround multi-word entries with "".')
    @commands.has_role('Access Level Alpha')
    async def addinfo(self, ctx, info):
        self.info.append("- " + info)
        await ctx.send(code_format(f'Added info to radar systems: {info}'))

    @commands.command(name='wipe', help='Wipe everything stored in the radar system.')
    @commands.has_role('Access Level Alpha')
    async def wipe(self, ctx):
        self.info = []
        await ctx.send(code_format('Radar systems wiped.'))

    @commands.command(name='status', help='Report current radar information.')
    @commands.has_any_role('Access Level Beta', 'Access Level Alpha')
    async def status(self, ctx):
        response = '+ Available Access Levels: Beta, Alpha\n\nBattalion Details: https://docs.google.com/document/d/1zaK8UTxrM2aPmw5kivvoKPckthh30nKU-1U5ACOjYXg/edit\n\nCurrent radar info:'
        for info in self.info:
            if len(response + info) > 2000:
                await ctx.send(code_format(response))
                response = ''
            response += '\n' + info
        await ctx.send(code_format(response))

    @commands.command(name='resetinfo', help='Reset radar info to defaults.', hidden=True)
    @commands.has_any_role('Staff', 'Builder')
    async def resetinfo(self, ctx):
        self.info = copy.deepcopy(START_INFO)
        await ctx.send(code_format('Radar info reset.'))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(code_format('This command requires an argument.'))
    elif isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.send(code_format('This command cannot be used in private messages. Head back to the server and try it there.'))
    elif isinstance(error, commands.errors.MissingAnyRole):
        missing = str(error)[str(error).index(':') + 3:-1].replace("'", "")
        await ctx.send(code_format(f'You are not authorized to perform this command. [{missing}] status required.', 'ini'))
    else: 
        print(type(error))
        print(error)

bot.add_cog(Login(bot))
bot.add_cog(Radar(bot))
bot.run(TOKEN)