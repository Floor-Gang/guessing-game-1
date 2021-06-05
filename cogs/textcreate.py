# [ main cog for text creation ]
from discord.ext import commands
from tinydb import TinyDB,Query
import time
import discord

colors = {'red':0xFF0000,"green":0x00FF00,"yellow":0xFFFF00}


xdb=TinyDB("database.json")
currentdb=xdb.table("current",cache_size=30)


class Create(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 


    @commands.command() 
    async def text(self,ctx,typex,*,message):




def setup(bot):
    bot.add_cog(Create(bot))