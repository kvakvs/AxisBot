from typing import Optional

import discord

from libaxis import crafting, players
from libaxis.conf import guild_conf, delete_after
from libaxis.rolecheck import missing_required_manager_role


async def learn_craft(interaction: discord.Interaction, who: Optional[discord.Member], item_id: int):
    if who is not None and missing_required_manager_role(interaction):
        await interaction.response.send_message(
            f':no_entry: Must have {guild_conf["manager_role"]} role to learn the crafting for someone else',
            delete_after=delete_after,
            ephemeral=True)
        return

    member = who if who is not None else interaction.user

    # Update the player cache
    players.ensure_exists(member.id, str(member), member.display_name)

    item_info = crafting.learn_craft(member.id, item_id)
    if item_info is None:
        await interaction.response.send_message(
            f"Failed to find crafting item id {item_id} on Wowhead or failed to parse the server response.",
            delete_after=delete_after,
            ephemeral=True)
        return

    await interaction.response.send_message(
        f"Learned a craftable item {item_info.item_name} from <{item_info.link}> for {member.display_name}",
        delete_after=delete_after,
        ephemeral=True)


async def forget_craft(interaction: discord.Interaction, who: Optional[discord.Member], item_id: int):
    if who is not None and missing_required_manager_role(interaction):
        await interaction.response.send_message(
            f':no_entry: Must have {guild_conf["manager_role"]} role to forget the crafting by someone else',
            delete_after=delete_after,
            ephemeral=True)
        return

    member = who if who is not None else interaction.user
    crafting.forget_craft(member.id, item_id)

    await interaction.response.send_message(
        f"Removed a craftable item {item_id} from {member.display_name}",
        delete_after=delete_after,
        ephemeral=True)


def create_crafts_embed(search_text: str, all_crafts: dict[int, list[crafting.Craftable]]) -> discord.Embed:
    embed = discord.Embed(title=f"Search results for: {search_text}",
                          # url="https://github.com/kvakvs/AxisBot/blob/master/README.md",
                          # description="Search results",
                          color=0xFF5733)

    limit = 0
    for item_id in all_crafts.keys():
        this_item_crafters = all_crafts[item_id]
        crafter_names = "; ".join([players.get_display_name(craft.player_id) for craft in this_item_crafters])
        first_item = this_item_crafters[0]
        embed.add_field(name=f"{crafter_names}",
                        value=f":scroll: [{first_item.item.item_name}]({first_item.item.link})",
                        inline=True)
        limit += 1
        if limit >= 25:
            embed.add_field(name="Results limited",
                            value="Showing only first 25 results",
                            inline=True)
            break
    # embed.set_footer(text=f"")

    return embed


async def find_crafts(interaction: discord.Interaction, text: str, subclass: Optional[str]):
    if len(text) < 3:
        await interaction.response.send_message(
            f"Search text is too short. Must be at least 3 characters",
            delete_after=delete_after,
            ephemeral=True)
        return

    craftable_dict = crafting.find_all_crafts(text, subclass)
    if not craftable_dict:
        if subclass is None:
            await interaction.response.send_message(
                f"Failed to find any crafting item matching {text} in all categories",
                delete_after=delete_after,
                ephemeral=True)
        else:
            await interaction.response.send_message(
                f"Failed to find any crafting item matching {text} in category {subclass}",
                delete_after=delete_after,
                ephemeral=True)
        return

    embed = create_crafts_embed(search_text=text, all_crafts=craftable_dict)
    await interaction.response.send_message(
        embed=embed,
        delete_after=delete_after * 4,
        ephemeral=True)
