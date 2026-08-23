import discord
from discord.ext import commands, tasks
from discord.ui import LayoutView, Container, Button, Section, Separator, ActionRow, TextDisplay
import time

CLAN_DESCRIPTION = '''
The Clan System is designed for players who enjoy competitive or progression-based gameplay. Create your own clan, challenge other clans, compete for victories, and level up together.

Each clan has a member limit and must recruit at least 4 players within one week of creation. If a clan fails to meet this requirement, it will be automatically deleted.
'''

class ClanManager:
    def __init__(self, bot, ctx: commands.Context):
        self.bot = bot
        self.ctx = ctx
        self.file = self.bot.data_manager.get_data_dir() / "clan.json"
        self.clan_limit = 5
        self.players_limit = 8
        
        
    def get_data(self):
        return self.bot.data_manager.read_file(self.file)
        
    def write(self, data):
        return self.bot.data_manager.save_file(self.file, data)
        
    def get_user_info(self, user: discord.Member):
        for clan_name, clan_data in self.get_data():
            if int(clan_data['leader']) == int(user.id):
                return "Leader", clan_name
                break
            for players in clan_data['players']:
                if int(players['uid']) == int(user.id):
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
            clan_role = self.ctx.guild.get_role(int(data[clan_name]['clan_role']))
            await user.add_roles(clan_role)
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
                    clan_role = self.ctx.guild.get_role(int(data[clan]['clan_role']))
                    await user.add_roles(clan_role)
                    self.save_data(data)
                    break
            return f"User is successfully removed from {clan}"
            
        
    def create(self, user: discord.Member, clan_name: str, v2_id: str):
        data = self.get_data()
        role, clan = self.get_user_info(user)
        if role == "Leader":
            return f"You already own {clan}"
            
        elif role == "Member":
            return f"You are already a member of {clan}"
            
        elif len(data.keys()) == self.clan_limit:
            return "Clan limit reached"
        
        else:
            clan_role = await self.ctx.guild.create_role(name=clan_name)
            await user.add_role(clan_role)
            leader_info = {"name": user.name, "user_id": user.id, "aid": v2_id}
            data[clan_name] = {
                'leader': int(user.id),
                'players': [leader_info],
                'clan_role': clan_role.id,
                'won' : 0,
                'lost' : 0,
                'created_at' : int(time.time())
            }
            
            self.write(data)
            return data
            
    def delete(self, user: discord.Member):
        data = self.get_data()
        role, clan = self.get_user_info(user)
        if role == "Member":
            return f"User is member of {clan}"
        elif role is None:
            return "User does not belongs to any clan"
        else:
            clan_role = self.ctx.guild.get_role(int(data[clan]['clan_role']))
            await self.ctx.guild.delete_role(clan_role)
            del data[clan]
            self.save_data(data)
            return "Successfully deleted {clan}"
            
class ClanDashboard(LayoutView):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self._build_dashboard()
        
    def _build_dashboard(self):
        clan_manager = ClanManager(self.bot)
        container = Container()
        sep = Separator()
        clan_text = TextDisplay("## Clan System")
        container.add_item(clan_text)
        container.add_item(sep)
        clan_desc = TextDisplay(f"```js\n{CLAN_DESCRIPTION}\n````")
        container.add_item(clan_desc)
        button_row = ActionRow()
        join_button = Button(label='Join Clan', style=discord.ButtonStyle.secondary)
        clan_button = Button(label='Available Clans', style=discord.ButtonStyle.secondary)
        
        
class ClanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        pass
        
        
async def setup(bot):
    await bot.add_cog(ClanCog(bot))