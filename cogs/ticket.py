import traceback

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import (
    ActionRow,
    Button,
    Container,
    LayoutView,
    MediaGallery,
    Modal,
    Separator,
    TextDisplay,
    TextInput,
)
from discord.utils import get

from handlers._data import DataManager


class TicketManager:
    def __init__(self):
        self.data_manager = DataManager()
        self.config = self.data_manager.get_data_dir() / "ticket_config.json"

    def get_config(self):
        return self.data_manager.read_file(self.config)

    def save_config(self, data):
        return self.data_manager.save_file(self.config, data)

    def get_log_channel(self):
        config = self.get_config()
        channel = config["log_channel"]
        return channel if channel else "None"

    async def create_ticket(self, user: discord.Member):
        try:
            guild = user.guild
            ticket_name = f"{user.name}×ticket"

            get_ticket = get(guild.text_channels, name=ticket_name)
            print(get_ticket)

            if get_ticket:
                return "error", "a ticket already exist"

            ticket_channel = await guild.create_text_channel(name=ticket_name)

            permissions = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(
                    view_channel=True, send_messages=True, read_messages=True
                ),
            }
            await ticket_channel.edit(overwrites=permissions)

            return "success", ticket_channel
        except Exception as e:
            return "error", str(e)

    async def delete_ticket(self, channel: discord.TextChannel):
        try:
            ticket = get(channel.guild.text_channels, id=channel.id)
            channel_msgs = [
                messages
                async for messages in ticket.history(limit=None, oldest_first=True)
            ]
            if ticket:
                msg = await ticket.send("## Saving Transcript")
                with open(f"{ticket.name}.txt", "w") as transcript:
                    for message in channel_msgs:
                        transcript.write(f"{message.author.name} : {message.content}\n")
                        transcript.writelines(
                            f"Attachment : {attachment.url}\n"
                            for attachment in message.attachments
                        )

                await msg.edit(content="## Saved Transcript. Sending to log channel")
                log_channel = channel.guild.get_channel(self.get_log_channel())
                await log_channel.send(
                    content=f"Transcript of ticket : {ticket.name}",
                    file=discord.File(f"{ticket.name}.txt"),
                )

                await msg.edit(content="## Deleting Channel")
                await ticket.delete()
                return "success", "ticket successfully deleted"
        except Exception as e:
            return "error", str(e)


class DeleteTicketButton(Button):
    def __init__(self):
        super().__init__(
            label="Delete Ticket",
            style=discord.ButtonStyle.danger,
            custom_id="ticket:close",
        )
        self.ticket_manager = TicketManager()

    async def callback(self, interaction: discord.Interaction):
        try:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "You don't have administrator permission", ephemeral=True
                )
                return
            status, result = await self.ticket_manager.delete_ticket(
                interaction.channel
            )
            if status == "error":
                await interaction.response.send_message(result)

            await interaction.response.send_message(result, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            traceback.print_exc()


class CreateTicketModal(Modal):
    def __init__(self):
        super().__init__(title="Create Ticket", custom_id="ticket:modal")
        self.ticket_manager = TicketManager()

        self.topic = TextInput(
            label="Topic", placeholder="Enter your topic name", required=True
        )
        self.reason = TextInput(
            label="Reason", placeholder="Enter your reason", required=True
        )

        self.add_item(self.topic)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            status, result = await self.ticket_manager.create_ticket(interaction.user)
            if status == "error":
                await interaction.response.send_message(str(result), ephemeral=True)
            created_embed = discord.Embed(
                title="Ticket Created",
                description=f"**Ticket Name**: {result.name}\n**Ticket Mention**: {result.mention}\n**Ticket Channel Id**: `{result.id}`",
                color=0x00FFFF,
            )
            ticket_view = LayoutView()
            container = Container()
            sep = Separator()
            button_row = ActionRow()
            title = TextDisplay(f"### {interaction.user.mention} Welcome")
            reason = TextDisplay(
                f"> **Topic Name** : {self.topic.value}\n> **Reason** : ```{self.reason.value}```\n\n> <@&1539651469014335604> Assist them"
            )
            button_row.add_item(DeleteTicketButton())
            container.add_item(title)
            container.add_item(sep)
            container.add_item(reason)
            container.add_item(sep)
            container.add_item(button_row)
            container.accent_color = 0x00FFFF
            ticket_view.add_item(container)
            await result.send(view=ticket_view)
            await interaction.response.send_message(embed=created_embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            traceback.print_exc()


class CreateTicketButton(Button):
    def __init__(self):
        super().__init__(
            label="Create Ticket",
            style=discord.ButtonStyle.primary,
            emoji="<:tickets:1546595601679126528>",
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_modal(CreateTicketModal())
        except Exception as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            traceback.print_exc()


class TicketBox(LayoutView):
    def __init__(self):
        self.ticket_manager = TicketManager()
        super().__init__(timeout=None)
        self._build_box()

    def _build_box(self):
        container = Container()
        sep = Separator()
        cardinals_text = MediaGallery(
            discord.MediaGalleryItem(
                "https://cdn.discordapp.com/attachments/1539651471383986287/1547183017670475846/file_00000000067481fa99a0d01ba3ba92b5.png?ex=6aa27df8&is=6aa12c78&hm=dcac19d134ad8a38ada49de1c47975f1a925e8f07b0fb57466e723bc0a758d4c&"
            )
        )

        container.add_item(cardinals_text)
        container.add_item(sep)
        title = TextDisplay("## Support Panel")
        container.add_item(title)
        container.add_item(sep)
        rules = TextDisplay("""
        > Use <#1539651470713159734> for smaller complaints.
        > Do not open for fun or any kind of misuse.
        > Open only for emergency and private reports.
        > Do not ping anyone unnecessarily.
        """)
        container.add_item(rules)
        container.add_item(sep)
        button_row = ActionRow()
        button_row.add_item(CreateTicketButton())
        container.add_item(button_row)

        container.accent_color = 0x00FFFF
        self.add_item(container)


class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_manager = TicketManager()

    def cog_load(self):
        self.bot.add_view(TicketBox())

    ticket_group = app_commands.Group(name="ticket", description="Ticket Group")

    @ticket_group.command(name="panel", description="Send ticket panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Sent panel", ephemeral=True)
            await interaction.channel.send(view=TicketBox())
        except Exception as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            traceback.print_exc()

    @ticket_group.command(name="set_log_channel", description="Set ticket log channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_log_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        try:
            config = self.ticket_manager.get_config()
            config["log_channel"] = channel.id
            self.ticket_manager.save_config(config)
            await interaction.response.send_message(
                f"Log channel set to : {channel.mention}"
            )
        except Exception as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            traceback.print_exc()


async def setup(bot):
    await bot.add_cog(TicketCog(bot))
