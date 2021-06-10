# [ main cog for on_message and !!start ]
import discord
from discord.ext import commands
from tinydb import TinyDB,Query
import aiohttp
from cogs.helpers import purify , actual_prefix,prefix_for_guesses , ua , footers , endemotes
import random
import time
from tinydb.operations import increment

xdb=TinyDB("database.json")
topdb=xdb.table("topten",cache_size=30)
currentdb=xdb.table("current",cache_size=0)
pointsdb=xdb.table("points",cache_size=0)
dmdb = xdb.table("dm",cache_size=0)

ua=ua()

actual_prefix=actual_prefix()
prefix_for_guesses=prefix_for_guesses()
colors = {'red':0xFF0000,"green":0x00FF00,"yellow":0xFFFF00}


class Guess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 



    @commands.Cog.listener()
    async def on_message(self,msg):
        if msg.author == self.bot.user: 
            return
        if msg.guild is None and msg.author != self.bot.user:
            dmsearch = dmdb.search(Query().userid==msg.author.id)
            if len(dmsearch) != 0 and dmsearch[0]["current"]==True:
                return await msg.reply("You are blocked from sending DMs and Reports.")
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url('https://discord.com/api/webhooks/847191143129153546/ik2wF1P69DUFPqwaFmdcdOyRkmy7Vkem_jHGUR9ttaDFm7mDxy_9v-tkx0iKhEasVr3j', adapter=discord.AsyncWebhookAdapter(session))
                nmsg = f"**From: {msg.author.name}#{msg.author.discriminator}**({msg.author.id})\n**Content:**\n{msg.content}"
                await webhook.send(nmsg)
                return 
        bucket1 = commands.CooldownMapping.from_cooldown(15.0, 30.0, commands.BucketType.channel).get_bucket(msg)
        retry_after = bucket1.update_rate_limit()
        if retry_after:
            try:
                await msg.channel.edit(slowmode_delay=5)
            except:
                pass
        bucket2 = commands.CooldownMapping.from_cooldown(0.0, 10.0, commands.BucketType.channel).get_bucket(msg)
        retry_after = bucket2.update_rate_limit()
        if retry_after:
            try:
                await msg.channel.edit(slowmode_delay=0)
            except:
                pass


        lx=["broken bot",'bot broken','rigged','broken','sucks']
        for i in lx:
            if purify(msg.content.lower()).find(i) >= 0:
                lst=['https://tenor.com/view/cry-about-it-cry-about-it-meme-gif-20184012']
                await msg.reply(random.choice(lst))
                break
        if msg.content.startswith(prefix_for_guesses) or msg.content.startswith(actual_prefix):
            try:
                wlist = await msg.channel.webhooks()
            except:
                return await msg.channel.send("The bot is missing permissions to create webhooks")
            if len(wlist) == 0:
                hook = await msg.channel.create_webhook(name="guess10")
            else:
                boolxy=True
                for i in wlist:
                    if i.user==self.bot.user:
                        hook = i
                        boolxy=False
                        break
                if boolxy==True:
                    hook = await msg.channel.create_webhook(name="guess10")
            footer = footers()

        if msg.content.startswith(f"{actual_prefix}start"):
            currentdb.clear_cache()
            search=currentdb.search(Query().channelid==msg.channel.id)

            if len(search)!=0:
                if search[0]['current']==True:
                    gval=list(search[0]['guessed'].values())
                    desc=''
                    c=1
                    for i in gval:
                        if i == None:
                            try:
                                i=""
                            except:
                                i=""
                        desc=desc + '\n' + str(c) + '. ' + i
                        c+=1
                    
                    return await hook.send(f"A game is already in progress! Theres {int(search[0]['start']+60*5 - time.time())}s left for it to end! Use {actual_prefix}new to vote to start a new one, or {actual_prefix}hint for an answer (once per game)",embed=discord.Embed(
                        title=search[0]['top10']['0'],
                        description=desc,
                        color=colors['yellow']
                    ).set_footer(text=str(search[0]['counter'])+footer),username=ua[0],avatar_url=ua[1])
            '''rng=random.choice([1,2,3])
            if rng==2:
                rand=random.choice(topdb.all())
            else:
                rand=random.choice(list(topdb.all())[200:])'''
            rand=random.choice(list(topdb.all()))
            print(rand)
            await hook.send(embed=discord.Embed(
                title=rand['top10']['0'],
                description='1.\n2.\n3.\n4.\n5.\n6.\n7.\n8.\n9.\n10.'
            ).set_footer(text=str(rand['counter'])+footer),username=ua[0],avatar_url=ua[1])
            currentdb.upsert({'current':True,'top10':rand['top10'],'start':time.time(),'guildid':msg.guild.id,'channelid':msg.channel.id,'userid':msg.author.id,'guessed':{'1':None,'2':None,'3':None,'4':None,'5':None,'6':None,'7':None,'8':None,'9':None,'10':None},'endcount':0,"counter":rand["counter"]},Query().channelid==msg.channel.id)
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url('https://discord.com/api/webhooks/847130597071519754/Wv235UB6fZc3bB-2R1pl33KZNud_NJBK0f5DZI1kJ82iYtRnDC4-PzquIU_7pOyf6U8b', adapter=discord.AsyncWebhookAdapter(session))
                await webhook.send(rand)
                return 
            
        search=currentdb.search(Query().channelid==msg.channel.id)
        if len(search)==0:
            return 
        if search[0]['current']==False:
            return 
        if None not in list(search[0]['guessed'].values()) and search[0]['current'] != False:
            currentdb.update({"current":False},Query().channelid==msg.channel.id)
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
            
            return await hook.send(f"{endemotes()} You have guessed all the answers! This is the final list of guesses. {endemotes()}",embed=discord.Embed(
                title=search[0]['top10']['0'],
                description=desc,
                color=colors['green']
            ).set_footer(text=str(search[0]['counter'])+footer),username=ua[0],avatar_url=ua[1])
        if msg.content.startswith(prefix_for_guesses):
            search=currentdb.search(Query().channelid==msg.channel.id)
            if len(search)==0:
                return 
            if search[0]['current']==False:
                return 
            message=msg.content.replace(prefix_for_guesses,"",1)
            if search[0]['start']+60*5 <= time.time() and search[0]['current'] != False:
                currentdb.update({"current":False},Query().channelid==msg.channel.id)
                gval=list(search[0]['guessed'].values())
                desc=''
                c=1
                for i in gval:
                    if i == None:
                        i=f"||{search[0]['top10'][str(c)]}||"
                    desc=desc + '\n' + str(c) + '. ' + i
                    c+=1
                
                return await hook.send(f"{endemotes()} You have run out of time! This is the final list, with the ones not guessed in spoilers. {endemotes()}",embed=discord.Embed(
                    title=search[0]['top10']['0'],
                    description=desc,
                    color=colors['red']
                ).set_footer(text=str(search[0]['counter'])+footer),username=ua[0],avatar_url=ua[1])

            top10n=list(search[0]['top10'].values())
            top10n.pop(0)
            top10x=list(map(str.lower, top10n))
            toptemp=[]
            for i in top10x:
                i=purify(i)
                toptemp.append(i)
            top10x=toptemp
            boolx=False
            listw=['the','pokemon','is','in','dank','meme']
            for i in top10x:
                if len(purify(message.lower())) < 3 and purify(message.lower()) != i:
                    boolx=False
                    break
                if purify(message.lower()) in listw:
                    boolx=False
                    break
                t=i.find(purify(message.lower()))
                if t>=0:
                    boolx=True
                    break

            if boolx:
                guessed=search[0]['guessed']
                listg=list(guessed.values())
                listn=[]
                for i in listg:
                    if i == None:
                        pass
                    else:
                        listn.append(purify(i.lower()))
                chec=[]
                for i in list(map(str.lower, listn)):
                    tempint = i.find(purify(message.lower()))
                    if tempint >= 0:
                        chec.append(i)

                top10=search[0]['top10']
                listt=list(top10.values())
                listtn=[]
                for i in listt:
                    if i == None:
                        pass
                    else:
                        listtn.append(purify(i.lower()))
                chect=[]
                for i in list(map(str.lower, listtn)):
                    tempint = i.find(purify(message.lower()))
                    if tempint >= 0:
                        chect.append(i)

                if len(chec) >= len(chect):
                    
                    return await hook.send("Already guessed!",username=ua[0],avatar_url=ua[1])

                for num,i in enumerate(top10x):
                    if purify(i.lower()).find(purify(message.lower())) >= 0:
                        guessed[str(num+1)]=top10n[num]+f" (Guessed by: <@{msg.author.id}>)"
                psearch=pointsdb.search(Query().id==[msg.author.id,msg.guild.id])
                if len(psearch)==0:
                    pointsdb.insert({"id":(msg.author.id,msg.guild.id),"points":0})
                else:
                    pointsdb.update(increment('points'),Query().id==(msg.author.id,msg.guild.id))

                currentdb.update({'guessed':guessed},Query().channelid==msg.channel.id)

                if None not in list(guessed.values()) and search[0]['current'] != False:
                    currentdb.update({"current":False},Query().channelid==msg.channel.id)
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
                    
                    return await hook.send(f"{endemotes()} You have guessed all the answers! This is the final list of guesses. {endemotes()}",embed=discord.Embed(
                        title=search[0]['top10']['0'],
                        description=desc,
                        color=colors['green']
                    ).set_footer(text=str(search[0]['counter'])+footer),username=ua[0],avatar_url=ua[1])
                gval=list(guessed.values())
                desc=''
                c=1
                for i in gval:
                    if i == None:
                        i=''
                    desc=desc + '\n' + str(c) + '. ' + i
                    c+=1
                                
                return await hook.send(embed=discord.Embed(
                        title=search[0]['top10']['0'],
                        description=desc,
                        color=colors['green']
                    ).set_footer(text=str(search[0]['counter'])+footer),username=ua[0],avatar_url=ua[1])
            else:
                await hook.send(content=f"<@{msg.author.id}> Wrong answer!",username=ua[0],avatar_url=ua[1])
                
        
        
        
def setup(bot):
    bot.add_cog(Guess(bot))