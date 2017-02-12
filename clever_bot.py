import discord
from discord.ext import commands
from config.config import get_clever, get_embed


class CleverBot:
    def __init__(self, client):
        self.client = client
        self.cs = None

    @commands.command(pass_context = True)
    async def clever(self, ctx, msg : str):
        message = ctx.message
        response = get_clever(self.cs, msg)
        self.cs = response['cs']
        await self.client.send_message(message.channel, embed=get_embed(response['output']))
    
def setup(client):
    client.add_cog(CleverBot(client))
