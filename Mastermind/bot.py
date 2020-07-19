# bot.py
import json
import random
from discord.ext import commands

with open('../config.py', 'r') as config:
    tokens = json.load(config)
    TOKEN  = tokens['MASTER_TOKEN'] 

SEQ_LEN = 4
N_TURNS = 10

class MMGame:
    def __init__(self):
        self.reset()
        self.active = False

    def reset(self):
        self.turns_left = N_TURNS
        self.sequence = "".join(random.choice('abcdef') for _ in range(SEQ_LEN))
        self.active = True

    def check(self, guess):
        self.turns_left -= 1
        correct = self.sequence

        # First, get all the perfect ones
        n_perfect = 0
        to_remove = []
        for i in range(len(self.sequence)):
            if self.sequence[i] == guess[i]:
                to_remove.append(i)

        n_perfect = len(to_remove)
        for i in to_remove[::-1]:
            correct = correct[:i] + correct[i+1:]
            guess = guess[:i] + guess[i+1:]

        # Next, get all the vaguely correct ones
        n_half = 0
        for c in guess:
            if c in correct:
                n_half += 1
                i = correct.index(c)
                correct = correct[:i] + correct[i+1:]

        return (n_perfect, n_half)

    def end_game(self):
        self.active = False

# Necessary state
bot = commands.Bot(command_prefix='!')
active_game = MMGame()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('This bot is in the following guilds:')
    for guild in bot.guilds:
       print(' -', guild.name)

@bot.command(name='start', help='Starts a game.')
async def start(ctx):
    active_game.reset()
    await ctx.send(f'Game begun. You have {N_TURNS} turns to crack the password, which will be made up of characters from a-f. Send `!guess xxxx` to make your guess.')

@bot.command(name='guess', help='Make a guess in an active game.')
async def guess(ctx, guess):
    if active_game.turns_left <= 0:
        await ctx.send(f'You have lost. The winning answer was {active_game.sequence}. Send `!start` to start a new game.')
        return

    if not active_game.active:
        await ctx.send(f'There is no active game. Send `!start` to start a new game.')
        return

    if len(guess) != len(active_game.sequence):
        await ctx.send(f'Your guess isn\'t the right length. Make sure it\'s {SEQ_LEN} characters long.')
        return

    result = active_game.check(guess)
    if result[0] == SEQ_LEN:
        active_game.end_game()
        await ctx.send(f'Congratulations, you\'ve won!')
        return

    await ctx.send(f'{result[0]} exacts, {result[1]} nears (guesses remaining: {active_game.turns_left})')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('This command requires an argument.')
    else: 
        print(error)

bot.run(TOKEN)