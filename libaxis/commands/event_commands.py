import logging
from typing import Optional

import discord

import libaxis
from libaxis import players, events, event_ui
from libaxis.conf import guild_conf, delete_after

logger = logging.getLogger('commands')


def missing_required_officer_role(interaction: discord.Interaction):
    role_name = guild_conf['manager_role']
    role = discord.utils.find(lambda r: r.name == role_name, interaction.guild.roles)

    return role not in interaction.user.roles


async def modify_or_show_wallet(interaction: discord.Interaction, who: discord.Member, gold: Optional[int]):
    """ (Admin only) Player has deposited (positive) or withdrew (negative) gold.
    """
    players.ensure_exists(who.id, str(who), who.display_name)

    if gold is not None:
        if missing_required_officer_role(interaction):
            await interaction.response.send_message(
                f':no_entry: Must have {guild_conf["manager_role"]} role to modify the wallets',
                delete_after=delete_after,
                ephemeral=True)
            return

        players.add_balance(who.id, gold)
        balance = players.get_balance(who.id)
        display_name = players.get_display_name(who.id)
        await interaction.response.send_message(
            f'The gold ({gold}) has been deposited for the player {display_name} ({who}), "'
            f'"balance is now {balance}',
            delete_after=delete_after,
            ephemeral=True)

    balance = players.get_balance(who.id)
    await interaction.response.send_message(
        f'The player {who} has balance of {balance}',
        delete_after=delete_after,
        ephemeral=True)


async def place_bid(client: discord.Client, interaction: discord.Interaction):
    """ Any participant can bid on the latest event
    """
    event_id = events.find_latest_event()
    if event_id is None:
        await interaction.response.send_message(f':no_entry: No event exists, can''t bid just yet',
                                                delete_after=delete_after,
                                                ephemeral=True)
        return

    # post buttons view
    view = event_ui.EventView(event_id=event_id)

    available_outcomes = list(filter(lambda each_o: each_o.is_available(),
                                     libaxis.outcome.get_outcomes(event_id=event_id)))
    if len(available_outcomes) == 0:
        await interaction.response.send_message(f':no_entry: All outcomes for this event have been taken',
                                                delete_after=delete_after,
                                                ephemeral=True)
        return

    for outcome in available_outcomes:
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
    view.message = await interaction.response.send_message(
        view=view,
        delete_after=delete_after,
        ephemeral=True)


async def post_ulduar_event(interaction: discord.Interaction, name: str):
    """ (Admin only) Creates an Ulduar gambo event
    """
    if missing_required_officer_role(interaction):
        await interaction.response.send_message(
            f':no_entry: Must have {guild_conf["manager_role"]} role to create events',
            delete_after=delete_after,
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
        delete_after=delete_after,
        ephemeral=True)


async def bump_event(client: discord.Client, interaction: discord.Interaction):
    """
    Repost the latest event again and delete it high up in the channel
    """
    if missing_required_officer_role(interaction):
        await interaction.response.send_message(
            f':no_entry: Must have {guild_conf["manager_role"]} role to bump events',
            delete_after=delete_after,
            ephemeral=True)
        return

    event_id = events.find_latest_event()
    if event_id is None:
        await interaction.response.send_message(f':no_entry: No event exists, can''t bump just yet',
                                                delete_after=delete_after,
                                                ephemeral=True)
        return

    await events.bump_event(event_id=event_id, client=client)
    await interaction.response.send_message(f'Event reposted and refreshed, old message is deleted',
                                            delete_after=1.0,
                                            ephemeral=True)
