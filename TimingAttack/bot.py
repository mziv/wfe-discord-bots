# bot.py
# to look into: https://github.com/Rapptz/discord.py/blob/e2de93e2a65960c9c83e8a2fe53d18c4f9600196/discord/ext/commands/bot.py#L622

import json
import random
from discord.ext import commands
import discord

with open('../config.py', 'r') as config:
    tokens = json.load(config)
    TOKEN  = tokens['TIMING_TOKEN'] 

# Necessary state
PREFIX   = 'ace'
password = 'acedef'
attempts = 0

bot = commands.Bot(command_prefix='+')

def code_format(s):
    return "```diff\n" + s + "```"

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('This bot is in the following guilds:')
    for guild in bot.guilds:
       print(' -', guild.name)
    await bot.change_presence(game=discord.Game(name='All things radar | +help'))

@bot.command(name='set', help='Sets the secret password.', hidden=True)
async def set_pwd(ctx, message: str):
    # Verify authentication
    allowed = False
    for role in ctx.author.roles:
        if role.name in ["Staff", "Builder"]:
            allowed = True
    if not allowed:
        return 

    global password
    global attempts
    password = PREFIX + message.lower()
    attempts = 0
    await ctx.send("Set password to: `" + password + "`")

@bot.command(name='try', help='Attempt a login.')
async def take_turn(ctx, guess: str):
    global attempts
    attempts += 1

    if len(guess) > len(password):
        await ctx.send(code_format("- ERROR: Password entry exceeded max length."))
        return

    guess = guess.lower()
    time_spent = random.uniform(0, 0.1)
    time_unit = 10
    for i in range(min(len(guess), len(password))):
        if guess[i] == password[i]:
            time_spent += time_unit
        else:
            break

    if guess == password:
        await ctx.send(code_format("Correct Authentication."))
        return

    response = "- ERROR: Incorrect Authentication.\nProcessing time: " + str(time_spent) + " cycs"
    if attempts > 3 and attempts <= 6:
        response += f'\n\n+ NOTE: Excessive login attempts registered. Remember that all passwords begin with the mandatory prefix \"{PREFIX}\" and are made up of characters in the range a-f.'
    elif attempts > 6 and attempts <= 9:
        response += f'\n\n+ NOTE: Password attempts are processed in order from front to back.'
    elif attempts > 9 and attempts <= 12:
        response += f'\n\n+ NOTE: Authentication system reminders can be accessed using the `!hint` command.'
    await ctx.send(code_format(response))

@bot.command(name='hint', help='Helpful tips about the authentication system.', hidden=True)
async def hint(ctx):
    response =  f'+ NOTE: Excessive login attempts registered. Remember that all passwords begin with the mandatory prefix \"{PREFIX}\" and are made up of characters in the range a-f.'
    response += f'\n\n+ NOTE: Password attempts are processed in order from front to back.'
    await ctx.send(code_format(response))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(code_format('This command requires an argument.'))
    else: 
        print(error)


bot.run(TOKEN)