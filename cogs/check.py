# [ main cog for points ]
import discord
from discord.ext import tasks , commands
from tinydb import TinyDB,Query
import time
from cogs.helpers import ua , endemotes
xdb=TinyDB("database.json")
currentdb=xdb.table("current",cache_size=0)
pointsdb=xdb.table("points",cache_size=30)
colors = {'red':0xFF0000,"green":0x00FF00,"yellow":0xFFFF00}

ua = ua()

class Check(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.check.start()

    @tasks.loop(minutes=2)
    async def check(self):
        currentdb.clear_cache()
        pointsdb.clear_cache()
        for search in currentdb.all():
            if search['start']+60*5 <= time.time() and search['current'] != False:
                currentdb.update({"current":False},Query().channelid==search['channelid'])
                gval=list(search['guessed'].values())
                desc=''
                c=1
                for i in gval:
                    if i == None:
                        try:
                            i=f"||{search['top10'][str(c)]}||"
                        except:
                            i=f"nothing here because no one added a {c} place"
                    desc=desc + '\n' + str(c) + '. ' + i
                    c+=1
                channel=self.bot.fetch_channel(search['channelid'])
                await channel.send(content=f"{endemotes()}",embed=discord.Embed(
                    title=search['top10']['0'],
                    description=desc,
                    color=colors['red']
                ).set_footer(text=str(search[0]['counter'])+" | You have run out of time! This is the final list, with the ones not guessed in spoilers."),username=ua[0],avatar_url=ua[1])
            else:
                pass
        pass
        for point in pointsdb.all():
            if point["points"] > 10000 and point['id'][1]==644750155030986752:
                guild=self.bot.get_guild(644750155030986752)
                role = discord.utils.get(guild.roles, id=847824735739445278)
                try:
                    guild.get_member(point["userid"]).add_role(role)
                except:
                    pass
                pass




def setup(bot):
    bot.add_cog(Check(bot))