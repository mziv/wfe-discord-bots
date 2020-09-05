# community-bot.py

# Warning - as it's implemented right now, this bot should only
# be active in one server at a time!

import os
import asyncio
from discord.ext import commands
import discord
import random
import json
import time
from datetime import datetime
from datetime import timedelta

# Load token from config file
with open('../config.py', 'r') as config:
    tokens = json.load(config)
    TOKEN  = tokens['CIRCLE_TOKEN'] 

UTC_OFFSET = 4
MORNING_CIRCLE_CHANNEL = 688863645064888400 # general
ADMIN_LIST = [141368839521697792, 689502497391640681] # Maya, Jud  
COMMAND_CHANNELS = [689806899268550708] # no-kids-garbage-time
DEFAULT_HOUR = 10 # send message at 10am
CHAR_LIMIT = 2000

def check_permissions(ctx):
    return ctx.channel.id in COMMAND_CHANNELS or ctx.author.id in ADMIN_LIST

bot = commands.Bot(command_prefix='#', help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('This bot is in the following guilds:')
    for guild in bot.guilds:
       print(' -', guild.name)
    await bot.change_presence(activity=discord.Game(name='circles and questions | #help'))

@bot.command()
async def help(ctx):
    if not check_permissions(ctx):
        return
    response  = 'Here are all the things I know how to do!\n'
    response += '`#help` - list all the commands I know\n'
    response += '`#add` - add a question to my question bank (make sure to surround it with quotes)\n'
    response += '`#list` - list all of the questions I have stored\n'
    response += '`#remove` - remove a question from my question bank (make sure to surround it with quotes)\n'
    await ctx.send(response)
    

class MorningCircle(commands.Cog):
    def __init__(self, bot, question_file):
        self.bot = bot
        self.question_file = question_file
        with open(question_file, 'r+') as qs:
            self.question_bank = [q.strip() for q in qs.readlines()]

        print(f'Starting questions: {self.question_bank}')
        self.scheduled_hour = DEFAULT_HOUR
        self.question_channel = MORNING_CIRCLE_CHANNEL

    def write_out_question_file(self):
        with open(self.question_file, 'w') as out:
            for q in self.question_bank:
                out.write(q + "\n")

    async def question_background_task(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                # Target time is today but at a specific hour
                target_time = datetime.now().replace(hour=self.scheduled_hour + UTC_OFFSET, minute=0, second=0, microsecond=0)
                # Adjust the current time from UTC to EST
                current_time = datetime.now()
                # If the target hour is before now, move target to tomorrow
                if current_time.hour >= self.scheduled_hour:
                    target_time = target_time + timedelta(days=1)

                # Calculate n seconds until the target time
                nseconds = (target_time - datetime.now()).total_seconds()
                print(f'Seconds to next question: {nseconds}')
                await asyncio.sleep(nseconds)

                await self.send_question()
                print("Question sent.")

                # Wait long enough to ensure that just in case our timing was off,
                # we don't accidentally double send.
                await asyncio.sleep(5)

            except Exception as e:
                print(str(e))
                await asyncio.sleep(5)

    async def send_question(self):
        # Select a random question and remove it from the question bank
        if len(self.question_bank) == 0:
            response = "Sorry team, I'm out of questions!"
        else:
            question = random.choice(self.question_bank)
            self.question_bank.remove(question)
            self.write_out_question_file()
            question = question.replace('\\n', '\n')
            response = "Today's morning circle question is: \n" + question

        await self.bot.get_channel(self.question_channel).send(response)

    # Commands
    @commands.command(name='add', help='Add a question to my question bank. Surround multi-word entries with "".')
    async def addinfo(self, ctx, question):
        if not check_permissions(ctx):
            return 
        self.question_bank.append(question.replace('\n', '\\n'))
        self.write_out_question_file()

        # Reply with confirmation
        response = f'Added \"{question}\" to the bank of questions.'
        await ctx.send(response)

    @commands.command(name='list', help='List all of the questions in my question bank.')
    async def list(self, ctx):
        if not check_permissions(ctx):
            return 
        response  = 'Stored questions:\n'
        for q in self.question_bank:
            if len(response) + len(q) > CHAR_LIMIT:
                await ctx.send('There are too many questions you absolute lunatics.')
                time.sleep(2)
                return
                # await message.channel.send('...jk here u go')
                # await message.channel.send(response)
                # response = ''
            response += ' - ' + q + '\n'
        await ctx.send(response)

    @commands.command(name='remove', help='Remove a question from the bank.')
    async def remove(self, ctx, question):
        if not check_permissions(ctx):
            return 
        question = question.strip().replace('\n', '\\n')
        if question in self.question_bank:
            self.question_bank.remove(question)
            self.write_out_question_file()
            response = 'Successfully removed.'
        else:
            response = 'Sorry, I couldn\'t find that question.'
        await ctx.send(response)

bot_cog = MorningCircle(bot, "questions.txt")
bot.add_cog(bot_cog)
bot.loop.create_task(bot_cog.question_background_task())
bot.run(TOKEN)
