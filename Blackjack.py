import random
from config.config import config, get_embed
from discord.ext import commands
def get_suits():
    while 1:
        for suit in ['hearts','diamonds','spades','clubs']:
            yield suit

class Blackjack:
    def __init__(self):
        self.cards = ('ace','2','3','4','5','6','7','8','9','10','jack','queen','king')
        self.deck = []
        self.dealer_drew = []
        self.get_suits = get_suits()
        for card in self.cards:
            for i in range(0,4):
                self.deck.append("{}_of_{}".format(card, next(self.get_suits)))
        self.full_deck = self.deck.copy()
        for shuff in range(0,15):
            random.shuffle(self.deck)
        print(len(self.deck), self.deck)
        self.player_deck = []
        self.dealer_deck = []
        for i in range(0,2):
            self.deal('dealer')


    def check_deck(self):
        if not len(self.deck):
            self.deck = self.full_deck.copy()
            for shuff in range(0,15):
                random.shuffle(self.deck)
                
    def deal(self, player):
        self.check_deck()
        card = self.deck.pop()
        if player == 'player':
            self.player_deck.append(card)
        elif player == 'dealer':
            self.dealer_deck.append(card)
        else:
            raise SyntaxError('Ivalid player')
        return card


    def play(self, do):
        if do not in ('hit','stand'):
            raise TypeError('Unknown Command')
        if do == 'hit':
            new = self.deal('player')
        elif do == 'stand':
            while 1:
                result=self.check_over('dealer')
                try:
                    if 'busts' in result or result == 'blackjack':
                        return result
                except: pass
                if result >= 17:
                    return result
                else:
                    dealt = self.deal('dealer')
                    self.dealer_drew.append(dealt)
        return new

    def check_over(self, player='player'):
        if player == 'player':
            deck = self.player_deck
        else: deck = self.dealer_deck
        values = []
        values_2 = []
        for i in deck:
            val = i.split('_')[0]
            if val in ('jack','queen','king'):
                values.append(10)
                values_2.append(10)
            elif val == 'ace':
                values.append(1)
                values_2.append(11)
            else:
                values.append(int(val))
                values_2.append(int(val))

        if sum(values) > 21:
            return 'busts %s' % sum(values)
        elif sum(values) == 21 or sum(values_2) == 21:
            return 'blackjack'
        elif sum(values_2) < 21:
            return sum(values_2)
        return sum(values)
        

