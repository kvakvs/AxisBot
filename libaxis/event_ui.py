from typing import Optional, Union

import discord.ui
from discord import ButtonStyle, Emoji, PartialEmoji

from libaxis import events


class EventView(discord.ui.View):
    def __init__(self, *, event_id: int, timeout: Optional[float] = 60.0):
        super().__init__(timeout=timeout)
        self.event_id = event_id
        self.message = None

    async def on_timeout(self) -> None:
        # for item in self.children:
        #     item.disabled = True
        self.children.clear()  # empty the buttons frame
        await self.message.edit(view=self)


#     @discord.ui.button(label="Hello", style=discord.ButtonStyle.success)
#     async def hello(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.send_message("Hello!", ephemeral=True)


class OutcomeButton(discord.ui.Button):
    def __init__(self, *,
                 client: discord.Client,
                 event_id: int,
                 outcome_id: int,
                 gold: int,
                 outcome_name: str,
                 style: ButtonStyle = ButtonStyle.secondary, label: Optional[str] = None,
                 disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None,
                 emoji: Optional[Union[str, Emoji, PartialEmoji]] = None, row: Optional[int] = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji,
                         row=row)
        self.client = client
        self.event_id = event_id
        self.outcome_name = outcome_name
        self.outcome_id = outcome_id
        self.gold = gold

    async def callback(self, interaction: discord.Interaction):
        bet_attempt = events.bet_on_outcome(
                event_id=self.event_id,
                outcome_id=self.outcome_id,
                player_id=interaction.user.id,
                display_name=interaction.user.display_name,
                gold=self.gold)
        if bet_attempt is None:
            await interaction.response.send_message(
                f":white_check_mark: Your bet of {self.gold} on {self.outcome_name} was accepted",
                ephemeral=True)
            # Update the embed
            await events.update_event_embed(event_id=self.event_id, client=self.client)
        else:
            await interaction.response.send_message(
                f":no_entry: Your bet on {self.outcome_name} was not accepted: {bet_attempt}",
                ephemeral=True)
