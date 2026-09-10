import discord
from discord.ext import commands
from openai import OpenAI
import traceback
from discord import app_commands
from discord.ui import TextDisplay, LayoutView, Container, Separator


class AiManager:
    def __init__(self):
        self.client = OpenAI(
            base_url="http://92.4.71.79:11434/v1",
            api_key="ollama",  # Required by SDK syntax, but ignored by Ollama
        )
        self.client_modal = "qwen2.5:7b"
        self.personality = """
        You are Cardinal, An Ai Assistant, Created By The Cardinals Team.
        Your modal is CardinalAI1.0.
        Your purpose is to help users and management in Cardinals Discord Server and help in programming.
        You are a good coder and reply after some research and have knowledge of discord.
        """

    def get_response(self, prompt: str):
        response = self.client.chat.completions.create(
            model=self.client_modal,
            messages=[
                {"role": "system", "content": self.personality},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content


class MessageBox(LayoutView):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(timeout=None)
        self._build_box()

    def _build_box(self):
        container = Container()
        sep = Separator()

        message = TextDisplay(self.msg)
        credit_text = TextDisplay("-# CardinalsAI")
        container.add_item(message)
        container.add_item(sep)
        container.add_item(credit_text)
        container.accent_color = 0x00FFFF

        self.add_item(container)


class CardinalAi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ai_manager = AiManager()

    @app_commands.command(name="chat", description="Chat with Cardinal Ai")
    async def chat(self, interaction: discord.Interaction, message: str):
        try:
            await interaction.response.defer()

            response = self.ai_manager.get_response(message)
            await interaction.followup.send(view=MessageBox(response))
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(str(e), ephemeral=True)


async def setup(bot):
    await bot.add_cog(CardinalAi(bot))
