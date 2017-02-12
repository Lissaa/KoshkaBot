import discord, asyncio, logging, os, copy, re
from discord.ext import commands
from config.config import config

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


conf = config(os.path.join(os.getcwd(), 'Koshka.db'))
cur_s = conf.get_table('Settings', get_row = True, column_name = 'Currency_name')[0][0]
cur_p = conf.get_table('Settings', get_row = True, column_name = 'Currency_plural_name')[0][0]
cur_i = conf.get_table('Settings', get_row = True, column_name = 'Currency_icon')[0][0]
prefix = conf.get_table('Settings', get_row = True, column_name = 'Prefix')[0][0]
while 1:
    try:
        client = commands.Bot(list(prefix))

        @client.event
        async def on_ready():
            print('Logged in as')
            print(client.user.name)
            print(client.user.id)
            print('------')


        def get_embed(title=None, txt=None):
            if title and txt:
                embed=discord.Embed(title=title, description=txt, colour=discord.Colour.red())
            elif title:
                embed=discord.Embed(title=title, colour=discord.Colour.red())
            elif txt:
                embed=discord.Embed(description=txt, colour=discord.Colour.red())
            else: embed=None
            return embed

        @client.command(pass_context=True)
        async def prune(ctx, amount : int = 100):
            message=ctx.message
            if amount > 150:
                await client.send_message(message.channel, embed=get_embed(title="Cannot prune more than 150 messages"))
                return
            await client.purge_from(message.channel, limit = amount+1)
            tmp = await client.send_message(message.channel, embed=get_embed(title='Successfully pruned {} messages.'.format(amount)))
            await asyncio.sleep(2)
            await client.delete_message(tmp)

        @client.command(pass_context=True)
        async def say(ctx, *msg : str):
            await client.purge_from(ctx.message.channel, limit = 1)
            await client.send_message(ctx.message.channel, embed=get_embed(txt=" ".join(msg)))

        @client.event
        async def on_message(message):
            if 'help' in message.content and '{}help'.format(client.command_prefix[0]) not in message.content:
                await client.send_message(message.channel, embed=get_embed(txt="Type {}help for help".format(client.command_prefix[0])))
            if re.findall("^<@!?277664561119625217>", message.content):
                message = copy.deepcopy(message)
                txt=re.match("^<@!?277664561119625217> (?P<msg>.+)", message.content)
                message.content = "{}clever {}".format(client.command_prefix[0], txt['msg'])

            await client.process_commands(message)


        initial_extensions = [
            'vainglory',
            'money',
            'Bot_admin',
            'Blackjack',
            'clever_bot'
            ]

        for ex in initial_extensions:
            client.load_extension(ex)
        client.handle_message("""To add me to your server: =>https://discordapp.com/oauth2/authorize?client_id=277664561119625217&scope=bot&permissions=66186303
                                          \nMessage <@!95280508384063488> for more support.""")
        client.run(CLIENTID) ###Change the CLIENTID to your bot id
    except discord.HTTPException as e:
        print(e.response, e.message, file = stderr)
        pass
    
