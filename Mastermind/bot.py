# bot.py
import json
import random
from discord.ext import commands
import discord
import time

with open('../config.py', 'r') as config:
    tokens = json.load(config)
    TOKEN  = tokens['MASTER_TOKEN'] 

def code_format(s, type='ini'):
    return "```" + type + "\n" + s + "```"

ROLES = [
    "Meteor Marauders",
    "Neo Novaco",
    "The Celestites",
    "Starfleet Dawnbreaker",
    "None"
]

DATA_MAP = {
    "Meteor Marauders": "DATA FILE [EVIDENCE 1]: https://drive.google.com/file/d/1gFcs8DyCtBbjjasTCR4nt2SzEQJ4mx4x/view?usp=sharing",
    "Neo Novaco": "DATA FILE [EVIDENCE 2]: https://drive.google.com/file/d/1K5GCDtUKa62f947EcQRbdCQ9X6NY-SmO/view?usp=sharing",
    "The Celestites": "DATA FILE [EVIDENCE 3]: https://drive.google.com/file/d/1dT8l9cZbz63nERtF3L-mn_FPHmbfZnuo/view?usp=sharing",
    "Starfleet Dawnbreaker": "DATA FILE [EVIDENCE 4]: https://drive.google.com/file/d/1CRj3Iz3e97jouOau4Cd2EXbSOBtTLRDR/view?usp=sharing"
}

class MMGame:
    RANGES   = { 1: 'ab', 2: 'abcd', 3: 'abcdef' }
    SEQ_LENS = { 1: 3, 2: 3, 3: 4 }
    N_TURNS  = 10

    def __init__(self):
        self.active = False
        self.level = 1

    def full_reset(self):
        self.active = False
        self.level = 1

    def reset(self):
        self.turns_left = self.N_TURNS
        self.sequence = "".join(random.choice(self.RANGES[self.level]) for _ in range(self.SEQ_LENS[self.level]))
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

        # Return tuple of the form (won?, (# perfect, # half))
        if n_perfect == len(self.sequence):
            self.win()
            return (True, (-1, -1))

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

        # Return tuple of the form (won?, (# perfect, # half))
        if self.turns_left == 0:
            self.lose()
        return (False, (n_perfect, n_half))

    def guess_valid(self, guess):
        for c in guess:
            if not c in self.RANGES[self.level]:
                return False
        return True

    def win(self):
        if self.level < max(self.SEQ_LENS.keys()):
            self.level += 1
        self.active = False

    def lose(self):
        self.active = False

    def status(self):
        if not self.active:
            return "There is no active hacking session. Send `!begin` to start one."

        blanks = ''.join(['x' for i in range(self.SEQ_LENS[self.level])])
        char_range = self.RANGES[self.level]
        char_range = char_range[0] + '-' + char_range[-1]
        return f'You have [{self.turns_left}] attempts to crack the password, ' + \
               f'which will be made up of characters from [{char_range}]. ' + \
               f'Send `!guess {blanks}` to make your guess.'


bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('This bot is in the following guilds:')
    for guild in bot.guilds:
       print(' -', guild.name)
    await bot.change_presence(activity=discord.Game(name='all things data storage | !help'))

