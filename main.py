# !/bin/env python

import logging
from typing import Optional

import discord

import libaxis.outcome
from libaxis import quote
from libaxis.commands import quote_commands, event_commands
from libaxis.bot_client import MyClient
from libaxis.conf import conf, bot_conf, guild_conf

logging.basicConfig(filename="axisbot.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running Axis Bot")
logger = logging.getLogger('main')

intents = discord.Intents(messages=True, reactions=True, guilds=True)
# intents = discord.Intents(326417524800)
# intents.reactions.flag

print(f"Starting bot for guild {guild_conf['id']} ({guild_conf['name']})")
client = MyClient(conf=conf,
                  intents=intents,
                  guild=discord.Object(id=int(guild_conf['id'])),
                  application_id=int(bot_conf['application_id']))


@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user} (ID: {client.user.id})')


@client.tree.command(description="Add or remove gold from the gambling wallet, only officers can do this.")
@discord.app_commands.describe(
    who='The player who is depositing or withdrawing gold',
    gold='How much gold has been deposited (negative value for withdraw)',
)
async def wallet(interaction: discord.Interaction, who: discord.Member, gold: Optional[int]):
    await event_commands.modify_or_show_wallet(interaction=interaction, who=who, gold=gold)


@client.tree.command(description="Show buttons to bid on the latest event")
async def bid(interaction: discord.Interaction):
    await  event_commands.place_bid(client=client, interaction=interaction)


@client.tree.command(
    description="Post a new Ulduar raid event. Only officers can do this, this makes previous event inaccessible.")
@discord.app_commands.describe(
    name='The title for the event',
)
async def ulduar(interaction: discord.Interaction, name: str):
    await event_commands.post_ulduar_event(interaction=interaction, name=name)


@client.tree.command(description="Repost the latest event, and delete the old message. Only officers can do this.")
async def bump(interaction: discord.Interaction):
    await event_commands.bump_event(client=client, interaction=interaction)


# ===============================================================================
# Quotes management and posting
# ===============================================================================

@client.tree.command(description="Teach bot a new quote. Takes a short key and text.")
@discord.app_commands.describe(
    key='Quote key, a short word (no spaces)',
    text='The text to be stored',
)
async def learn(interaction: discord.Interaction, key: str, text: str):
    await quote_commands.learn_quote(interaction=interaction, key=key, text=text)


@client.tree.command(description="Insert a saved quote into the chat.")
@discord.app_commands.describe(
    key='Quote key, which was used when /learn-ing',
)
async def quote(interaction: discord.Interaction, key: str):
    await quote_commands.post_quote(interaction=interaction, key=key)


@client.tree.command(description="Forget a saved quote.")
@discord.app_commands.describe(
    key='Quote key, which was used when /learn-ing',
)
async def forget(interaction: discord.Interaction, key: str):
    await quote_commands.forget_quote(interaction=interaction, key=key)


@client.tree.command(description="Show ids of the quotes you have taught me.")
async def quotes(interaction: discord.Interaction):
    await quote_commands.print_quote_keys(interaction=interaction)


# A Context Menu command is an app command that can be run on a member or on a message by
# accessing a menu within the client, usually via right clicking.
# It always takes an interaction as its first parameter and a Member or Message as its second parameter.

# # This context menu command only works on members
# @client.tree.context_menu(name='Axis Gambling Wallet')
# async def wallet_menu(interaction: discord.Interaction, member: discord.Member):
#     # The format_dt function formats the date time into a human readable representation in the official client
#     await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')


# # This context menu command only works on messages
# @client.tree.context_menu(name='Report to Moderators')
# async def report_message(interaction: discord.Interaction, message: discord.Message):
#     # We're sending this response message with ephemeral=True, so only the command executor can see it
#     await interaction.response.send_message(
#         f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
#     )
#
#     # Handle report by sending it into a log channel
#     log_channel = interaction.guild.get_channel(0)  # replace with your channel id
#
#     embed = discord.Embed(title='Reported Message')
#     if message.content:
#         embed.description = message.content
#
#     embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
#     embed.timestamp = message.created_at
#
#     url_view = discord.ui.View()
#     url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))
#
#     await log_channel.send(embed=embed, view=url_view)


client.run(bot_conf['token'])
