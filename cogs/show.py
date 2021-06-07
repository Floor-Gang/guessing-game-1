# [ main cog for forceskip , hint ]
from discord.ext import commands
from tinydb import TinyDB,Query
import discord
import random
from cogs.helpers import footers,ua

xdb=TinyDB("database.json")
currentdb=xdb.table("current",cache_size=30)
pointsdb=xdb.table("points",cache_size=0)
colors = {'red':0xFF0000,"green":0x00FF00,"yellow":0xFFFF00}
ua=ua()

class Show(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 


    @commands.command(aliases=['show','hint'])
    @commands.cooldown(1, 60*2.5, commands.BucketType.channel)
    async def reveal(self,ctx):
        currentdb.clear_cache()
        search=currentdb.search(Query().channelid==ctx.channel.id) 
        footer=footers()
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
            try:
                wlist = await ctx.channel.webhooks()
            except:
                return await ctx.channel.send("The bot is missing permissions to create webhooks")
            if len(wlist) == 0:
                hook = await ctx.channel.create_webhook(name="guess10")
            else:
                boolxy=True
                for i in wlist:
                    if i.user==self.bot.user:
                        hook = i
                        boolxy=False
                        break
                if boolxy==True:
                    hook = await ctx.channel.create_webhook(name="guess10")
            return await hook.send("You have guessed all the answers! This is the final list of guesses.",embed=discord.Embed(
                title=search[0]['top10']['0'],
                description=desc,
                color=colors['green']
            ).set_footer(text=str(search[0]['counter'])+footer),username=ua[0],avatar_url=ua[1])

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
            try:
                wlist = await ctx.channel.webhooks()
            except:
                return await ctx.channel.send("The bot is missing permissions to create webhooks")
            if len(wlist) == 0:
                hook = await ctx.channel.create_webhook(name="guess10")
            else:
                boolxy=True
                for i in wlist:
                    if i.user==self.bot.user:
                        hook = i
                        boolxy=False
                        break
                if boolxy==True:
                    hook = await ctx.channel.create_webhook(name="guess10")
            return await hook.send(f"The hint was {tval.index(rand)+1}. {rand} and all the answers are done! This is the final list of guesses.",embed=discord.Embed(
                title=search[0]['top10']['0'],
                description=desc,
                color=colors['green']
            ).set_footer(text=str(search[0]['counter'])+footer),username=ua[0],avatar_url=ua[1])
        try:
            wlist = await ctx.channel.webhooks()
        except:
            return await ctx.channel.send("The bot is missing permissions to create webhooks")
        if len(wlist) == 0:
            hook = await ctx.channel.create_webhook(name="guess10")
        else:
            boolxy=True
            for i in wlist:
                if i.user==self.bot.user:
                    hook = i
                    boolxy=False
                    break
            if boolxy==True:
                hook = await ctx.channel.create_webhook(name="guess10")
        return await hook.send(f"{tval.index(rand)+1}. {rand}",embed=discord.Embed(
            title=search[0]['top10']['0'],
            description=desc,
            color=colors['green']
        ).set_footer(text=str(search[0]['counter'])+footer),username=ua[0],avatar_url=ua[1])
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
            try:
                wlist = await ctx.channel.webhooks()
            except:
                return await ctx.channel.send("The bot is missing permissions to create webhooks")
            if len(wlist) == 0:
                hook = await ctx.channel.create_webhook(name="guess10")
            else:
                boolxy=True
                for i in wlist:
                    if i.user==self.bot.user:
                        hook = i
                        boolxy=False
                        break
                if boolxy==True:
                    hook = await ctx.channel.create_webhook(name="guess10")
            footer=footers()
            await hook.send("You ended this game! This is the final list, with the ones not guessed in spoilers.",embed=discord.Embed(
                title=search[0]['top10']['0'],
                description=desc,
                color=colors['red'],
            ).set_footer(text=str(search[0]['counter'])+footer),username=ua[0],avatar_url=ua[1])
        pass



    @commands.command(aliases=["lb",'leaderboard','points'])
    async def rank(self,ctx):
        store=[]
        store2=[]
        store3=[]
        store4=[]
        for num,i in enumerate(sorted(list(pointsdb.all()), key=lambda k: k['points'], reverse=True)):
            if i["id"][1] == ctx.guild.id:
                store2.append(i)
        if len(store2)==0:
            return await ctx.send("No one has points yet in this server!")
        for num,i in enumerate(store2):
            store3.append(f"{num+1}. <@!{i['id'][0]}> - {i['points']}")
            if len(store3) == 10:
                store4.append(store3)
                store3=[]
        if len(store3)!=0:
            store4.append(store3)
        for i in store4:
            text=""
            for j in i:
                text = text + j + "\n"
            store.append(text)
        title = ctx.guild.name
        async def createbook(bot, ctx, title, pages, **kwargs):

            header = kwargs.get("header", "") # String
            results = kwargs.get("results", 0) # Int
            
            pagenum = 1

            def get_results():
                results_min = (pagenum - 1) * 8 + 1
                if pagenum == len(pages): results_max = results
                else: results_max = pagenum * 8
                return f"Showing {results_min} - {results_max} results out of {results}"

            pagemax = len(pages)
            if results:
                header = get_results()
                if len(pages) == 0: pagemax = 1

            embed = discord.Embed(title=title, description=f"{header}\n\n{pages[pagenum - 1]}", colour=0xF42F42)
            embed.set_footer(text=f"Page {pagenum}/{pagemax}", icon_url=ua[1])
            msg = await ctx.send(embed=embed)
            
            await msg.add_reaction("⬅️")
            await msg.add_reaction("➡")
            
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡"]
        
            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout = 60, check=check)
                    await msg.remove_reaction(reaction, user)
                    
                    if str(reaction.emoji) == "⬅️":
                        pagenum -= 1
                        if pagenum < 1: pagenum = len(pages)
                            
                    elif str(reaction.emoji) == "➡":
                        pagenum += 1
                        if pagenum > len(pages): pagenum = 1

                    header = get_results() if results else header
                    if str(reaction.emoji) == "⬅️" or str(reaction.emoji) == "➡":
                        embed = discord.Embed(title=title, description=f"{header}\n\n{pages[pagenum - 1]}", colour=0xF42F42)
                        embed.set_footer(text=f"Page {pagenum}/{len(pages)}", icon_url=ua[1])
                        await msg.edit(embed=embed)
                except:
                    header = get_results() if results else header
                    embed = discord.Embed(title="Bot Server Status", description=f"{header}\n\n{pages[pagenum - 1]}", colour=0xF42F42)
                    embed.set_footer(text=f"Request timed out", icon_url=ua[1])
                    await msg.edit(embed=embed)
                    break
        await createbook(self.bot,ctx,title,store)
        pass


def setup(bot):
    bot.add_cog(Show(bot))