class Backdoor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        self.breach_map = {}
        for role in ROLES:
            self.breach_map[role] = 0
        self.breaches = 0
        self.REQ_BREACHES = 4
        self.guild = None

    async def get_active_game(self, ctx):
        if not ctx.author.id in self.games:
            await ctx.send(code_format(f'There is no active hacking session. Send `!begin` to start one.'))
            return
        game = self.games[ctx.author.id]
        return game

    async def get_user_role(self, ctx):
        # Populate it once we need it, I guess.
        if not self.guild:
            for guild in self.bot.guilds:
                if guild.name == 'Across the Universe':
                    self.guild = guild

        # Now actually get the member.
        member = self.guild.get_member(ctx.author.id)
        if member != None:
            for role in member.roles:
                if role.name in self.breach_map:
                    return role.name
        return "None"

    ### Status reports ###

    @commands.command(name='status', help='Reports info about your hacking session.')
    async def status(self, ctx):
        game = await self.get_active_game(ctx)
        if not game:
            return
        await ctx.send(code_format(f'HACKING AT [LEVEL {game.level}].\n\n' + game.status()))

    @commands.command(name='breaches', help='Reports aggregate info about system integrity.')
    async def breaches(self, ctx):
        role = await self.get_user_role(ctx)
        breaches = self.breach_map[role]
        response =  f'You are breaching for [{role}]. The system has been breached [{breaches}/{self.REQ_BREACHES}] times.\n\n'
        response += f'; System integrity: [{(self.REQ_BREACHES - breaches) * 100 / self.REQ_BREACHES}%]'
        await ctx.send(code_format(response))

    ### Gameplay ###

    @commands.command(name='begin', help='Begin hacking current level.')
    async def begin(self, ctx):
        if not ctx.author.id in self.games:
            self.games[ctx.author.id] = MMGame()
        game = await self.get_active_game(ctx)
        if not game:
            return
        game.reset()
        await ctx.send(code_format(f'[LEVEL {game.level}] HACKING INITIATED.\n\n' + game.status()))

    @commands.command(name='guess', help='Make a guess in your current hacking session.')
    async def guess(self, ctx, guess):
        game = await self.get_active_game(ctx)
        if not game:
            return

        # Error handling
        if not game.active:
            await ctx.send(code_format('There is no active hacking session. Send `!begin` to start one.'))
            return

        if len(guess) != len(game.sequence):
            await ctx.send(code_format(f'Your entry isn\'t the right length. Make sure it\'s [{len(game.sequence)}] characters long.'))
            return

        guess = guess.lower()
        if not game.guess_valid(guess):
            char_range = game.RANGES[game.level]
            char_range = char_range[0] + '-' + char_range[-1]
            await ctx.send(code_format(f'There are invalid characters in this guess. Remember that the valid range of characters is [{char_range}].'))
            return

        level = game.level
        result = game.check(guess)

        # result[0] is True if we won
        if result[0]:
            max_level = max(game.SEQ_LENS.keys())
            if level == max_level:
                await ctx.send(code_format(f'[LEVEL {level} BREACHED].\n\nThere are [{max_level - level}] levels remaining.'))
                await self.win(ctx)
            else:
                await ctx.send(code_format(f'[LEVEL {level}] BREACHED.\n\nThere are [{max_level - level}] levels remaining. Send `!begin` to begin the next level.'))
            return

        # If there are no more turns, we should let them know
        if game.turns_left == 0:
            await ctx.send(code_format(f'- The system detected you - you\'ll have to wait for it to reset before you can try again.\n\nSend `!begin` to try again at this level.', 'diff'))
            return

        await ctx.send(code_format(f'[{result[1][0]}] exacts, [{result[1][1]}] nears.\n\n; You have [{game.turns_left}] attempts left before the system detects you.'))

    @commands.command(name='win', help='for testing; just win the game', hidden=True)
    async def do_win(self, ctx):
        await self.win(ctx)

    async def award_role(self, guild, uid, role_name):
        role = discord.utils.get(guild.roles, name=role_name)
        found = False
        member = guild.get_member(uid)
        if member != None:
            await member.add_roles(role)
            found = True
        return found

    async def win(self, ctx):
        role = await self.get_user_role(ctx)
        self.breach_map[role] += 1
        
        breaches = self.breach_map[role]
        await self.award_role(self.guild, ctx.author.id, 'Code Master')
        await ctx.send(code_format(f'You have breached the system. [Code Master] status acquired. If you wish to contribute another breach, simply send `!begin` again to restart from your current level.'))
        response =  f'The system has been breached [{breaches}/{self.REQ_BREACHES}] times.\n\n'
        response += f'; System integrity: [{max(self.REQ_BREACHES - breaches, 0) * 100 / self.REQ_BREACHES}%]'
        if breaches >= self.REQ_BREACHES:
            response += f'\n\nSystem fully breached! Integrity compromised. New access levels achieved - return to the server and send `!help` for more information.'
        await ctx.send(code_format(response))
    
    ### Reward ###

    @commands.command(name='data', help='Full access to internal systems.')
    @commands.has_any_role('Code Master')
    async def data(self, ctx):
        role = await self.get_user_role(ctx)
        breaches = self.breach_map[role]
        if breaches < self.REQ_BREACHES:
            await ctx.send(code_format(f'- ERROR: System is not fully breached.', 'diff'))
            return
        if role in DATA_MAP:
            await ctx.send(code_format(DATA_MAP[role]))
        else:
            await ctx.send(code_format('There is no data to be found.'))

    ### State-changing options ###

    @commands.command(name='restart', help='Reset your hacking progress.', hidden=True)
    async def restart(self, ctx):
        game = await self.get_active_game(ctx)
        if not game:
            return
        game.full_reset()
        await ctx.send(code_format(f'Hacking state fully reset.'))

    @commands.command(name='reset', help='Reset the number of breaches')
    @commands.has_any_role('Staff', 'Builder')
    async def reset(self, ctx, role):
        if role in self.breach_map:
            self.breach_map[role] = 0
        else:
            self.breach_map["None"] = 0
            role = "None"
        await ctx.send(code_format(f'Number of breaches for [{role}] reset to [0].'))


    @commands.command(name="all", help='Secret, report everything', hidden=True)
    @commands.has_any_role('Staff', 'Builder')
    async def all(self, ctx):
        response = ''
        for r in self.breach_map:
            response += f'{r}: {self.breach_map[r]}\n'
        await ctx.send(code_format(response))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('This command requires an argument.')
    elif isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.send(code_format('This command cannot be used in private messages. Head back to the server and try it there.'))
    elif isinstance(error, commands.errors.MissingAnyRole):
        missing = str(error)[str(error).index(':') + 3:-1]
        await ctx.send(code_format(f'You are not authorized to perform this command. [{missing}] status required.'))
    else: 
        print(type(error))
        print(error)



bot.add_cog(Backdoor(bot))
bot.run(TOKEN)