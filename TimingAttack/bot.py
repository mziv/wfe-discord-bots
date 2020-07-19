# bot.py
import json
import random
from discord.ext import commands

with open('../config.py', 'r') as config:
    tokens = json.load(config)
    TOKEN  = tokens['TIMING_TOKEN'] 

# Necessary state
PREFIX   = 'ace'
password = 'acedef'
attempts = 0

bot = commands.Bot(command_prefix='!')

def code_format(s):
    return "```diff\n" + s + "```"

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('This bot is in the following guilds:')
    for guild in bot.guilds:
       print(' -', guild.name)

@bot.command(name='set', help='Sets the secret password.', hidden=True)
async def set_pwd(ctx, message: str):
    global password
    global attempts
    password = PREFIX + message.lower()
    attempts = 0
    await ctx.send("Set password to: `" + password + "`")

@bot.command(name='login', help='Attempt a login.')
async def take_turn(ctx, guess: str):
    global attempts
    attempts += 1

    if len(guess) > len(password):
        await ctx.send(code_format("- ERROR: Password entry exceeded max length."))
        return

    guess = guess.lower()
    time_spent = random.uniform(0, 0.1)
    time_unit = 1
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
    elif attempts > 6:
        response += f'\n\n+ NOTE: Password attempts are processed in order from front to back.'
    await ctx.send(code_format(response))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(code_format('This command requires an argument.'))
    else: 
        print(error)


bot.run(TOKEN)