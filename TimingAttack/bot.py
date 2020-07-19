# bot.py
import json
import random
from discord.ext import commands

with open('../config.py', 'r') as config:
    tokens = json.load(config)
    TOKEN  = tokens['TIMING_TOKEN'] 

# Necessary state
password = 'xxxdef'
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

@bot.command(name='set', help='Sets the secret password.')
@commands.has_any_role("Staff","Builder") 
async def set_pwd(ctx, message: str):
    global password
    global attempts
    password = message.lower()
    attempts = 0
    await ctx.send("Set password to: `" + password + "`")

@bot.command(name='login', help='Attempt a login.')
async def take_turn(ctx, guess: str):
    global attempts
    attempts += 1

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
    if attempts > 3:
        response += "\n\n+ NOTE: Excessive login attempts registered. Remember that all passwords begin with the mandatory prefix XXX and are in the range a-g."
    await ctx.send(code_format(response))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(code_format('This command requires an argument.'))
    else: 
        print(error)


bot.run(TOKEN)