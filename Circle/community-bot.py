# community-bot.py

# Warning - as it's implemented right now, this bot should only
# be active in one server at a time!

import os
import asyncio
import discord
import random
import json
# from config import TOKEN
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

ADD_COMMAND     = 'add'
HELP_COMMAND    = 'help'
LIST_COMMAND    = 'list'
REMOVE_COMMAND  = 'remove'
CHANNEL_COMMAND = 'channel'

class MorningCircle(discord.Client):
    def __init__(self, question_file):
        # Call parent constructor
        super().__init__()

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
        await self.wait_until_ready()

        while not client.is_closed():
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
            response = "Today's morning circle question is: \n" + question

        await self.get_channel(self.question_channel).send(response)

    async def handle_command(self, message):
        command = message.content[1:].strip()
        print(f'Received command: {command}')

        # Default response
        response = 'Sorry, I don\'t recognize that command. Try `# help` for a list of commands I do know.'

        if command.startswith(HELP_COMMAND):
            response  = 'Here are all the things I know how to do!\n'
            response += '`# help` - list all the commands I know\n'
            response += '`# add` - add a question to my question bank (put the question after the word add)\n'
            response += '`# list` - list all of the questions I have stored\n'
            response += '`# remove` - remove a question from my question bank (put the question after the word remove)\n'
            #response += '`# channel` - set the channel I should be sending questions to in the morning\n'
        elif command.startswith(ADD_COMMAND):
            question = command[len(ADD_COMMAND):].strip()
            if len(question) == 0:
                response = "Please add a question after that command."
            self.question_bank.append(question)
            self.write_out_question_file()

            # Reply with confirmation
            response = f'Added \"{question}\" to the bank of questions.'

        elif command.startswith(LIST_COMMAND):
            response  = 'Stored questions:\n'
            for q in self.question_bank:
                response += ' - ' + q + '\n'

        elif command.startswith(REMOVE_COMMAND):
            if message.author.id not in ADMIN_LIST:
                response = 'Sorry, you\'re not authorized to take that action.'
            else:
                question = command[len(REMOVE_COMMAND):].strip()
                if question in self.question_bank:
                    self.question_bank.remove(question)
                    self.write_out_question_file()
                    response = 'Successfully removed.'
                else:
                    response = 'Sorry, I couldn\'t find that question.'
        elif command.startswith(CHANNEL_COMMAND):
            return # disabled for now!
            channel = command[len(CHANNEL_COMMAND):].strip()
            response = 'Sorry, I couldn\'t find the specified channel.'
            for c in self.guilds[0].channels:
                if c.name == channel:
                    self.question_channel = c.id
                    response = f'Morning circle questions will now be sent to {channel}.'

        await message.channel.send(response)

    async def on_message(self, message):
        # We don't want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.channel.id in COMMAND_CHANNELS or message.author.id in ADMIN_LIST:
            # Passively listen for messages directed at the bot
            if message.content.startswith('#'):
                await self.handle_command(message)

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        print('This bot is in the following guilds:')
        for guild in self.guilds:
           print(' -', guild.name)

client = MorningCircle("questions.txt")
client.loop.create_task(client.question_background_task())
client.run(TOKEN)
