import discord
from discord.ext import commands
from discord.ui import (
    Container,
    LayoutView,
    MediaGallery,
    Section,
    Separator,
    TextDisplay,
    Thumbnail,
)


class WelcomeLayout(LayoutView):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=180)
        self._build_container(member)

    def _build_container(self, member: discord.Member):
        sep = Separator(visible=True)
        server_name = TextDisplay("### 𝚆𝚎𝚕𝚌𝚘𝚖𝚎 𝚝𝚘 𝚃𝚑𝚎 𝙲𝚊𝚛𝚍𝚒𝚗𝚊𝚕")
        user_name = TextDisplay(
            f"**Name** : `{member.name}`\n**Mention** : {member.mention}\n**ID** : `{member.id}`"
        )
        user_icon = Thumbnail(
            member.avatar.url if member.avatar else member.default_avatar.url
        )
        user_section = Section(user_name, accessory=user_icon)
        welcome_banner = MediaGallery(
            discord.MediaGalleryItem(
                "https://cdn.discordapp.com/attachments/1539651471383986287/1547629694424186880/file_000000009f9081f5bec030ed95de7a14.png?ex=6aa41df8&is=6aa2cc78&hm=845307f74aa463ffc8c89904ad203cc426e0720d5e27acb35a4d7deb9f501f40&"
            )
        )
        container = Container(
            server_name,
            sep,
            user_section,
            sep,
            welcome_banner,
            accent_color=0x00FFFF,
        )
        self.add_item(container)


class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            channel = member.guild.get_channel(1540673634367176754)
            layout = WelcomeLayout(member)
            await channel.send(view=layout)
        except Exception as e:
            print(f"ERROR while welcoming {member.name}: {type(e).__name__}:  {e}")

    @commands.command(name="welcome_test", description="Test Welcome Message")
    async def welcome_test(self, ctx):
        print("Welcome Cog command called")

        try:
            layout = WelcomeLayout(ctx.author)
            print("Layout created")

            await ctx.send(view=layout)
            print("View sent")

        except Exception as e:
            print(f"ERROR: {type(e).__name__}:  {e}")
            await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")


async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
