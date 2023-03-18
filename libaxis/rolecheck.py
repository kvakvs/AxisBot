import discord

from libaxis.conf import guild_conf


def missing_required_manager_role(interaction: discord.Interaction):
    role_name = guild_conf['manager_role']
    role = discord.utils.find(lambda r: r.name == role_name, interaction.guild.roles)

    return role not in interaction.user.roles


def missing_required_event_manager_role(interaction: discord.Interaction):
    role_name = guild_conf['event_manager_role']
    role = discord.utils.find(lambda r: r.name == role_name, interaction.guild.roles)

    return role not in interaction.user.roles
