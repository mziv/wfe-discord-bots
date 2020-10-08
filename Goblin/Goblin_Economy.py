# This bot was written by Cohen.
import json
import os
import random
import discord
import time
import asyncio
import sched
from discord.ext import commands

# os.chdir("/Users/imcohencohen/Desktop/Cohen's Bots")

with open('../config.py', 'r') as config:
    tokens = json.load(config)
    TOKEN  = tokens['GOBLIN_TOKEN'] 

bot = commands.Bot(command_prefix='$')
bot.remove_command('help')
echochannel = None
moneys_track_channel = '763468526391787550'
msg_dump_channel = '763468526391787550'

async def goblin_coefficient(base_amt):
	if base_amt >= 4:
		moneys_amt = 4
	else:
		moneys_amt = base_amt
	print(moneys_amt)
	return(moneys_amt)

async def get_bank_data():
    with open("Goblin Economy.json","r") as f:
        users = json.load(f)

    return users

async def get_nick(member):
    member_nickname = member.nick
    if member_nickname == None:
        member_nickname = member.name
    return member_nickname

async def open_account(user):
	users = await get_bank_data()

	if str(user.id) in users:
		return False
	else:
		users[str(user.id)] = {}
		users[str(user.id)]["moneys"] = 4
	with open("Goblin Economy.json","w") as f:
		json.dump(users, f)
	return True

@bot.event
async def on_message(message: discord.Message):
	member = bot.get_user(252564425511403520)
	if message.guild is None and not message.author.bot:
		await member.send(message.author.mention+" said: "+message.content)
	await bot.process_commands(message)

@bot.command(name='give',aliases=['gift','send','transfer'])
async def give(ctx,message,member:discord.Member):
	await open_account(ctx.author)
	await open_account(member)
	author_nickname = await get_nick(ctx.author)
	member_nickname = await get_nick(member)
	
	giver = ctx.author
	user = member
	users = await get_bank_data()
	message_data = message.split(" ") 
	add_amt = int(message_data[len(message_data) - 1])
	remove_amt = int(message_data[len(message_data) - 1])
	moneys_amt = users[str(user.id)]["moneys"]
	
	if moneys_amt - remove_amt <0:
		await ctx.send(f"{author_nickname}, you do not have that many gobdollars.")
	else:
		await ctx.send(f"{author_nickname} has given {member_nickname} {remove_amt} gobdollars.")
		users[str(giver.id)]["moneys"] -= remove_amt
		users[str(user.id)]["moneys"] += add_amt
		base_amt = users[str(user.id)]["moneys"]
		moneys_amt = await goblin_coefficient(base_amt)
		users[str(user.id)]["moneys"] = moneys_amt
		await ctx.send(f"{member_nickname} now has {moneys_amt} gobdollars.")
		await ctx.author.send(f"You now have {moneys_amt} gobdollars.")
	
	with open("Goblin Economy.json","w") as f:
		json.dump(users,f)

@bot.command(name='add',help="Add defined number of gobdollars to defined user's account")
@commands.has_any_role('Staff')
async def add(ctx,message,member:discord.Member):
	await open_account(member)
	
	member_nickname = await get_nick(member)
	user = member
	users = await get_bank_data()

	message_data = message.split(" ") 
	add_amt = int(message_data[len(message_data) - 1])

	await ctx.send(f"Added {add_amt} gobdollars to {member_nickname}'s account.")

	users[str(user.id)]["moneys"] += add_amt
	base_amt = users[str(user.id)]["moneys"]
	print(base_amt)
	moneys_amt = await goblin_coefficient(base_amt)
	users[str(user.id)]["moneys"] = moneys_amt
	await ctx.send(f"{member_nickname} now has {moneys_amt} gobdollars.")
	with open("Goblin Economy.json","w") as f:
		json.dump(users,f)

