import discord, re
import urllib.request, urllib.error, urllib.parse
from config.config import config, get_response, get_api, get_embed
from discord.ext import commands
from time import strftime, gmtime
from gamelocker.strings import pretty


class Vainglory:
    """VG cog for Koshka bot"""
    def __init__(self, client):
        self.client = client
        self.config = config('koshka.db')

    
    @commands.command(pass_context=True)
    async def lastmatch(self, ctx, user : str, region : str):
        """Get the last casual/ranked match results"""
        message = ctx.message
        tmp = await self.client.send_message(message.channel, embed=get_embed(title='Searching...'))
        try:
            response = get_response( user, region)
        except urllib.error.HTTPError as weberror:
            if weberror.code == 500:
                await self.client.edit_message(tmp, embed=get_embed(title='No such player: {}.'.format(user)))
            else:
                await self.client.edit_message(tmp, embed=get_embed(title='Cannot connect to vain.gg server. Use *random instead.'))
            return
        except ValueError:
            await self.client.send_message(message.channel, embed=get_embed(title='Not a valid region. Valid regions are: na, sea, sa, ea, eu.'))
            return
        title = "Last match results for player {}:".format(user)
        match = response['latestMatches'][0]
        if match['casual']:
            match['matchType'] = 'casual'
        else: match['matchType'] = 'ranked'
        match['startTime']=strftime("%a %d %b %Y %H:%M:%S GMT", gmtime(match['creationTime'] / 1000.0))
        match['duration']=float("%.2f"%(match['matchDuration']/60))
        roster = match['rosters']
        txt=''
        txt += "MatchType: {matchType}.\nStartTime: {startTime}.\nDuration: {duration}.\nRegion: {region}\n".format(**match)
        await self.client.send_message(message.channel, embed=get_embed(title=title, txt=txt)); txt=''
        for team in roster:
            txt += """\nSide: {side}.\nTurretsDestroyed: {turretKills}.\nTurretsRemaining: {turretsRemaining}.
            \nTeamGold: {gold}.\nAced: {acesEarned}.\nTotalHeroKills: {heroKills}.\nKrakenCaptures: {krakenCaptures}.\nPARTICIPANTS:\n""".format(**team)
            await self.client.send_message(message.channel, embed=get_embed(title=title, txt=txt)); txt=''
            for player in team['participants']:
                player['hero']=player['championDto']['cleanName']
                player['heroRole']=player['championDto']['role']
                player['iconUrl']=player['championDto']['iconUrl']
                player['farm']=int(player['farm'])
                player['name']=player['player']['name']
                player['KDA']="%s / %s / %s"%(player['kills'],player['deaths'],player['assists'])
                txt += """Name: {name}.\nHero: {hero}.\nRole: {heroRole}.\nHeroPic: {iconUrl}.\nSkin: {skinKey}.\nfarm: {farm}.
                \nKDA: {KDA}\nGoldMineCaptures: {goldMineCaptures}.\nCrystalMineCaptures: {crystalMineCaptures}.
                \nWentAfk: {wentAfk}.\nWinner: {winner}.\nFinalBuild: \n""".format(**player)
                for i, item in enumerate(player['matchItems']):
                    item['itemName']=item['itemDto']['cleanName']
                    item['itemIcon']=item['itemDto']['iconUrl']
                    item['i']=i+1
                    txt += "{i}.{itemName}.\n".format(**item)
                await self.client.send_message(message.channel, embed=get_embed(title=title, txt=txt)); txt=''
                
    @commands.command(pass_context=True)
    async def userstats(self, ctx, user : str, region : str):
        """Gets a better and more complete stats of an user tracked from Feb 1"""
        message = ctx.message
        tmp = await self.client.send_message(message.channel, embed=get_embed(title='Searching...'))
        try:
            response = get_response(user, region)
        except urllib.error.HTTPError as weberror:
            if weberror.code == 500:
                await self.client.edit_message(tmp, embed=get_embed(title='No such player: {}.'.format(user)))
            else:
                await self.client.edit_message(tmp, embed=get_embed(title='Cannot connect to vain.gg server. Use *random instead.'))
            return
        except ValueError:
            await self.client.send_message(message.channel, embed=get_embed(title='Not a valid region. Valid regions are: na, sea, sa, ea, eu.'))
            return
        response.pop('latestMatches')
        response.pop('roleData')
        favHero=", ".join([he['championDto']['cleanName'] for he in response['championData']])
        st=response['lifetimeStatistics']
        TR=st['totalRankedGamesPlayedInSeconds']/60
        TC=st['totalCasualGamesPlayedInSeconds']/60
        TP=st['totalTimePlayedInSeconds']/60
        txt = """Name: {name}.\nRegion: {region}.\nWins: {wins}.\nLosses: {losses}.\nWinStreak: {winStreak}.\nLossStreak: {lossStreak}.\nWinRate: {winRate}%.\nLifetimeGold: Too Much to Count.
                \nTotalCasualGamesWon: {totalCasualGamesWon}/{totalCasualGames}.\nTotalRankedGamesWon: {totalRankedGamesWon}/{totalRankedGames}.\nTotalGamesWon: {totalGamesWon}/{totalGames}.
                \nTotalRankedGamesPlayed: {totalRankedGamesPlayed:.2f} mins.\nTotalCasualGamesPlayed: {totalCasualGamesPlayed:.2f} mins.\nTotalTimePlayed: {totalTimePlayed:.2f} mins.
                \nFavorite Heros: {favHero}.\n""".format(favHero=favHero, totalRankedGamesPlayed=TR, totalCasualGamesPlayed=TC, totalTimePlayed=TP, **response,**response['lifetimeStatistics'])
        await self.client.send_message(message.channel, embed=get_embed(title='Statistics from Jan 27nd for: ', txt=txt))

    @commands.command(pass_context=True)
    async def stats(self, ctx, user : str):
        """Gets the basic stats of an user"""
        message=ctx.message
        api=get_api()
        tmp = await self.client.send_message(message.channel, embed=get_embed(title='Searching...'))
        try:
            m = api.matches({"update":True, "filter[playerNames]": user})
        except:
            await self.client.edit_message(tmp, embed=get_embed(title='No such player: {}.'.format(user)))
            return
        for i in m[0].rosters:
            for j in i.participants:
                if j.player.name == user:
                    if int(j.stats['karmaLevel'])==1:
                        karma = 'Good Karma.'
                    else: karma = 'Great Karma.'
                    await self.client.edit_message(tmp, embed=get_embed(title="Player: {}".format(user),txt='''\n\nWins: {wins}.\nLevel: {level}.
                                                                       Win Streak: {winStreak}.\nLose Streak: {lossStreak}.\nKarma: {karma}.'''.format(karma=karma, **j.stats,**j.player.stats)))


    @commands.command(pass_context=True)
    async def random(self, ctx, user : str):
        """Gets a random match results of a user"""
        message=ctx.message
        api=get_api()
        try:
            m = api.matches({"update":True, "filter[playerNames]": user})
        except:
            await self.client.send_message(message.channel, embed=get_embed(title='No such player: {}.'.format(user)))
            return
        match=m[0]
        for i in match.rosters:
            for j in i.participants:
                if j.player.name == user:
                    if j.stats['wentAfk']:
                        afk = 'yes'
                    else: afk = 'no'
                    if j.stats['winner'] == 'True':
                        win = "victory"
                    else: win = 'lost'
                    items = ", ".join(j.stats.pop('items'))
                    print(match.stats)
                    await self.client.send_message(message.channel, embed=get_embed(title='Random Game(Casual/Ranked) Results for Player: {}'.format(user), txt=
                                    '''\n\nHero: {hero}.\nSkin: {skinKey}.\nKDA: {kills}/{deaths}/{assists}.\nMinion Farm: {minionKills}.\nKrakens Captured: {krakenCaptures}.
                                    \nCrystal Mines Captured: {crystalMineCaptures}.\nGold Mines Captured: {goldMineCaptures}.\nTurrets Destroyed: {turretCaptures}.
                                    \nAfk: {afk}.\nResult: {endGameReason}.\nQueue: {queue}.\nMatch Duration: {duration:.2f} Minutes.\nGame Played on: {createdAt}.
                                    \nFinal Items Build: {items}.'''.format(hero=pretty(j.actor),afk=afk, items=items, duration = int(match.duration)/60, **match.stats, **j.stats)))
        title="Match Comp:"
        text=""
        for team in range(2):
            text += '\nTeam %i:\n' %(team+1)
            for player in range(3):
                name = match.rosters[team].participants[player].player.name
                hero = pretty(match.rosters[team].participants[player].actor)
                kills = match.rosters[team].participants[player].stats["kills"]
                deaths = match.rosters[team].participants[player].stats["deaths"]
                assists = match.rosters[team].participants[player].stats["assists"]
                text += "Player: {}, Hero: {}  {}/{}/{}\n".format(name, hero, kills, deaths, assists)
        await self.client.send_message(message.channel, embed=get_embed(title=title, txt=text))


def setup(client):
    client.add_cog(Vainglory(client))