class Game:
    def __init__(self, client):
        self.client = client
        self.in_game = False
        self.current_game = None
        self.config = config('koshka.db')
        self.cur_s = self.config.get_table('Settings', get_row = True, column_name = 'Currency_name')[0][0]
        self.cur_p = self.config.get_table('Settings', get_row = True, column_name = 'Currency_plural_name')[0][0]
        self.cur_i = self.config.get_table('Settings', get_row = True, column_name = 'Currency_icon')[0][0]


    def modify(self, user, amount = 0, get_amount = False):
        try:
            _amount = self.config.get_table('Cash', column_name = 'Amount', row_id = int(user.id))[0][0]
            amount += _amount
            if amount < 0:
                raise TypeError("Amount less than 0")
            self.config.change('Cash', user.id, 'Amount', amount)
        except ValueError as e:
            print(e.args)
            self.config.make_row('Cash', (int(user.id), user.name, amount))
            _amount = 0
        if get_amount:
            return _amount        
        
    @commands.command(pass_context = True)
    async def hit(self, ctx):
        message= ctx.message
        if not self.in_game:
            await self.client.send_message(message.channel, embed=get_embed(title='No Game is in session, please start a game'))
            return
        if message.author != self.started_by:
            await self.client.send_message(message.channel, embed=get_embed(title='You did not start this game, please wait.'))
            return
        new = self.current_game.play('hit')
        await self.client.send_message(message.channel, embed=get_embed(title='You got hit with:', txt='\n{}\n'.format(new.replace('_',' '))))
        result = self.current_game.check_over()
        cards = ", ".join(self.current_game.player_deck)
        cards = cards.replace('_',' ')
        try:
            if 'busts' in result:
                await self.client.send_message(message.channel, embed=get_embed(title='Your are busted! with %s total: ' % result.split(' ')[1], txt='\n{}\n'.format(cards)))
                await self.client.send_message(message.channel, embed=get_embed(title='You lost {}'.format(int(self.game_bet))))
                self.in_game = False
                self.current_game = None
                return
            elif result == 'blackjack':
                await self.client.send_message(message.channel, embed=get_embed(title='Blackjack!', txt='\n{}\n'.format(cards)))
                try:
                    self.modify(message.author, int(self.game_bet*2.5))
                except OSError as e:
                    print(e.args[0])
                    return
                await self.client.send_message(message.channel, embed=get_embed(title='You won {}'.format(int(self.game_bet*1.5))))
                self.in_game = False
                self.current_game = None
                return
        except:
            await self.client.send_message(message.channel, embed=get_embed(title='Your cards are: ', txt='\n{} with {} total\n'.format(cards, result)))
            self.player_max = result
            
    @commands.command(pass_context = True)
    async def stand(self, ctx):
        message = ctx.message
        if not self.in_game:
            await self.client.send_message(message.channel, embed=get_embed(title='No Game is in session, please start a game'))
            return
        if message.author != self.started_by:
            await self.client.send_message(message.channel, embed=get_embed(title='You did not start this game, please wait.'))
            return
        await self.client.send_message(message.channel, embed=get_embed(title='The dealer\'s cards is:', txt='\n{} and {}\n'.format(
            self.current_game.dealer_deck[0].replace('_',' '), self.current_game.dealer_deck[1].replace('_',' '))))
        result = self.current_game.play('stand')
        for i in self.current_game.dealer_drew:
            await self.client.send_message(message.channel, embed=get_embed(title='The dealer got hit with %s'%i))
        else:
            await self.client.send_message(message.channel, embed=get_embed(title='The dealer standed'))
        cards = ", ".join(self.current_game.dealer_deck)
        cards = cards.replace('_',' ')
        try:
            if 'busts' in result:
                await self.client.send_message(message.channel, embed=get_embed(title='The dealer got busted! with %s total: ' % result.split(' ')[1], txt='\n{}\n'.format(cards)))
                try:
                    self.modify(message.author, int(self.game_bet*2))
                except OSError as e:
                    print(e.args[0])
                    return
                await self.client.send_message(message.channel, embed=get_embed(title='You won {}'.format(int(self.game_bet))))
            elif result == 'blackjack':
                await self.client.send_message(message.channel, embed=get_embed(title='The dealer got a blackjack!', txt='\n{}\n'.format(cards)))
                await self.client.send_message(message.channel, embed=get_embed(title='You lost {}'.format(int(self.game_bet))))
        except:
            if result > self.player_max:
                await self.client.send_message(message.channel, embed=get_embed(title='The dealer got higher than you! with %s total: ' % result, txt='\n{}\n'.format(cards)))
                await self.client.send_message(message.channel, embed=get_embed(title='You lost {}'.format(int(self.game_bet))))
            elif result == self.player_max:
                await self.client.send_message(message.channel, embed=get_embed(title='The dealer got the same points as you! with %s total: ' % result, txt='\n{}\n'.format(cards)))
                await self.client.send_message(message.channel, embed=get_embed(title='This game was a push!'))
                try:
                    self.modify(message.author, int(self.game_bet))
                except OSError as e:
                    print(e.args[0])
                    return
            else:
                await self.client.send_message(message.channel, embed=get_embed(title='you got more than the dealer! dealer\'s total points was %s: ' % result, txt='\n{}\n'.format(cards)))
                await self.client.send_message(message.channel, embed=get_embed(title='You won {}'.format(int(self.game_bet))))
                try:
                    self.modify(message.author, int(self.game_bet*2))
                except OSError as e:
                    print(e.args[0])
                    return
        self.in_game = False
        self.current_game = None
    @commands.command(pass_context = True)
    async def blackjack(self, ctx, bet : int):
        """Blackjack beta, after started game, type %hit or %stand"""
        message = ctx.message
        self.game_bet = bet
        if self.in_game:
            await self.client.send_message(message.channel, embed=get_embed(title='A Game is already in session, please wait'))
            return
        try:
            self.modify(message.author, int(self.game_bet)*-1)
        except OSError as e:
            print(e.args[0])
            return
        except TypeError as e:
            await self.client.send_message(message.channel, embed=get_embed(title="You don't have enough {}{}.".format(self.cur_p, self.cur_i)))
            return
        self.in_game = True
        self.started_by = message.author
        self.current_game = Blackjack()
        self.current_game.play('hit')
        self.current_game.play('hit')
        result = self.current_game.check_over()
        cards = ", ".join(self.current_game.player_deck)
        cards = cards.replace('_',' ')
        if result == 'blackjack':
            await self.client.send_message(message.channel, embed=get_embed(title='Blackjack!', txt='\n{}\n'.format(cards)))
            try:
                self.modify(message.author, int(self.game_bet*2.5))
            except OSError as e:
                print(e.args[0])
                return
            await self.client.send_message(message.channel, embed=get_embed(title='You won {}'.format(int(self.game_bet*1.5))))
            self.in_game = False
            self.current_game = None
            return
        else:
            await self.client.send_message(message.channel, embed=get_embed(title='Your cards are: ', txt='\n{} with {} total\n'.format(cards, result)))
            self.player_max = result
        await self.client.send_message(message.channel, embed=get_embed(title='The dealer\'s cards is:', txt='\n{} and a hole card\n'.format(self.current_game.dealer_deck[0].replace('_',' '))))
        
def setup(client):
    client.add_cog(Game(client))
