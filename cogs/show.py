# [ main cog for forceskip , hint ]
from discord.ext import commands
from tinydb import TinyDB,Query
import discord
import random


xdb=TinyDB("database.json")
currentdb=xdb.table("current",cache_size=30)
colors = {'red':0xFF0000,"green":0x00FF00,"yellow":0xFFFF00}


class Show(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 


    @commands.command(aliases=['show','hint'])
    @commands.cooldown(1, 60*2.5, commands.BucketType.channel)
    async def reveal(self,ctx):
        currentdb.clear_cache()
        search=currentdb.search(Query().channelid==ctx.channel.id) 
        if None not in list(search[0]['guessed'].values()) and search[0]['current'] != False:
            currentdb.update({"current":False},Query().channelid==ctx.channel.id)
            gval=list(search[0]['guessed'].values())
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
            return await ctx.reply("You have guessed all the answers! This is the final list of guesses.",embed=discord.Embed(
                title=search[0]['top10']['0'],
                description=desc,
                color=colors['green']
            ).set_footer(text=search[0]['counter']))

        if search[0]['current']==False:
            return await ctx.send("There is no game going on in this channel right now")
        gval=list(search[0]['guessed'].values())
        tval=list(search[0]['top10'].values())
        tvalx=search[0]['top10']
        tval.pop(0)
        del tvalx["0"]
        for num,i in enumerate(gval):
            if i!=None:
                try:
                    del tvalx[str(num+1)]
                except Exception as e:
                    print(e)
        tvalx=list(tvalx.values())

        rand=random.choice(tvalx)
        guessed={}
        for j in range(0,10):
            if j == tval.index(rand):
                guessed[str(j+1)]=rand
            else:
                guessed[str(j+1)] = gval[j]
        currentdb.update({'guessed':guessed},Query().channelid==ctx.channel.id)
        desc=''
        c=1
        for i in guessed.values():
            if i == None:
                i=""
            desc=desc + '\n' + str(c) + '. ' + i
            c+=1
        search=currentdb.search(Query().channelid==ctx.channel.id)
        if None not in list(search[0]['guessed'].values()) and search[0]['current'] != False:
            currentdb.update({"current":False},Query().channelid==ctx.channel.id)
            gval=list(search[0]['guessed'].values())
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
            return await ctx.reply(f"The hint was {tval.index(rand)+1}. {rand} and all the answers are done! This is the final list of guesses.",embed=discord.Embed(
                title=search[0]['top10']['0'],
                description=desc,
                color=colors['green']
            ).set_footer(text=search[0]['counter']))
        return await ctx.reply(f"{tval.index(rand)+1}. {rand}",embed=discord.Embed(
            title=search[0]['top10']['0'],
            description=desc,
            color=colors['green']
        ).set_footer(text=search[0]['counter']))
        pass






    @commands.command(aliases=['forceend','kill','killswitch','end'])
    @commands.has_permissions(manage_messages=True)
    async def forcenew(self,ctx):
        currentdb.clear_cache()
        search=currentdb.search(Query().channelid==ctx.channel.id)
        if search[0]['current']!=False:
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
            await channel.send("You ended this game! This is the final list, with the ones not guessed in spoilers.",embed=discord.Embed(
                title=search[0]['top10']['0'],
                description=desc,
                color=colors['red'],
            ).set_footer(text=search[0]['counter']))
        pass



def setup(bot):
    bot.add_cog(Show(bot))