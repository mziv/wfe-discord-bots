# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands
import json
import random

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True

REPORT_CHANNEL = 751878615477649430
GUILD_ID = 751878614970269729
TRACKING_FILE = "tally.json"


bot = commands.Bot(command_prefix="!", intents=intents)

# one channel for messaging, one channel for reporting


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    print("This bot is in the following guilds:")
    for guild in bot.guilds:
        print(" -", guild.name)

    bot_cog = TallyBot(bot, TRACKING_FILE)
    bot.add_cog(bot_cog)


class TallyBot(commands.Cog):
    def __init__(self, bot, tracking_file):
        self.bot = bot
        self.tracking_file = tracking_file
        # tally is a map from users to {"poop": N, "cry": N}
        self.tally = {}
        if os.path.exists(tracking_file):
            self.tally = json.load(open(tracking_file, "r+"))

        print(f"Starting tallies: {self.tally}")

    def add_tally(self, author_name, kind):
        t_entry = self.tally.get(author_name, {"poop": 0, "cry": 0})
        t_entry[kind] = t_entry[kind] + 1
        self.tally[author_name] = t_entry
        self.log_tally()

    def log_tally(self):
        json.dump(self.tally, open(self.tracking_file, "w+"))

    async def report(self, author):
        t_entry = self.tally.get(author.name, {"poop": 0, "cry": 0})
        t_list = [t_entry["poop"], t_entry["cry"]]
        random.shuffle(t_list)
        channel = self.bot.get_channel(REPORT_CHANNEL)
        guild = await self.bot.fetch_guild(GUILD_ID)
        member = await guild.fetch_member(author.id)
        name = member.nick
        if not name or name == 'None':
            name = author.nick
        if not name or name == 'None':
            name = author.name
        await channel.send(f"{name}: {t_list[0]} {t_list[1]}")

    @commands.command(name="poop", help="Add a poop to your tally")
    async def poop(self, ctx):
        print(f"poop called by {ctx.author}")
        self.add_tally(ctx.author.name, "poop")
        await ctx.send(f"poop registered.")
        await self.report(ctx.author)

    @commands.command(name="cry", help="Add a cry to your tally")
    async def cry(self, ctx):
        print(f"cry called by {ctx.author}")
        self.add_tally(ctx.author.name, "cry")
        await ctx.send(f"cry registered.")
        await self.report(ctx.author)


bot.run(TOKEN)
