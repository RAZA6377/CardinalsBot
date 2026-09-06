from __future__ import annotations
import typing
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import LayoutView, Container, Button, Separator, ActionRow, TextDisplay, Modal, TextInput, MediaGallery, Select
import traceback
import time
from handlers._data import DataManager
from handlers._account import BsAccount

CLAN_DESCRIPTION = '''
The Clan System is designed for players who enjoy competitive or progression-based gameplay.
'''


class ClanManager:
    def __init__(self):
        self.data_manager = DataManager()
        self.file = self.data_manager.get_data_dir() / "clan.json"
        self.challenge_file = self.data_manager.get_data_dir() / "clan_challenges.json"
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
        
    async def update_score(self, interaction: discord.Interaction, clan_name: str, option: str, points: int):
        data = self.get_data()
        clan_info = data.get(clan_name)
        if clan_info is None:
            return 'error', 'Clan not found'
        if option not in ('won', 'lost'):
            return 'error', 'Option not valid'
        
        if points < 0:
            return 'error', 'Points can\'t be in negative'
            
        data[clan_name][option] += points
        self.write(data)
        clan_leader = interaction.guild.get_member(int(data[clan_name]['leader_id']))
        clan_thread = await interaction.guild.fetch_channel(int(data[clan_name]['clan_thread_id']))
        await clan_thread.send(f'{clan_leader.mention}\n```Updated clan {option} Points to {points}\nTotal = {data[clan_name][option]}```')
        return 'success', f'Updated **{clan_name}** {option} Points to {data[clan_name][option]}'
        
    async def add_user(self, user: discord.Member, v2_id: str, clan_name: str):
        data = self.get_data()
        role, clan = self.get_user_info(user)
        if role == "Leader":
            return f"You already own {clan}"
            
        elif role == "Member":
            return f"You are already a member of {clan}"
            
        elif len(data[clan_name]['players']) == self.players_limit:
            return "Players limit reached"
            
        else:
            user_data = {"name": user.name, "user_id": user.id, "aid": v2_id['id']}
            data[clan_name]['players'].append(user_data)
            self.write(data)
            clan_role_id = data[clan_name]['clan_role_id']
            clan_thread_id = data[clan_name]['clan_thread_id']
            clan_role = user.guild.get_role(clan_role_id)
            clan_thread = await user.guild.fetch_channel(clan_thread_id)
            await user.add_roles(clan_role)
            await clan_thread.add_user(user)
            await clan_thread.send(f'Welcome {user.mention} to **{clan_name} Clan**')
            return "Success"
            
    async def remove_user(self, user: discord.Member):
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
            clan_role = user.guild.get_role(data[clan]['clan_role_id'])
            clan_thread = await user.guild.fetch_channel(data[clan]['clan_thread_id'])
            await user.remove_roles(clan_role)
            await clan_thread.remove_user(user)
            await clan_thread.send(f'Removed {user.mention} From **{clan} Clan**')
            return f"User is successfully removed from {clan}"
            
        
    async def create(self, user: discord.Member, clan_name: str, v2_id: str, description: str):
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
            channel = user.guild.get_channel(1541464867641229423)
            clan_thread = await channel.create_thread(name=f'{clan_name} Clan', invitable=False)
            clan_role = await user.guild.create_role(name=f'[Clan] {clan_name}')
            await clan_thread.add_user(user)
            await user.add_roles(clan_role)
            await clan_thread.send(f'This is a discussion thread for **{clan_name}**.\n**Clan Leader** : {user.mention}')
            data[clan_name] = {
                'description': description,
                'leader_id': int(user.id),
                'players': [leader_info],
                'clan_role_id': clan_role.id,
                'clan_thread_id': clan_thread.id,
                'won' : 0,
                'lost' : 0,
                'status': None,
                'created_at' : int(time.time())
            }
            
            self.write(data)
            return 'created', data
            
    async def delete(self, user: discord.Member):
        data = self.get_data()
        role, clan = self.get_user_info(user)
        if role == "Member":
            return 'error', f"You are member of {clan} clan. You don\'t have permission to delete"
        elif role is None:
            return 'error', "User does not belongs to any clan"
        else:
            clan_data = data[clan]
            clan_role = user.guild.get_role(clan_data['clan_role_id'])
            clan_thread = await user.guild.fetch_channel(clan_data['clan_thread_id'])
            await clan_role.delete(reason='Clan deleted')
            await clan_thread.delete(reason='Clan deleted')
            del data[clan]
            self.write(data)
            return 'success', f"Successfully deleted {clan}"
            
    def get_challenge_data(self):
        return self.data_manager.read_file(self.challenge_file)
        
    def challenge_write(self, data):
        return self.data_manager.save_file(self.challenge_file, data)
        
    async def challenge(self, user: discord.Member, vs_clan: str):
        role, clan = self.get_user_info()
        if role == 'Member' or None:
            return 'error', 'You don\'t have permission to challenge'
        
            

