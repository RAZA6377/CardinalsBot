import discord
from discord.ext import commands
from discord import app_commands
from handlers._data import DataManager
from discord.ui import Button, LayoutView, Container, Section, Separator, TextDisplay
import traceback

class RoleManager:
    def __init__(self):
        self.data_manager = DataManager()
        self.role_file = self.data_manager.get_data_dir() / "role_data.json"
        
    def get_data(self):
        return self.data_manager.read_file(self.role_file)
        
    def save_data(self, data):
        return self.data_manager.save_file(self.role_file, data)
        
    def initiate_guild(self, guild: discord.Guild):
        try:
            data = self.get_data()
            if str(guild.id) in data:
                pass
            else:
                data[str(guild.id)] = {'roles': []}
                self.save_data(data)
        except:
            traceback.print_exc()
            pass 
        
    def get_guild_roles(self, guild: discord.Guild):
        self.initiate_guild(guild)
        data = self.get_data()
        return data[str(guild.id)]['roles']
        
    def add_role(self, guild: discord.Guild, role: discord.Role):
        data = self.get_data()
        guild_roles = self.get_guild_roles(guild)
        if role.id in guild_roles:
            return 'error', 'Role already exists'
        data[str(guild.id)]['roles'].append(role.id)
        self.save_data(data)
        return 'success', f'Added `{role.name}` To Button Role'
        
    def remove_role(self, guild: discord.Guild, role: discord.Role):
        data = self.get_data()
        guild_roles = self.get_guild_roles(guild)
        if role.id not in guild_roles:
            return 'error', 'Role doesn\'t exist'
        data[str(guild.id)]['roles'].remove(role.id)
        self.save_data(data)
        return 'success', f'Removed `{role.name}` From Button Role'
        
    async def manage_role(self, user: discord.Member, role: discord.Role):
        try:
            if role in user.roles:
                await user.remove_roles(role)
                return f'Successfully Removed {role.mention}'
            else:
                await user.add_roles(role)
                return f'Successfully Added {role.mention}'
        except Exception as e:
            return str(e)
            traceback.print_exc()
            
class RoleButton(Button):
    def __init__(self, role: discord.Role):
        self.role = role
        super().__init__(label=self.role.name, style=discord.ButtonStyle.secondary, custom_id=f'role:button:{self.role.id}')
        
    async def callback(self, interaction: discord.Interaction):
        try:
            result = await RoleManager().manage_role(interaction.user, self.role)
            layout = LayoutView()
            sep = Separator()
            result_status = TextDisplay(f'<a:tick:1546932427103150170> — Role Result')
            result_text = TextDisplay(result)
            result_footer = TextDisplay('`The Cardinals`')
            container = Container(
                result_status,
                sep,
                result_text,
                sep,
                result_footer,
                accent_color=0x00FFFF
                )
            layout.add_item(container)
        
            await interaction.response.send_message(view=layout, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            traceback.print_exc()
        
class RoleLayout(LayoutView):
    def __init__(self, guild: discord.Guild):
        self.role_manager = RoleManager()
        self.guild = guild
        super().__init__(timeout=None)
        self._create_panel()
        
    def _create_panel(self):
        data = self.role_manager.get_data()
        roles = self.role_manager.get_guild_roles(self.guild)
        container = Container()
        sep = Separator()
        title_text = TextDisplay('### [ Self Roles ]')
        container.add_item(title_text)
        for role in roles:
            role_data = self.guild.get_role(role)
            role_button = RoleButton(role_data)
            role_section = Section(f'### {role_data.name}', accessory=role_button)
            container.add_item(sep)
            container.add_item(role_section)
        container.add_item(sep)
        role_footer = TextDisplay('`The Cardinals`')
        container.accent_color = 0x00FFFF
        container.add_item(role_footer)
        self.add_item(container)
        
        
        
            
class ButtonRoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_manager = RoleManager()
        
    role_group = app_commands.Group(name='br', description='Button Role Manager')
    
    @role_group.command(name='add', description='Add a button role')
    @app_commands.checks.has_permissions(administrator=True)
    async def add(self, interaction: discord.Interaction, role: discord.Role):
        try:
            status, result = self.role_manager.add_role(interaction.guild, role)
            await interaction.response.send_message(result, ephemeral=True)
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(str(e), ephemeral=True)
            
    @role_group.command(name='remove', description='Remove a button role')
    @app_commands.checks.has_permissions(administrator=True)
    async def remove(self, interaction: discord.Interaction, role: discord.Role):
        try:
            status, result = self.role_manager.remove_role(interaction.guild, role)
            await interaction.response.send_message(result, ephemeral=True)
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(str(e), ephemeral=True)
            
    @role_group.command(name='panel', description='Send button role panel')
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        try:
            if not self.role_manager.get_guild_roles(interaction.guild):
                await interaction.response.send_message('No Button Roles Found', ephemeral=True)
                return
            await interaction.response.send_message('Successfully sent panel', ephemeral=True)
            await interaction.channel.send(view=RoleLayout(interaction.guild))
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(str(e), ephemeral=True)

async def setup(bot):
    await bot.add_cog(ButtonRoleCog(bot))