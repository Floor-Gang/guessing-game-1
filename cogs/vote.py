# [ main cog for vote , forcenew , on_reaction_add for vote ]
from discord.ext import commands
from tinydb import TinyDB,Query
import time
import discord

colors = {'red':0xFF0000,"green":0x00FF00,"yellow":0xFFFF00}


xdb=TinyDB("database.json")
currentdb=xdb.table("current",cache_size=30)


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 



    @commands.command(aliases=['forcestart','new','cancel','skip'])
    async def vote(self,ctx):
        search=currentdb.search(Query().channelid==ctx.channel.id)
        if search[0]['current']!=True:
            return await ctx.send("No match going on.")
        if search[0]['start']+60*5 - time.time() < 35:
            timeleft=int(search[0]['start']+60*5) - time.time()
            return await ctx.send(f"There is only {int(timeleft)}s left, wait thx")
            pass
        if search[0]['endcount'] != 0:
            return await ctx.send("There is already a vote going on.")
        m=await ctx.send("React with <:kms:847138153189343273> to end the match and start another.")
        await m.add_reaction("<:kms:847138153189343273>")


    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,user):
        if user==self.bot.user:
            return
        try:
            r=reaction.emoji.id
        except:
            return
        if r==847138153189343273:
            if reaction.message.author.id==846586533439995914:
                search=currentdb.search(Query().channelid==reaction.message.channel.id)
                if search[0]['current']!=False:
                    currentdb.update({'endcount':search[0]['endcount']+1},Query().channelid==search[0]['channelid'])
                    if search[0]['endcount']+1 >= 3:
                        currentdb.update({"current":False},Query().channelid==search[0]['channelid'])
                        gval=list(search[0]['guessed'].values())
                        desc=''
                        c=1
                        for i in gval:
                            if i == None:
                                try:
                                    i=f"||{search[0]['top10'][str(c)]}||"
                                except:
                                    i=f"nothing here because no one added a {c} place"
                            desc=desc + '\n' + str(c) + '. ' + i
                            c+=1
                        channel=self.bot.get_channel(search[0]['channelid'])
                        await channel.send("You have voted to end! This is the final list, with the ones not guessed in spoilers.",embed=discord.Embed(
                            title=search[0]['top10']['0'],
                            description=desc,
                            color=colors['red'],
                        ).set_footer(text=search[0]['counter']))
            pass
        pass



def setup(bot):
    bot.add_cog(Vote(bot))