class ClanMenu(Select):
    def __init__(self):
        clan_menu_options = {'Create Clan': 'create', 'Join Clan': 'join', 'Available Clans': 'list', 'Delete Clan': 'delete'}
        options = [discord.SelectOption(
            label=clan_option,
            value=clan_value
            )
            for clan_option, clan_value in clan_menu_options.items()
        ]
        
        super().__init__(placeholder='Select a clan option', options=options, custom_id='clan:clanmenu')
        self.clan_manager = ClanManager()
        
    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]
        
        # Create Clan
        if selected_value == 'create':
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
            except Exception:
                await interaction.response.send_message('Something went wrong, contact an admin', ephemeral=True)
                traceback.print_exc()
                
        # Join clan
        elif selected_value == 'join':
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
            except Exception:
                await interaction.response.send_message('Something went wrong, contact an admin', ephemeral=True)
                traceback.print_exc()
            
        # Clan List
        elif selected_value == 'list':
            data = self.clan_manager.get_data()
            embed = discord.Embed(title='Available Clans', description='A list of available clans', color=0x00FFFF)
            if data != {}:
                for clan_name, clan_data in data.items():
                    embed.add_field(
                    name=f'Clan: {clan_name}', 
                    value=f'**Leader** : <@{int(clan_data['leader_id'])}>\n**Clan Role** : <@&{int(clan_data['clan_role_id'])}>\n**Total Member** : {len(clan_data['players'])}\n**Won** : {clan_data['won']}\n**Lost** : {clan_data['lost']}',inline=True)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message('```No Available Clans Found.```', ephemeral=True)
                return
            
        # Clan delete
        
        elif selected_value == 'delete':
            try:
                status, result = await self.clan_manager.delete(interaction.user)
                if status == 'error':
                    await interaction.response.send_message(result, ephemeral=True)
                    return
                await interaction.response.send_message(result, ephemeral=True)
            except Exception:
                await interaction.response.send_message('Something went wrong, contact an admin', ephemeral=True)
                traceback.print_exc()
        
        
        
            
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
            clan_thread = await interaction.guild.fetch_channel(clan_info['clan_thread_id'])
            print(clan_thread)
            embed = discord.Embed(title='Clan Join Request', description=f"{interaction.user.name} Applied for your clan.\n```Username : {interaction.user.name}\nDiscord Id : {interaction.user.id}\nBs Aid : {self.aid_value}```", color=0x00FFFF)
            
            async def on_approval_accept(interaction: discord.Interaction):
                if interaction.user.id == clan_leader.id:
                    user_add = await self.clan_manager.add_user(self.applicant,self.aid_value, self.selected_clan)
                    await interaction.response.edit_message(content='**Approval Accepted**',view=None)
                    if user_add == 'Success':
                        try:
                            await self.applicant.send(f'Congratulations! You are now a member of {self.selected_clan} Clan')
                        except:
                            pass
                    else:
                        try:
                            await self.applicant.send(user_add)
                        except:
                            pass
                else:
                    await interaction.response.send_message('You aren\'t clan leader', ephemeral=True)
        
            async def on_approval_deny(interaction: discord.Interaction):
                if interaction.user.id == clan_leader.id:
                    await interaction.response.edit_message(content='Approval Denied', view=None)
                    try:
                        await self.applicant.send(f'Your approval for {self.selected_clan} Clan has been declined. Try again')
                    except:
                        pass
                else:
                    await interaction.response.send_message('You aren\'t clan leader', ephemeral=True)
            
            async def on_aid_confirm(interaction: discord.Interaction):
                await clan_thread.send(clan_leader.mention, embed=embed,view=ConfirmView(on_confirm=on_approval_accept, on_deny=on_approval_deny))
                await interaction.response.edit_message(content=f"Your request has been sent to clan's thread", view=None)
                
            async def on_aid_deny(interaction: discord.Interaction):
                await interaction.response.edit_message(content="Request Cancelled.", view=None)
                return
        
            if self.aid_value is None:
                await interaction.response.send_message('Invalid `a-id`. Try again', ephemeral=True)
                return
            else:
                aid_confirmation_embed = discord.Embed(title='Account Id Confirmation', description=f'**Tag**: `{self.aid_value['tag']}`\n**Account ID** : `{self.aid_value['id']}`\n**Created** : `{self.aid_value['create_time']}`',color=0x00FFFF)
                await interaction.response.send_message(embed=aid_confirmation_embed, view=ConfirmView(on_confirm=on_aid_confirm, on_deny=on_aid_deny), ephemeral=True)
        
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(str(e), ephemeral=True)
            
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
                    if self.aid_value['id'] == player['aid']:
                        await interaction.response.send_message(f'`This account id already exist in {clan_name} members list`', ephemeral=True)
                        return
                    
            status, result = await self.clan_manager.create(
                interaction.user,
                self.clan_name,
                self.aid_value['id'],
                self.clan_desc
                    )
            if status == 'error':
                await interaction.followup.send(result, ephemeral=True)
                return
            embed = discord.Embed(
                title='Clan Created Successfully',
                description=f'`Clan Name`: {self.clan_name}\n`Clan Description` : {self.clan_desc}\n`Leader Info` : \n- {result[self.clan_name]['players']}\n`Clan Role` : <@&{result[self.clan_name]['clan_role_id']}>\n`Clan Thread` : <#{result[self.clan_name]['clan_thread_id']}>',
                    color=0x00FFFF
                    )
            print(f'Created a clan by {interaction.user.name}')
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            await interaction.response.send_message('Something went wrong, contact an admin', ephemeral=True)
            traceback.print_exc()
            