@bot.command(name='checkbalance',aliases=['cbal','chkbal'],help="Displays the balance of defined user.")
async def checkbalance(ctx,member:discord.Member):
	await open_account(member)
	
	member_nickname = await get_nick(member)
	user = member
	users = await get_bank_data()
	
	moneys_amt = users[str(user.id)]["moneys"]
	
	em = discord.Embed(title = f"Gobdollar balance",description = f"{moneys_amt}",color = discord.Color(0x75EE10))
	em.set_author(name = member_nickname, icon_url = member.avatar_url)
	
	await ctx.send(embed=em)

@bot.command(name="reset",help="Resets everyone's Moneys to 4")
async def reset(ctx):
	with open("Goblin Economy.json","r") as f:
		users = json.load(f)
		
	for u in users:
		users[u]['moneys'] = 4
		
	with open("Goblin Economy.json","w") as f:
		json.dump(users,f)
	await ctx.send("Moneys successfully reset")

@bot.command(name='inquiry', aliases=['inq'], help='Ask the economy bot a question. Question must be in quotes (" ").')
async def inquiry(ctx,message):
	#user = bot.get_user(252564425511403520)
	channel = bot.get_channel(763468526391787550)
	await channel.send(message)
	#await user.send(message) <uncomment these if you want inquiries PMed to you
	await ctx.send("Processing inquiry. Please hold...")

@bot.command(name='echodm',aliases=['edm'], help='Echos typed phrase in DM to the defined user. Message must be in ""')
@commands.has_any_role("Staff)")
async def echodm(ctx, member: discord.Member, message):
	await member.send(message)
	time.sleep(0.1)
	await ctx.send("Message sent")

@bot.command(name='echoin', aliases=['ein'], help='Echos typed phrase in the defined channel. Message must be in ""')
@commands.has_any_role("Staff")
async def echoin(ctx, channel, message):
	no_pound = int(channel[2:-1])
	channel = bot.get_channel(no_pound)
	await channel.send(message)
	
@bot.command(name='setecho',aliases=['sete'], help='Sets echo location for echoto.')
@commands.has_any_role("Staff")
async def setecho(ctx, channel):
	global echochannel
	no_pound = int(channel[2:-1])
	channel = bot.get_channel(no_pound)
	echochannel = channel
	await ctx.send("Echoto channel set to "+echochannel.name)
	
@bot.command(name='echo', help='Sends echo to channel defined by setecho. Message must be in "".')
@commands.has_any_role('Staff')
async def echo(ctx,message):
    channel = echochannel
    if echochannel == None:
        await ctx.send("No echo channel designated. Please use '$setecho' command to choose echo channel.")
    else:
        await channel.send(message)

@bot.command(name='help',help="Run this command to get started.")
async def help(ctx):

    author_nickname = await get_nick(ctx.author)
    help_img = 'https://cdn.discordapp.com/attachments/700480001312686170/762470650526564362/AZpFeJ3IBdyUAAAAAElFTkSuQmCC.png'


    embed = discord.Embed(title = "How to use the Goblin Economy Bot", description = "a list of commands and how to use them", color = discord.Color(0x75EE10))
    embed.add_field(name = "$give", value = "Command format: \n`$give # @person`\nGives the mentioned (@)user the defined number(#) of gobdollars. If you have that many.", inline=False)
    embed.add_field(name = "$inquiry", value = 'Command format: \n`$inquiry "This is my question in quotation marks!"`\nAsks a question to the Goblin Economy Bot. Please allow 1-5 minutes for response.', inline=False)
    embed.add_field(name = "$checkbalance, $cbal", value = "Command format: \n`$cbal @user`\nTells you the mentioned (@)user's current balance.", inline=False)
    embed.add_field(name = "$help", value = 'Displays this message.', inline = False)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {author_nickname}")
    embed.set_thumbnail(url = help_img)

#This version deletes itself after 60 seconds. If you don't want that then remove the , delete_after=60 in the ctx.send below. You can also change how long it stays in seconds by changing the 60.
    await ctx.send(embed=embed,delete_after=30)
#    await ctx.author.send(embed=embed) #You can uncomment this if you want the bot to also DM the user a copy of the embed.
    await ctx.message.delete() #This deletes the $help message that the user sent to call this command, you can also remove this if ypu wish.

bot.run(TOKEN)