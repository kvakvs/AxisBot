import discord

from libaxis import quote as quote_module
from libaxis.conf import delete_after


async def learn_quote(interaction: discord.Interaction, key: str, text: str):
    qte = quote_module.get_quote(key=key)
    if qte is not None and qte.player_id != interaction.user.id:
        await interaction.response.send_message(
            f":no_entry: Sorry, I already know that quote. And it is not yours. Use `/quote {key}` to post it.",
            delete_after=delete_after,
            ephemeral=True)
        return

    quote_module.learn_quote(player_id=interaction.user.id, quote_key=key, quote_text=text)
    await interaction.response.send_message(
        f"Learned a quote. Post using `/quote {key}`. Forget using `/forget {key}`",
        delete_after=delete_after,
        ephemeral=True)


async def post_quote(interaction: discord.Interaction, key: str):
    qte = quote_module.get_quote(key)
    if qte is None:
        await interaction.response.send_message(
            f":no_entry: Sorry, I don't know that quote. Teach me using /learn {key} <text>",
            delete_after=delete_after,
            ephemeral=True)
        return
    await interaction.channel.send(qte.format())
    await interaction.response.send_message("Quote posted",
                                            delete_after=1.0,
                                            ephemeral=True)


async def forget_quote(interaction: discord.Interaction, key: str):
    qte = quote_module.get_quote(key)
    if qte is None:
        await interaction.response.send_message(f":no_entry: Sorry, I don't know that quote.",
                                                delete_after=delete_after,
                                                ephemeral=True)
        return
    elif qte.player_id != interaction.user.id:
        await interaction.response.send_message(f":no_entry: I know that quote but its not yours!",
                                                delete_after=delete_after,
                                                ephemeral=True)
        return
    quote_module.forget_quote(player_id=interaction.user.id, quote_key=key)
    await interaction.response.send_message(f"Quote {key} has been forgotten",
                                            delete_after=delete_after,
                                            ephemeral=True)


def code_quote(key: str):
    return f"`{key}`"


async def print_quote_keys(interaction: discord.Interaction):
    my_keys = quote_module.get_user_quote_keys(player_id=interaction.user.id)
    my_quotes = ", ".join(map(code_quote, my_keys))

    other_keys = quote_module.get_other_users_quote_keys(player_id=interaction.user.id)
    other_quotes = ", ".join(map(code_quote, other_keys))

    await interaction.response.send_message(
        f"Quotes you taught me (you can use, modify or forget those): {my_quotes}\n"
        f"Other people's quotes (you can use those): {other_quotes}",
        delete_after=delete_after * 4,
        ephemeral=True)
