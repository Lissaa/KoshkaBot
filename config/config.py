import sqlite3, json, discord, gamelocker
import urllib.request, urllib.error, urllib.parse
from discord.ext import commands

class config:
    def __init__(self, location):
        self.connection = sqlite3.connect(location)
        self.cursor = self.connection.cursor()

    def change(self, table_name, row_id, column_name, data):
        self.get_table(table_name, column_name=column_name, row_id=int(row_id))
        self.cursor.execute("UPDATE {0} SET {1} = \"{2}\" WHERE Id = {3}".format(table_name, column_name, data, int(row_id)))
        self.connection.commit()

    def get_sorted(self, table_name, sort_by):
        try:
            table = self.cursor.execute("SELECT * FROM %s ORDER BY %s DESC" % (table_name, sort_by))
        except Exception as e:
            raise OSError(e.args[0])
        table = list(table)
        if table == []:
            raise ValueError("No Data Found")
        return table
        
    def get_table(self, table_name, get_all = False, **stuff):
        """Possible keys: column_name str, row_id int, get_row bool, change_to str"""
        column_name = stuff.pop('column_name', None)
        row_id = stuff.pop('row_id', 1)
        get_row = stuff.pop('get_row', False)
        try:
            if get_all:
                table = self.cursor.execute("SELECT * FROM %s" % table_name)
            elif get_row:
                table = self.cursor.execute("SELECT %s FROM %s" % (column_name, table_name))
            else:
                table = self.cursor.execute("SELECT %s FROM %s WHERE Id = %i" % (column_name, table_name, row_id))
        except Exception as e:
            raise OSError(e.args[0])
        table = list(table)
        if table == []:
            raise ValueError("No Data Found With This Role Id")
        return table

    def make_row(self, table_name, values : tuple):
        val_str=""
        for value in values:
            if isinstance(value, str):
                val_str+="\"{}\"".format(value)
            else:
                val_str+="{}".format(value)
            if value!=values[-1]:
                val_str+=','
        try:
            self.cursor.execute("INSERT INTO {} VALUES ({})".format(table_name, val_str))
        except Exception as e:
            raise OSError(e.args[0])
        self.connection.commit()
    
class check:
    
    def owner_only():
        return commands.check(lambda ctx: check.is_owner_check(ctx.message))

    def is_owner_check(message):
        return message.author.id in ['139069549692715008','95280508384063488']

def get_response(user, region):
    if region == 'sea': region = 'sg'
    if region not in ('na','sg','sa','eu','ea'):
        raise ValueError("Invalid Region")
    url = 'http://ardan.vain.gg/api/v1/player/byName/update?playerName=%s&shard=%s'%(user, region)
    username = "vain"
    password = "om4YsiEtCDHP1Hylp9vP"
    con = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    con.add_password(None, url, username, password)
    urllib.request.install_opener(urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(con)))
    req = urllib.request.Request(url)
    return json.loads(urllib.request.urlopen(req).read())

def get_clever(cs, msg):
    if not cs: url = 'http://www.cleverbot.com/getreply?key=28c8b62b873cc57504aca8befe0bbeeb&input=%s'%(msg)
    else: url = 'http://www.cleverbot.com/getreply?key=28c8b62b873cc57504aca8befe0bbeeb&input=%s&cs=%s'%(msg, cs)
    req = urllib.request.Request(url)
    return json.loads(urllib.request.urlopen(req).read())
def get_api():
    APIKEY = "aaa.bbb.ccc"
    return gamelocker.Gamelocker(APIKEY).Vainglory()

def get_embed(title=None, txt=None):
    if title and txt:
        embed=discord.Embed(title=title, description=txt, colour=discord.Colour.red())
    elif title:
        embed=discord.Embed(title=title, colour=discord.Colour.red())
    elif txt:
        embed=discord.Embed(description=txt, colour=discord.Colour.red())
    else: embed=None
    return embed
