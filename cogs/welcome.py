import discord
from discord.ext import commands
from discord.ui import LayoutView, Button, Container, MediaGallaryItem, TextDisplay, Section, Separator, Thumbnail

class WelcomeLayout(discord.ui.LayoutView):
    def __init__(self, member: discord.Member):
        self._build_container(member)
        
    def _build_container(self, member: discord.Member):
        
        sep = Separator(visible=True)
        server_name = TextDisplay("### 𝚃𝚑𝚎 𝙲𝚊𝚛𝚍𝚒𝚗𝚊𝚕")
        user_name = TextDisplay(f"**Name** : `{member.name}`\n**Mention** : {member.mention}\n**ID** : `{member.id}`")
        user_icon = Thumbnail(member.avatar.url if member.avatar else member.default_avatar.url)
        user_section = Section(user_name, accessory=user_icon)
        welcome_banner = MediaGallaryItem("https://cdn.discordapp.com/attachments/1017630659885420554/1540413350893195274/file_000000003b6c8211a11ece1e3be103e2.png?ex=6a89dd3a&is=6a888bba&hm=c0da9f5283bab44851268e6c038da34cf35f3f0987a17140c7a7b2ae875de98b&")
        welcome_btn = Button(label='Welcome',style=discord.ButtonStyle.secondary, emoji='<:cardinal:1540407908771307690>')
        welcome_btn.callback = welcome_btn_cb
        
        async def welcome_btn_cb(interaction: discord.Interaction):
            if interaction.user.id == member.id:
                await interaction.response.send_message("You cant welcome yourself dude", ephemepral=True)
                return
            await interaction.channel.send(f"`{interaction.user.name}` Welcomes `{member.name}`")
            
            
        container = Container(
            server_name,
            sep,
            user_section,
            sep,
            welcome_banner,
            welcome_btn,
            accent_color=0x00FFFF
            )
        self.add_item(container)
        
class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='welcome_test', description=f"Test Welcome Message")
    async def welcome_test(self, ctx):
        layout = WelcomeLayout(ctx.author)
        await ctx.send(view=layout)
        
async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))