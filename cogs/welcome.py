import discord
from discord.ext import commands
from discord.ui import (
    LayoutView,
    Button,
    Container,
    TextDisplay,
    Section,
    Separator,
    Thumbnail,
    ActionRow,
    MediaGallery
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
                    "https://cdn.discordapp.com/attachments/1017630659885420554/1540413350893195274/file_000000003b6c8211a11ece1e3be103e2.png?ex=6a89dd3a&is=6a888bba&hm=c0da9f5283bab44851268e6c038da34cf35f3f0987a17140c7a7b2ae875de98b&"
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
            channel = member.guild.get_channel(1539651470327156911)
            layout = WelcomeLayout(member)
            await channel.send(view=layout)
        except Exception as e:
            print(f"ERROR while welcoming {member.name}: {type(e).__name__}:  {e}")
            pass
            

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
