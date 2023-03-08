# !/bin/env python

import logging
from typing import Optional

import discord

import libaxis.outcome
from libaxis.bot_client import MyClient
from libaxis import players, events, event_ui
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


@client.tree.command()
@discord.app_commands.describe(
    who='The player who is depositing or withdrawing gold',
    gold='How much gold has been deposited (negative value for withdraw)',
)
async def wallet(interaction: discord.Interaction, who: discord.Member, gold: Optional[int]):
    """ (Admin only) Player has deposited (positive) or withdrew (negative) gold.
    """
    players.ensure_exists(who.id, str(who), who.display_name)
    role_name = guild_conf['manager_role']
    role = discord.utils.find(lambda r: r.name == role_name, interaction.guild.roles)

    if gold is not None:
        if role not in interaction.user.roles:
            await interaction.response.send_message(
                f':no_entry: Must have {role_name} role to modify the wallets', ephemeral=True)
            return

        players.add_balance(who.id, gold)
        balance = players.get_balance(who.id)
        display_name = players.get_display_name(who.id)
        await interaction.response.send_message(
            f'The gold ({gold}) has been deposited for the player {display_name} ({who}), "'
            f'"balance is now {balance}', ephemeral=True)
    else:
        balance = players.get_balance(who.id)
        await interaction.response.send_message(
            f'The player {who} has balance of {balance}', ephemeral=True)


@client.tree.command()
# @discord.app_commands.describe()
async def bid(interaction: discord.Interaction):
    """ Any participant can bid on the latest event
    """
    event_id = events.find_latest_event()
    if event_id is None:
        await interaction.response.send_message(f':no_entry: No event exists, can''t bid just yet', ephemeral=True)
        return

    # post buttons view
    view = event_ui.EventView(event_id=event_id)

    for outcome in libaxis.outcome.get_outcomes(event_id=event_id):
        # emoji = discord.PartialEmoji(name=outcome.get_first_word())
        bet_amount = guild_conf['bet_amount']
        b = event_ui.OutcomeButton(
            client=client,
            event_id=event_id,
            outcome_id=outcome.outcome_id,
            gold=bet_amount,
            outcome_name=outcome.name,
            style=discord.ButtonStyle.grey,
            label=f"+{bet_amount} {outcome.cut_first_word()}",
            custom_id=f"outcome_id={outcome.outcome_id}")
        view.add_item(b)

    # view.message = await interaction.user.send(view=view)  # save sent message for update on timeout
    view.message = await interaction.response.send_message(ephemeral=True, view=view)


@client.tree.command()
@discord.app_commands.describe(
    name='The title for the event',
)
async def ulduar(interaction: discord.Interaction, name: str):
    """ (Admin only) Creates an Ulduar gambo event
    """
    role_name = guild_conf['manager_role']
    role = discord.utils.find(lambda r: r.name == role_name, interaction.guild.roles)

    if role not in interaction.user.roles:
        await interaction.response.send_message(
            f':no_entry: Must have {role_name} role to create events',
            ephemeral=True)
        return

    # create event
    logger.info(f'Creating event "{name}" for {interaction.user.display_name} in channel {interaction.channel_id}')
    event_id, embed = events.add_ulduar_event(author=interaction.user.display_name, name=name,
                                              channel=interaction.channel_id)

    # post embed
    embed_update = await interaction.channel.send(embed=embed)
    events.update_event_embed_id(event_id=event_id, embed_id=embed_update.id)

    await interaction.response.send_message(
        f'Event "{name}" has been created, use /bid to show the bidding buttons',
        ephemeral=True)
    # return bid(interaction)


@client.tree.command()
async def bump(interaction: discord.Interaction):
    """
    Repost the latest event again and delete it high up in the channel
    """
    event_id = events.find_latest_event()
    if event_id is None:
        await interaction.response.send_message(f':no_entry: No event exists, can''t bump just yet', ephemeral=True)
        return

    await events.bump_event(event_id=event_id, client=client)
    await interaction.response.send_message(f'Event reposted and refreshed, old message is deleted', ephemeral=True)


# # The rename decorator allows us to change the display of the parameter on Discord.
# # In this example, even though we use `text_to_send` in the code, the client will use `text` instead.
# # Note that other decorators will still refer to it as `text_to_send` in the code.
# @client.tree.command()
# @discord.app_commands.rename(text_to_send='text')
# @discord.app_commands.describe(text_to_send='Text to send in the current channel')
# async def send(interaction: discord.Interaction, text_to_send: str):
#     """Sends the text into the current channel."""
#     await interaction.response.send_message(text_to_send)


# # To make an argument optional, you can either give it a supported default argument
# # or you can mark it as Optional from the typing standard library. This example does both.
# @client.tree.command()
# @discord.app_commands.describe(
#     member='The member you want to get the joined date from; defaults to the user who uses the command')
# async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
#     """Says when a member joined."""
#     # If no member is explicitly provided then we use the command user here
#     member = member or interaction.user
#
#     # The format_dt function formats the date time into a human readable representation in the official client
#     await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


# A Context Menu command is an app command that can be run on a member or on a message by
# accessing a menu within the client, usually via right clicking.
# It always takes an interaction as its first parameter and a Member or Message as its second parameter.

# # This context menu command only works on members
# @client.tree.context_menu(name='Show Join Date')
# async def show_join_date(interaction: discord.Interaction, member: discord.Member):
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
