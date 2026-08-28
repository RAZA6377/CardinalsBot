from __future__ import annotations
import discord
from discord.ext import commands
from discord.ui import LayoutView, Container, Button, Separator, ActionRow, TextDisplay, Modal, TextInput, Select
import traceback
import time
from handlers._data import DataManager
from handlers._account import BsAccount

CLAN_DESCRIPTION = '''
The Clan System is designed for players who enjoy competitive or progression-based gameplay. Create your own clan, challenge other clans, compete for victories, and level up together.

Each clan has a member limit and must recruit at least 4 players within one week of creation. If a clan fails to meet this requirement, it will be automatically deleted.
'''


class ClanManager:
    def __init__(self):
        self.data_manager = DataManager()
        self.file = self.data_manager.get_data_dir() / "clan.json"
        self.clan_limit = 5
        self.players_limit = 8
        
        
    def get_data(self):
        return self.data_manager.read_file(self.file)
        
    def write(self, data):
        return self.data_manager.save_file(self.file, data)
        
    def get_clans(self):
        data = self.get_data()
        return data.keys()
        
    def get_clan(self, clan_name: str):
        data = self.get_data()
        return data[clan_name]
        
    def get_user_info(self, user: discord.Member):
        for clan_name, clan_data in self.get_data().items():
            if int(clan_data['leader_id']) == int(user.id):
                return "Leader", clan_name
                break
            for players in clan_data['players']:
                if int(players['user_id']) == int(user.id):
                    return "Member", clan_name
                    break
        return None, None
        
    def add_user(self, user: discord.Member, v2_id: str, clan_name: str):
        data = self.get_data()
        role, clan = self.get_user_info(user)
        if role == "Leader":
            return f"You already own {clan}"
            
        elif role == "Member":
            return f"You are already a member of {clan}"
            
        elif len(data[clan_name]['players']) == self.players_limit:
            return "Players limit reached"
            
        else:
            user_data = {"name": user.name, "user_id": user.id, "aid": v2_id}
            data[clan_name]['players'].append(user_data)
            self.write(data)
            return "Success"
            
    def remove_user(self, user: discord.Member):
        data = self.get_data()
        role, clan = self.get_user_info(user)
        if role is None:
            return "User does not belong to any clan"
        elif role == "Leader":
            return "User owns this clan"
            
        else:
            clan_players = data[clan]['players']
            for index, user_data in enumerate(clan_players):
                if user_data['user_id'] == user.id:
                    del data[clan]['players'][index]
                    self.write(data)
                    break
            return f"User is successfully removed from {clan}"
            
        
    def create(self, user: discord.Member, clan_name: str, v2_id: str, description: str):
        data = self.get_data()
        role, clan = self.get_user_info(user)
        if role == "Leader":
            return 'error', f"You already own {clan}"
            
        elif role == "Member":
            return 'error', f"You are already a member of {clan}"
            
        elif len(data.keys()) == self.clan_limit:
            return 'error', "Clan limit reached"
        
        else:
            leader_info = {"name": user.name, "user_id": user.id, "aid": v2_id}
            data[clan_name] = {
                'description': description,
                'leader_id': int(user.id),
                'players': [leader_info],
                'clan_role_id': None,
                'clan_thread_id': None,
                'won' : 0,
                'lost' : 0,
                'created_at' : int(time.time())
            }
            
            self.write(data)
            return 'created', data
            
    def delete(self, user: discord.Member):
        data = self.get_data()
        role, clan = self.get_user_info(user)
        if role == "Member":
            return f"User is member of {clan}"
        elif role is None:
            return "User does not belongs to any clan"
        else:
            del data[clan]
            self.write(data)
            return f"Successfully deleted {clan}"
            
            
            
