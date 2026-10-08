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

from discord.ui import (
    LayoutView, 
    Button, 
    TextDisplay, 
    Container, 
    Separator
    )

class GuideBox(LayoutView):
    def __init__(self):
        super().__init__(timeout=None)
        self._build_box()
        
    def _build_box(self):
        container = Container()
        title_text = discord.ui.Section('## Registration Guide', accessory=discord.ui.Thumbnail(_guild.icon.url))
        container.add_item(title_text)
        container.add_item(Separator())
        guide_text = TextDisplay('> **Press `Tutorial` Button To Watch How To Register**')
        container.add_item(guide_text)
        button_row = discord.ui.ActionRow()
        
        url_button = Button(label='Tutorial', style=discord.ButtonStyle.primary, url='https://drive.google.com/file/d/1y3O17aidLobI3a4tO2hLVCfKU7YhDKOS/view?usp=sharing')
        button_row.add_item(url_button)
        container.add_item(button_row)
        container.accent_color = 0x00FFFF
        self.add_item(container)


class RegistrationGuide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.command(name='rg', description='Registration Guide')
    @commands.has_permissions(administrator=True)
    async def rg(self, ctx):
        await ctx.send(view=GuideBox())
        
        
async def setup(bot):
    await bot.add_cog(RegistrationGuide(bot))