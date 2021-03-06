import discord
import asyncio
from typing import Union, List

from discord import message
from ...logging import convert_logging
import easy_embed as ezembed

from discord import abc
from discord.interactions import Interaction
from discord.utils import MISSING
from discord.commands import ApplicationContext
from discord.ext.commands import Context

log = convert_logging.get_logging()


class Paginator(discord.ui.View):
    def __init__(
        self,
        pages: Union[List[str], List[discord.Embed]],
        author_check=True,
    ):
        super().__init__()
        self.pages = pages
        self.current_page = 1
        self.page_count = len(self.pages)
        self.go_first = self.children[0]
        self.previous_button = self.children[1]
        self.forward_button = self.children[2]
        self.go_last = self.children[3]
        self.end = self.children[4]
        self.user_check = author_check
        self.user = None

        log.debug(
            f"Created Paginator with {self.pages} pages and author_check={self.user_check}"
        )

    async def interaction_check(self, interaction: Interaction) -> bool:
        if self.user_check:
            return self.user == interaction.user
        return True

    @discord.ui.button(label="⭅", style=discord.ButtonStyle.primary, disabled=True)
    async def go_to_start(
        self, button: discord.ui.Button, interaction: discord.Interaction, disabled=True
    ):
        log.debug(
            f'"Go First" button clicked for {interaction} by {interaction.user.display_name} in channel {interaction.channel.name} in guild {interaction.guild.name}'
        )
        self.current_page = 1

        log.debug(f"Disabling Previous Button")
        self.previous_button.disabled = True
        log.debug(f"Disabling Go To Start Button")
        button.disabled = True

        self.children[2].disabled = False
        self.children[3].disabled = False

        page = self.pages[self.current_page - 1]
        await interaction.response.edit_message(
            content=page if isinstance(page, str) else None,
            embed=page if isinstance(page, discord.Embed) else MISSING,
            view=self,
        )

    @discord.ui.button(label="⟸", style=discord.ButtonStyle.primary, disabled=True)
    async def previous(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        log.debug(
            f'"Go Previous" button clicked for {interaction} by {interaction.user.display_name} in channel {interaction.channel.name} in guild {interaction.guild.name}'
        )
        self.current_page -= 1

        if self.current_page == 1:
            log.debug(f"Current Page is 1 disabling previous button and gofirst button")
            self.go_first.disabled = True
            button.disabled = True

        self.children[2].disabled = False
        self.children[3].disabled = False

        page = self.pages[self.current_page - 1]
        await interaction.response.edit_message(
            content=page if isinstance(page, str) else None,
            embed=page if isinstance(page, discord.Embed) else MISSING,
            view=self,
        )

    @discord.ui.button(label="⟹", style=discord.ButtonStyle.primary)
    async def forward(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        log.debug(
            f'"Go Forward" button clicked for {interaction} by {interaction.user.display_name} in channel {interaction.channel.name} in guild {interaction.guild.name}'
        )
        self.current_page += 1

        if self.current_page == self.page_count:
            log.debug(f"Current Page is Last Page, Disabling Button and GoLast Button")
            self.go_last.disabled = True
            button.disabled = True

        self.children[1].disabled = False
        self.children[0].disabled = False

        page = self.pages[self.current_page - 1]
        await interaction.response.edit_message(
            content=page if isinstance(page, str) else None,
            embed=page if isinstance(page, discord.Embed) else MISSING,
            view=self,
        )

    @discord.ui.button(label="⭆", style=discord.ButtonStyle.primary)
    async def go_to_end(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        log.debug(
            f'"Go Last" button clicked for {interaction} by {interaction.user.display_name} in channel {interaction.channel.name} in guild {interaction.guild.name}'
        )
        self.current_page = len(self.pages)

        log.debug(f"Disabling Forward Button")
        self.forward_button.disabled = True
        log.debug(f"Disabling Go Last Button")
        button.disabled = True

        self.children[1].disabled = False
        self.children[0].disabled = False

        page = self.pages[self.current_page - 1]
        await interaction.response.edit_message(
            content=page if isinstance(page, str) else None,
            embed=page if isinstance(page, discord.Embed) else MISSING,
            view=self,
        )

    @discord.ui.button(label="⤫", style=discord.ButtonStyle.red)
    async def kill_switch(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        log.debug(
            f"Kill Switch Received for {interaction} by {interaction.user.display_name} in channel {interaction.channel.name} in guild {interaction.guild.name}"
        )

        log.debug(f"Disabling all Buttons")
        self.go_first.disabled = True
        self.previous_button.disabled = True
        self.forward_button.disabled = True
        self.go_last.disabled = True
        self.end.disabled = True
        log.debug(f"Disabled all Buttons, Removing")

        self.remove_item(self.go_first)
        self.remove_item(self.previous_button)
        self.remove_item(self.forward_button)
        self.remove_item(self.go_last)
        self.remove_item(self.end)
        log.debug(f"Removed all buttons")

        # page = self.pages[self.current_page - 1]
        page = ezembed.create_embed(
            title=f"**This Interaction has Ended**", color=discord.Colour.red()
        )
        await interaction.response.edit_message(
            content=page if isinstance(page, str) else None,
            embed=page if isinstance(page, discord.Embed) else MISSING,
            view=self,
        )

    async def run(self, messageable: abc.Messageable, ephemeral: bool = False):
        log.debug(f"Running Paginator")
        if not isinstance(messageable, abc.Messageable):
            log.error(f"{messageable} is not abc.Messageable")
            raise TypeError("messageable should be a subclass of abc.Messageable")

        page = self.pages[0]

        if isinstance(messageable, (ApplicationContext, Context)):
            self.user = messageable.author

        if isinstance(messageable, ApplicationContext):
            message = await messageable.respond(
                content=page if isinstance(page, str) else None,
                embed=page if isinstance(page, discord.Embed) else MISSING,
                view=self,
            )
        else:
            message = await messageable.send(
                content=page if isinstance(page, str) else None,
                embed=page if isinstance(page, discord.Embed) else MISSING,
                view=self,
            )
        return message

    def next_button(self, label: str, color: str = "primary"):
        log.debug(f"Changing Forward Button Label to {label} and color to {color}")
        self.forward_button.label = label
        color = getattr(discord.ButtonStyle, color.lower())
        self.forward_button.style = color

    def back_button(self, label: str, color: str = "primary"):
        log.debug(f"Changing Back Button Label to {label} and color to {color}")
        self.previous_button.label = label
        color = getattr(discord.ButtonStyle, color.lower())
        self.previous_button.style = color

    def first_button(self, label: str, color: str = "primary"):
        log.debug(f"Changing First Button Label to {label} and color to {color}")
        self.go_first.label = label
        self.go_first.style = getattr(discord.ButtonStyle, color.lower())

    def last_button(self, label: str, color: str = "primary"):
        log.debug(f"Changing Last Button Label to {label} and color to {color}")
        self.go_last.label = label
        self.go_last.style = getattr(discord.ButtonStyle, color.lower())
