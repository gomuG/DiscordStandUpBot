import os

from discord.ext import tasks, commands
import discord
from dotenv import load_dotenv
from datetime import datetime, time, timedelta, date
import asyncio
import random
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
TEAM = os.getenv('DISCORD_TEAM', 'Nobody')
USER = os.getenv('DISCORD_USER')
FILTER_MESSAGE = os.getenv('FILTER_MESSAGE')
CHANNELS = os.getenv('DISCORD_CHANNELS')

channels_json = json.loads(CHANNELS)

description = 'A simple bot to serve a simple purpose for now.'
activity = discord.Activity(type=discord.ActivityType.watching, name=f'over {TEAM}')
monitored_guild = None

intents = discord.Intents.all()
client = commands.Bot(command_prefix='?', description=description, intents=intents, activity=activity)

WHEN = time(3, 50, 0)


@client.event
async def on_ready():
    print(f'{client.user} is connected to the following guild:\n')

    guilds = client.guilds
    guilds_list = '\n - '.join([guild.name for guild in guilds])
    print(f'Part of the following Guilds:\n - {guilds_list}')

    for guild in guilds:
        if guild.id == int(GUILD):
            global monitored_guild
            monitored_guild = guild

        print(f'{guild.name}(id: {guild.id})')
        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')

    print(monitored_guild)


def check_channel(channel_id):
    try:
        channels_json[channel_id]
        return True
    except KeyError:
        return False


def shuffle_members(channel):
    members = []
    for member in channel.members:
        if not member.bot: # Ignore bots in voice channels
            members.append(member.mention)

    random.shuffle(members)
    return members


@client.command(description='Generate a shuffled list of members')
async def shuffle(ctx, channel: str):
    se_channel = discord.utils.get(client.get_all_channels(), guild__name=ctx.guild.name, name=channel)
    print(se_channel)
    if se_channel is None:
        await ctx.send("Hey, I dont think such a channel exist...")
    elif not se_channel.members:
        await ctx.send("Hey, there isnt anyone here for me to shuffle!")
    else:
        members = shuffle_members(se_channel)
        msg_members_mention_list = '\n '.join([f'{i}) {member}' for i, member in enumerate(members, start=1)])
        await ctx.send(f"Today's Stand Up Order:\n {msg_members_mention_list}")


# @client.command(description='set daily reminders')
# async def notification(ctx):
#     client.loop.create_task(my_background_task(ctx))
#     await my_background_task.start(ctx)


# @tasks.loop(seconds=60)
# async def my_background_task(ctx):
#     print('hello world running task')
#     print(ctx.guild.name)
#     guild = discord.utils.get(client.guilds, name=GUILD)
#     # channel = guild.channels[0].channels[1]
#     await ctx.send(ctx.message.content)


# @my_background_task.before_loop
# async def before_my_task():
#     await client.wait_until_ready()
#
#     now = datetime.now()
#     target_time = datetime.combine(now.date(), WHEN)
#     seconds_till_target = (target_time - now).total_seconds()
#     print("counting down %s" % seconds_till_target)
#     await asyncio.sleep(seconds_till_target)


async def carl_bot_message_filter(message):
    if message.guild == monitored_guild and message.author.name == USER and check_channel(str(message.channel.id)):
        if FILTER_MESSAGE in message.content:
            if message.role_mentions:
                mention = ' ' + message.role_mentions[0].mention + '!'
            elif not message.role_mentions:
                mention = '!'
            countdown = channels_json[str(message.channel.id)]['shuffle_countdown']
            await message.channel.send(f'Thank you {message.author.mention} for the reminder!'
                                       f' Gather up{mention} '
                                       f"I will start shuffling in {countdown} seconds!")

            await asyncio.sleep(countdown)
            voice_channel = discord.utils.get(
                message.guild.channels,
                id=channels_json[str(message.channel.id)]['voice_id']
            )
            members = shuffle_members(voice_channel)

            if members:
                msg_members_mention_list = '\n '.join([f'{i}) {member}' for i, member in enumerate(members, start=1)])
                await message.channel.send(f"Today's date is {date.today().strftime('%B %d, %Y')}!\n Stand Up Order:\n {msg_members_mention_list}")
            elif not members:
                await message.channel.send("Hey, there is no one here!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await carl_bot_message_filter(message)

    print(message.content)
    await client.process_commands(message)

client.run(TOKEN)
