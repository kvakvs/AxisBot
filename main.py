# !/bin/env python

import logging
from typing import Optional

import discord

from libaxis.bot_client import MyClient
from libaxis.commands import quote_commands, event_commands, crafting_commands
from libaxis.conf import conf, bot_conf, guild_conf

logger = None


def init_logging():
    logging.basicConfig(filename="axisbot.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

    global logger
    logger = logging.getLogger('main')
    logger.info("Running Axis Bot")


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


@client.tree.command(description="[Manager role only] Add or remove gold from the gambling wallet.")
@discord.app_commands.describe(
    who='Player''s discord name',
    gold='How much gold to add or remove (negative value for withdraw)',
)
async def wallet(interaction: discord.Interaction, who: discord.Member, gold: Optional[int]):
    await event_commands.modify_or_show_wallet(interaction=interaction, who=who, gold=gold)


@client.tree.command(description="Show buttons to place your bet on the latest event")
async def bet(interaction: discord.Interaction):
    await event_commands.place_bet(interaction=interaction)


@client.tree.command(
    description="[Event Manager role only] Post a new Ulduar raid event. Makes previous event inaccessible.")
@discord.app_commands.describe(
    name='The title for the event',
)
async def ulduar(interaction: discord.Interaction, name: str):
    await event_commands.post_ulduar_event(interaction=interaction, name=name)


@client.tree.command(
    description="[Event Manager role only] Toggles matching outcomes in the latest event, by a substring.")
async def outcome(interaction: discord.Interaction, search_str: str):
    await event_commands.toggle_outcomes(interaction=interaction, search_str=search_str)


@client.tree.command(description="[Manager role only] Repost the latest event, and delete the old message.")
async def bump(interaction: discord.Interaction):
    await event_commands.bump_event(interaction=interaction)


@client.tree.command(description="[Event manager role only] Lock the event by id, or latest event.")
async def lock_event(interaction: discord.Interaction, event_id: Optional[int]):
    await event_commands.lock_event(interaction=interaction, event_id=event_id)


# ===============================================================================
# Craftables, crafting
# ===============================================================================

@client.tree.command(description="Teach the bot that or someone else can create an item")
async def learn_craft(interaction: discord.Interaction, item_id: int, who: Optional[discord.Member]):
    await crafting_commands.learn_craft(interaction=interaction, who=who, item_id=item_id)


@client.tree.command(description="Teach the bot that you or someone else can no longer create an item")
async def forget_craft(interaction: discord.Interaction, item_id: int, who: Optional[discord.Member]):
    await crafting_commands.forget_craft(interaction=interaction, who=who, item_id=item_id)


@client.tree.command(description="Search for any craftable item, can search item descriptions and reagents too")
async def craft(interaction: discord.Interaction, text: str):
    await crafting_commands.find_crafts(interaction=interaction, text=text, subclass=None)


@client.tree.command(description="Search for a Jewelcrafting design, can search item descriptions and reagents too")
async def jc(interaction: discord.Interaction, text: str):
    await crafting_commands.find_crafts(interaction=interaction, text=text, subclass="Jewelcrafting Designs")


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


init_logging()
client.run(bot_conf['token'])
