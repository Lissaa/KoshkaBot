import discord, random, json
from discord.ext import commands
from config.config import config, get_embed, check

class Currency:
    def __init__(self, client):
        self.client = client
        self.config = config('koshka.db')
        self.cur_s = self.config.get_table('Settings', get_row = True, column_name = 'Currency_name')[0][0]
        self.cur_p = self.config.get_table('Settings', get_row = True, column_name = 'Currency_plural_name')[0][0]
        self.cur_i = self.config.get_table('Settings', get_row = True, column_name = 'Currency_icon')[0][0]


    
    @commands.command(pass_context=True)
    async def money(self, ctx, user : discord.User = None):
        """Check a user's money"""
        message=ctx.message
        if not user: user = ctx.message.author
        amount = self.modify(user, get_amount = True)
        if not amount: await self.client.send_message(message.channel, embed=get_embed(title="{} has 0 {}{}.".format(user.name, self.cur_s, self.cur_i)))
        else: await self.client.send_message(message.channel, embed=get_embed(title="{} has {} {}{}.".format(user.name, amount, self.cur_p, self.cur_i)))

    @commands.command(pass_context=True)
    async def lb(self, ctx):
        message = ctx.message
        try:
            lb = self.config.get_sorted('Cash', 'Amount')
        except OSError as e:
            print(e.args[0])
            return
        txt = '\n'
        max_width = 0
        if len(lb) < 15:
            for i in range(0,len(lb)):
                if len(lb[i][1]) > max_width:
                    max_width = len(lb[i][1])
            title = "{0:>{1}} \tMoney:".format("Name:",max_width+1)
            for i in lb:
                txt += "{0:>{1}} \t{2}\n".format(i[1],max_width+1, i[2])
        else:
            for i in range(0, 15):
                if len(lb[i][1]) > max_width:
                    max_width = len(lb[i][1])
            title = "{0:<{1}}  Money:".format("Name:",max_width+1)
            for i in range(0,15):
                txt += "{0:<{1}}  {2}\n".format(lb[i][1],max_width+1, lb[i][2])
        with open('a.txt', 'w', encoding = 'utf-8') as a:
            a.write(txt)
        print(max_width)
        title+=txt
        await self.client.say("```"+title+"```")
        
    def modify(self, user, amount = 0, get_amount = False, take_all = False):
        try:
            _amount = self.config.get_table('Cash', column_name = 'Amount', row_id = int(user.id))[0][0]
            amount += _amount
            if amount < 0:
                raise TypeError("Amount less than 0")
            if take_all:
                amount = 0
            self.config.change('Cash', user.id, 'Amount', amount)
        except ValueError as e:
            print(e.args)
            self.config.make_row('Cash', (int(user.id), user.name, amount))
            _amount = 0
        if get_amount:
            return _amount
        
    @check.owner_only()       
    @commands.command(pass_context=True)
    async def draw(self, ctx, amount : int = 0):
        """Bot owner only, draw a random person and award the money"""
        message = ctx.message
        if not amount:
            amount = random.randint(1,100)
        while 1:
            user = random.choice(list(message.server.members))
            if not user.bot: break
        try:
            self.modify(user, int(amount))
        except OSError as e:
            print(e.args[0])
            return
        if amount == 1:
            await self.client.send_message(message.channel, embed=get_embed(title="{} has won 1 {}{}.".format(user.name, self.cur_s, self.cur_i)))
        else:
            await self.client.send_message(message.channel, embed=get_embed(title="{} has won {} {}{}.".format(user.name,amount, self.cur_p, self.cur_i)))

    @check.owner_only()
    @commands.command(pass_context=True)
    async def add(self, ctx, amount : int, user : discord.User = None):
        """Bot owner only command, give money to a user"""
        if not user: user = ctx.message.author
        message=ctx.message
        if 0 > amount > 300:
            await self.client.send_message(message.channel, embed=get_embed(title="Invalid amount."))
            return
        try:
            self.modify(user, int(amount))
        except OSError as e:
            print(e.args[0])
            return
        if amount == 1:
            await self.client.send_message(message.channel, embed=get_embed(title="{} added 1 {}{}.".format(user.name, self.cur_s, self.cur_i)))
        else:
            await self.client.send_message(message.channel, embed=get_embed(title="{} added {} {}{}.".format(user.name,amount, self.cur_p, self.cur_i)))

    @commands.command(pass_context=True)
    async def give(self, ctx, amount : int, user : discord.User = None):
        """not bot owner only command, give money to a user"""
        if not user: user = ctx.message.author
        message=ctx.message

        try:
            self.modify(message.author, amount*-1)
        except OSError as e:
            print(e.args[0])
            return
        except TypeError as e:
            await self.client.send_message(message.channel, embed=get_embed(title="You don't have enough {}{}.".format(self.cur_p, self.cur_i)))
            return
        
        try:
            self.modify(user, int(amount))
        except OSError as e:
            print(e.args[0])
            return
        if amount == 1:
            await self.client.send_message(message.channel, embed=get_embed(title="{} give {} 1 {}{}.".format(message.author,user.name, self.cur_s, self.cur_i)))
        else:
            await self.client.send_message(message.channel, embed=get_embed(title="{} give {} {} {}{}.".format(message.author,user.name,amount, self.cur_p, self.cur_i)))

    @check.owner_only()
    @commands.command(pass_context=True)
    async def take(self, ctx, amount : int, user : discord.User = None):
        """Bot owner only commnad, take money from a user"""
        if not user: user = ctx.message.author
        if int(amount) < 0: take_all = True
        else: take_all =False
        message=ctx.message
        try:
            self.modify(user, amount*-1, take_all = take_all)
        except OSError as e:
            print(e.args[0])
            return
        except TypeError as e:
            await self.client.send_message(message.channel, embed=get_embed(title="You don't have enough {}{}.".format(self.cur_p, self.cur_i)))
            return
        if amount == 1:
            await self.client.send_message(message.channel, embed=get_embed(title="{} lost 1 {}{}.".format(user.name, self.cur_s, self.cur_i)))
        else:
            await self.client.send_message(message.channel, embed=get_embed(title="{} lost {} {}{}.".format(user.name, amount, self.cur_p, self.cur_i)))
            
    @commands.command(pass_context=True)
    async def bet(self, ctx, amount : int, side : int):
        """Guess the value of the 12 sided dice, guess it right, you win 10 times your bet"""
        message = ctx.message
        user = message.author
        if side not in range(1,13):
            await self.client.send_message(message.channel, embed=get_embed(title="Side not valid, valid sides are: 1-12"))
            return
        elif amount < 3:
            await self.client.send_message(message.channel, embed=get_embed(title="Cannot bet less than 10"))
            return
        try:
            self.modify(user, int(amount*-1))
        except OSError as e:
            print(e.args[0])
            return
        except TypeError as e:
            await self.client.send_message(message.channel, embed=get_embed(title="You don't have enough {}{}.".format(self.cur_p, self.cur_i)))
            return
        win_num = random.randint(1,12)
        if int(side) == int(win_num):
            win_amount = int(amount*10)
            self.modify(user, win_amount)
            await self.client.send_message(message.channel, embed=get_embed(title="You won {} {}{} for guessing it right.".format(win_amount,self.cur_p, self.cur_i)))
        else:
            await self.client.send_message(message.channel, embed=get_embed(title="Better luck next time, the dice rolled {}.".format(win_num)))
                                           
def setup(client):
    client.add_cog(Currency(client))