class ChallengeDashboard(LayoutView):
    def __init__(self, clan):
        super().__init__(timeout=None)
        self.selected_players = []
        self.clan_manager = ClanManager()
        self._create_dashboard()
        
    def _create_dashboard(self):
        self.clear_items()
        container = Container()
        sep = Separator()
        
        header = TextDisplay('Challenge Dashboard')
        container.add_item(header)
        container.add_item(sep)
        choose_text = TextDisplay('```Choose your players```')
        container.add_item(choose_text)
        choose_row = ActionRow()
        options = [
            discord.SelectOption(
                label=str(player['name']),
                value=int(player['uid'])
            )
            for player in self.clan_manager.get_data()[clan]['players']
        ]
        player_selector = Select(
            placeholder='Select your warriors',
            options=options
            custom_id='challenge:warriors'
            )
        player_selector.callback = on_player_selection
        choose_row.add_item(player_selector)
        player_selected_text = ""
        index = 0
        for selected_player in self.selected_players:
            for clan_player in self.clan_manager.get_data()[clan]['players']:
                if int(clan_player['uid']) == int(selected_player):
                    player_selected_text += f"# {index+1} -- {clan_player['name']}\n> U-ID : {clan_player['uid']}\n> A-ID : {clan_player['aid']}"
        selected_text = TextDisplay(f'```{player_selected_text}```')
        container.add_item(choose_row)
        container.add_item(selected_text)
        
        async def on_player_selection(self, interaction: discord.Interaction):
            for i in self.values:
                self.selected_players.append(i)
            self._create_dashboard()
            
        self.add_item(container)
        
        
        
    
        
class ClanDashboard(LayoutView):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self._build_dashboard()
        
    def _build_dashboard(self):
        self.clear_items()
        clan_manager = ClanManager()
        container = Container()
        sep = Separator()
        clan_banner = MediaGallery(
                discord.MediaGalleryItem(
                    "https://cdn.discordapp.com/attachments/1539217756891643924/1543694391552774284/file_00000000f6788211ab4c8bd6ecaa42d8.png?ex=6a95ccef&is=6a947b6f&hm=12b8fa7d584f897e29412fd42eeccb804f89ee8412775aadb147c7b9bf9e99cd&"
                )
                    
        )
        container.add_item(clan_banner)
        container.add_item(sep)
        menu_row = ActionRow()
        clan_desc = TextDisplay(f"{CLAN_DESCRIPTION}")
        container.add_item(clan_desc)
        container.add_item(sep)
        menu_row.add_item(ClanMenu())
        container.add_item(menu_row)
        
        
        container.accent_color = 0x00FFFF
        self.add_item(container)
        
        
class ClanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clan_manager = ClanManager()
        
    async def clan_choices(
        self, 
        interaction: discord.Interaction,
        current: str
    ):
        data = self.clan_manager.get_data()
        return [
            app_commands.Choice(name=clan, value=clan)
            for clan, clan_data in data.items()
            if current.lower() in clan.lower()
        ][:5]
    
    clan_group = app_commands.Group(name='clan', description='Clan group')
    
    @clan_group.command(name='panel', description='Clan panel')
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message('Sent', ephemeral=True)
            await interaction.channel.send(view=ClanDashboard(self.bot))
        except Exception:
            await interaction.response.send_message(traceback.format_exc(), ephemeral=True)
        
    @clan_group.command(name='update_score', description='Update score for a clan')
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.autocomplete(clan_name=clan_choices)
    async def update_score(self, interaction: discord.Interaction, clan_name: str, option: typing.Literal['won', 'lost'], points: int):
        try:
            status, result = await self.clan_manager.update_score(interaction, clan_name, option, points)
            if status == 'error':
                await interaction.response.send_message(result, ephemeral=True)
            await interaction.response.send_message(f'```{result}```')
        except Exception as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            traceback.print_exc()
        
    @clan_group.command(name='challenge', description='Challenge a clan')
    @app_commands.autocomplete(clan_name=clan_choices)
    async def challenge(self, interaction: discord.Interaction, clan_name: str):
        role, clan = self.clan_manager.get_user_info(interaction.user)
        challenge_data = self.clan_manager.challenge_data()
        
        if clan_name == clan:
            await interaction.response.send_messsge('You cannot challenge your own clan', ephemeral=True)
            return
        
        if role == 'Member' or None:
            await interaction.response.send_messsge('You cannot challenge any clan', ephemeral=True)
            return
        
        if clan or clan_name in challenge_data:
            await interaction.response.send_messsge('Your or opponent clan is already in a match', ephemeral=True)
            return
        
        
        
        
            
        
async def setup(bot):
    await bot.add_cog(ClanCog(bot))