class ConfirmView(discord.ui.View):
    def __init__(
        self,
        on_confirm,
        on_deny
    ):
        super().__init__(timeout=None)

        self.on_confirm = on_confirm
        self.on_deny = on_deny

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.success
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        try:
            await self.on_confirm(interaction)
        except:
            traceback.print_exc()

    @discord.ui.button(
        label="Deny",
        style=discord.ButtonStyle.danger
    )
    async def deny(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        try:
            await self.on_deny(interaction)
        except:
            traceback.print_exc()
        
class CreateClanButton(Button):
    def __init__(self):
        super().__init__(
            label='Create your clan',
            style=discord.ButtonStyle.secondary,
            custom_id='clan:create'
            )
            
        self.clan_manager = ClanManager()
        
    async def callback(self, interaction: discord.Interaction):
        try:
            role, clan_name = self.clan_manager.get_user_info(interaction.user)
            print(role, clan_name)
            if role == 'Leader':
                await interaction.response.send_message(f'You already own {clan_name} clan', ephemeral=True)
                return
            elif role == 'Member':
                await interaction.response.send_message(f'You are already a member of {clan_name} clan', ephemeral=True)
                return
            else:
                await interaction.response.send_modal(CreateClanModal())
        except Exception as e:
            await interaction.response.send_message(e, ephemeral=True)
            traceback.print_exc()
            
class JoinButton(Button):
    def __init__(self):
        super().__init__(
            label='Join a clan', 
            style=discord.ButtonStyle.secondary, 
            custom_id='clan:join'
            )
            
        self.clan_manager = ClanManager()
        
    async def callback(self, interaction: discord.Interaction):
        print('Join button pressed')
        try:
            role, clan_name = self.clan_manager.get_user_info(interaction.user)
            print(role, clan_name)
            if role == 'Leader':
                await interaction.response.send_message(f'You already own {clan_name} clan', ephemeral=True)
                return
            elif role == 'Member':
                await interaction.response.send_message(f'You are already a member of {clan_name} clan', ephemeral=True)
                return
            else:
                await interaction.response.send_modal(JoinClanModal())
                
        except Exception as e:
            await interaction.response.send_message(e, ephemeral=True)
            traceback.print_exc()
            

class ClanListButton(Button):
    def __init__(self):
        super().__init__(
            label='Available Clans',
            style=discord.ButtonStyle.secondary,
            custom_id='clan:list'
            )
        self.clan_manager = ClanManager()
        
    async def callback(self, interaction: discord.Interaction):
        data = self.clan_manager.get_data()
        embed = discord.Embed(title='Available Clans', description='A list of available clans', color=0x00FFFF)
        if data != {}:
            for clan_name, clan_data in data.items():
                embed.add_field(
                    name=f'Clan: {clan_name}', 
                    value=f'**Leader** : <@{int(clan_data['leader_id'])}\n**Clan Role** : <@&{int(clan_data['clan_role_id'])}\n**Total Member** : {len(clan_data['players'])}\n**Won** : {clan_data['won']}\n**Lost** : {clan_data['lost']}',inline=True)
                
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message('```No Available Clans Found.```', ephemeral=True)
            return
    
class JoinClanModal(Modal):
    def __init__(self):
        super().__init__(title='Join a clan', custom_id='clan:join_modal')
        self.clan_manager = ClanManager()
    
        self.aid = TextInput(
            label='Enter your a-ID',
            placeholder='Example: a-xxx', 
            required=True,
        )
        
        options = [
            discord.SelectOption(
                label=clan_name,
                value=clan_name
            )
            for clan_name, clan_data in self.clan_manager.get_data().items()
        ]
        
        self.clan_select = Select(
            placeholder='Select a clan',
            options=options,
            required=True
        )
        self.add_item(self.aid)
        self.add_item(
            discord.ui.Label(
                text='Select a clan',
                component=self.clan_select
            )
        )
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.aid_value = BsAccount(self.aid.value).get_aid_info()
            print(self.aid_value)
            self.selected_clan = self.clan_select.values[0]
            print(self.selected_clan)
            self.applicant = interaction.user
            clan_info = self.clan_manager.get_clan(self.selected_clan)
            clan_leader = interaction.guild.get_member(clan_info['leader_id'])
            clan_thread = interaction.guild.fetch_channel(clan_info['clan_thread_id'])
            embed = discord.Embed(title='Clan Join Request', description=f"{interaction.user.name} Applied for your clan.\n```Username : {interaction.user.name}\nDiscord Id : {interaction.user.id}\nBs Aid : {self.aid_value}```", color=0x00FFFF)
            
            async def on_approval_accept(interaction: discord.Interaction):
                clan_role = interaction.guild.get_role(clan_info['clan_role_id'])
                await self.applicant.add_roles(clan_role)
                user_add = self.clan_manager.add_user(self.applicant,self.aid_value, self.selected_clan)
                await interaction.response.edit_message(view=None)
                if user_add == 'Success':
                    try:
                        await self.applicant.send(f'Congratulations! You are now a member of {self.selected_clan} Clan')
                    except:
                        pass
                else:
                    await self.applicant.send(user_add)
        
            async def on_approval_deny(interaction: discord.Interaction):
                await interaction.response.edit_message(view=None)
                await self.applicant.send(f'Your approval for {self.selected_clan} Clan has been declined. Try again')
            
            async def on_aid_confirm(interaction: discord.Interaction):
                await clan_thread.send(clan_leader.mention, embed=embed,view=ConfirmView(on_confirm=on_approval_accept(interaction.guild), on_deny=on_approval_deny))
                await interaction.response.edit_message(content=f"Your request has been sent to clan's thread", view=None)
                
            async def on_aid_deny(interaction: discord.Interaction):
                await interaction.response.edit_message(content="Request Cancelled.", view=None)
                return
        
            if self.aid_value is None:
                await interaction.response.send_message('Invalid `a-id`. Try again', ephemeral=True)
                return
            else:
                aid_confirmation_embed = discord.Embed(title='Account Id Confirmation', description=f'**Tag**: `{self.aid_value['tag']}`\n**Account ID** : `{self.aid_value['id']}`\n**Created** : `{self.aid_value['create_time']}`',color=0x00FFFF)
                await interaction.response.send_message(embed=aid_confirmation_embed, view=ConfirmView(on_confirm=on_aid_confirm, on_deny=on_aid_deny))
        
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(e, ephemeral=True)
            
class CreateClanModal(Modal):
    def __init__(self):
        super().__init__(title='Join a clan', custom_id='clan:create_modal')
        self.clan_manager = ClanManager()
    
        self.aid = TextInput(
            label='Enter your a-ID',
            placeholder='Example: a-xxx', 
            required=True,
        )
        self.clan_name = TextInput(
            label='Enter your clan',
            placeholder='Example: Cardinals',
            max_length=15,
            required=True,
        )
        
        self.clan_description = TextInput(
            label='Enter your clan description',
            placeholder='Example: We are a clan.',
            max_length=30,
            required=True,
        )
        
        self.add_item(self.aid)
        self.add_item(self.clan_name)
        self.add_item(self.clan_description)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            
            self.aid_value = BsAccount(self.aid.value).get_aid_info()
            self.clan_name = self.clan_name.value 
            self.clan_desc = self.clan_description.value
            print(self.aid_value)
            print(self.clan_name)
            print(self.clan_desc)
            data = self.clan_manager.get_data()
            print(data)
            if self.aid_value is None:
                await interaction.response.send_message('Invalid a-id entered', ephemeral=True)
                return
            
            if self.clan_name in data:
                await interaction.response.send_message('`A clan already exist with this name. Try something diffrent.`', ephemeral=True)
                return
            for clan_name, clan_data in data.items():
                for player in clan_data['players']:
                    if self.aid_value['id'] == players['aid']:
                        await interaction.response.send_message(f'`This account id already exist in {clan_name} members list`', ephemeral=True)
                        return
            await interaction.response.defer()
            status, result = self.clan_manager.create(
                interaction.user,
                self.clan_name,
                self.aid_value['id'],
                self.clan_desc
                    )
            if status == 'error':
                await interaction.response.send_message(result, ephemeral=True)
                return
            
            channel = interaction.guild.get_channel(1541464867641229423)
            clan_thread = await channel.create_thread(name=f'{self.clan_name} Clan', invitable=False)
            clan_role = await interaction.guild.create_role(name=self.clan_name)
            await clan_thread.add_user(interaction.user)
            await interaction.user.add_roles(clan_role)
            await clan_thread.send(f'This is a discussion thread for **{self.clan_name}.\n**Clan Leader** : {interaction.user.mention}')
            result[self.clan_name]['clan_role_id'] = clan_role.id
            result[self.clan_name]['clan_thread_id'] = clan_thread.id
            print(result)
            self.clan_manager.write(result)
            embed = discord.Embed(
                title='Clan Created Successfully',
                description=f'`Clan    Name`: {self.clan_name}\n`Clan       Description` : {self.clan_desc}\n`Leader    Info` : {result[self.clan_name]['players']}\n`Clan Role` : {clan_role.mention}\n`Clan       Thread` : {clan_thread.mention}',
                    color=0x00FFFF
                    )
            print(f'Created a clan by {interaction.user.name}')
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception:
          #  await interaction.response.send_message(traceback.format_exc(), ephemeral=True)
            traceback.print_exc()
            
class ClanDashboard(LayoutView):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self._build_dashboard()
        
    def _build_dashboard(self):
        clan_manager = ClanManager()
        container = Container()
        sep = Separator()
        clan_text = TextDisplay("## Clan System")
        container.add_item(clan_text)
        container.add_item(sep)
        clan_desc = TextDisplay(f"```js\n{CLAN_DESCRIPTION}\n```")
        container.add_item(clan_desc)
        container.add_item(sep)
        button_row = ActionRow()
        button_row.add_item(JoinButton())
        button_row.add_item(CreateClanButton())
        button_row.add_item(ClanListButton())
        container.add_item(button_row)
        container.accent_color = 0x00FFFF
        self.add_item(container)
        
        
class ClanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def clandash(self, ctx):
        try:
            await ctx.send(view=ClanDashboard(self.bot))
        except Exception:
            await ctx.send(traceback.format_exc())
            
        
        
async def setup(bot):
    await bot.add_cog(ClanCog(bot))