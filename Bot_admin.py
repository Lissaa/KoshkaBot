import discord, sys
from discord.ext import commands
from config.config import config, get_embed, check

class Bot_Administration:
    def __init__(self, client):
        self.client = client
        self.config = config('koshka.db')
        
    @commands.command(pass_context=True)
    async def changeprefix(self, ctx, prefix : str):
        message = ctx.message
        self.client.command_prefix = list(prefix)
        self.config.change('Settings', 1, 'Prefix', str(prefix))
        await self.client.send_message(message.channel, embed=get_embed(title='{} has changed prefix to: {}'.format(message.author,prefix)))

    @check.owner_only()
    @commands.command(pass_context=True)
    async def die(self, ctx):
        await self.client.send_message(ctx.message.channel, embed=get_embed('Bye.'))
        client.close()
        sys.exit(0)
        
def setup(client):
    client.add_cog(Bot_Administration(client))
