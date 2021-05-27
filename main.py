import web
import discord
from discord.ext import commands,tasks
import os
from tinydb import TinyDB,Query
import random
import time
import aiohttp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import asyncio


prefix_for_guesses=".."
actual_prefix="!!"
bot = commands.Bot(command_prefix=actual_prefix,
intents=discord.Intents.all())
client = bot

bot.remove_command("help")

xdb=TinyDB("database.json")

topdb=xdb.table("topten",cache_size=30)
currentdb=xdb.table("current",cache_size=30)
dmdb=xdb.table("dm",cache_size=30)
def main():
    colors = {'red':0xFF0000,"green":0x00FF00,"yellow":0xFFFF00}
    @bot.event
    async def on_ready():
        check.start()
        print("started")

    @bot.command(aliases=['show','hint'])
    @commands.cooldown(1, 60*2.5, commands.BucketType.channel)
    async def reveal(ctx):
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

    @bot.command()
    async def add(ctx,*,message):
        if ctx.author.id != 602569683543130113 and ctx.author.id!=200621124768235521:
            return
        '''if link != None:
            listx=getlist(link)
            title=listx.pop(0)
            try:
                dictx={0:title}
                for i,value in enumerate(listx):
                    dictx[i+1]=value
                topdb.insert({'counter':len(topdb.all())+1,"top10":dictx})
                await ctx.send(f"Added {title} with {listx}")
            except Exception as e:
                await ctx.send(e)
        else:'''
        message=message.split('\n')
        title=message.pop(0)
        dictx={"0":title}
        if len(message) != 10:
            return await ctx.send("List doesnt have 10 values exactly")
        for num,i in enumerate(message):
            i=i.strip(f"{num+1}. ")
            dictx[str(num+1)]=i
        print(dictx)
        topdb.upsert({'count':len(topdb.all())+1,"top10":dictx},Query().top10==dictx)
        await ctx.send("Added")

    @bot.command(aliases=['forcestart','new'])
    async def vote(ctx):
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

        
        

    @bot.command()
    async def help(ctx):
        await ctx.send(embed=discord.Embed(
            title="get help",
            description=f"Use `{actual_prefix}start` to start a game in any channel.\nUse `{prefix_for_guesses}guess` to guess during a game.\nUse {actual_prefix}new to Vote to start a new game.\nUse {actual_prefix}hint for one answer, can be used once per game."
        ))
        pass


    @bot.event
    async def on_message(msg):
        if msg.author == bot.user: 
            await client.process_commands(msg)
            return
        if msg.guild is None and msg.author != bot.user:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url('https://discord.com/api/webhooks/847191143129153546/ik2wF1P69DUFPqwaFmdcdOyRkmy7Vkem_jHGUR9ttaDFm7mDxy_9v-tkx0iKhEasVr3j', adapter=discord.AsyncWebhookAdapter(session))
                nmsg = f"**From: {msg.author.name}#{msg.author.discriminator}**({msg.author.id})\n**Content:**\n{msg.content}"
                await webhook.send(nmsg)
                return await client.process_commands(msg)
        if msg.channel.id==846713646888517652 and msg.content.lower() in ["broken bot",'bot broken','rigged','broken','sucks']:
            lx=["broken bot",'bot broken','rigged','broken','sucks']
            for i in lx:
                if purify(msg.content.lower()).find(i):
                    lst=['https://tenor.com/view/cry-about-it-cry-about-it-meme-gif-20184012']
                    await msg.reply(random.choice(lst))
                    break
        if msg.content.startswith(f"{actual_prefix}start"):
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
                    await client.process_commands(msg)
                    return await msg.reply(f"A game is already in progress! Theres {int(search[0]['start']+60*5 - time.time())}s left for it to end! Use {actual_prefix}new to vote to start a new one, or {actual_prefix}hint for an answer (once per game)",embed=discord.Embed(
                        title=search[0]['top10']['0'],
                        description=desc,
                        color=colors['yellow']
                    ).set_footer(text=search[0]['counter']))

            rand=random.choice(topdb.all())
            print(rand)
            if msg.channel.id!=846713646888517652 and msg.channel.id!=715244478356652083:
                if len(search)!=0:
                    if search[0]['start'] > time.time()+15:
                        await client.process_commands(msg)
                        timeleft=time.time()+15-search[0]['start']
                        return await msg.channel.send(f'Wait {timeleft}')
            await msg.channel.send(embed=discord.Embed(
                title=rand['top10']['0'],
                description='1.\n2.\n3.\n4.\n5.\n6.\n7.\n8.\n9.\n10.'
            ).set_footer(text=rand['counter']))
            currentdb.upsert({'current':True,'top10':rand['top10'],'start':time.time(),'channelid':msg.channel.id,'userid':msg.author.id,'guessed':{'1':None,'2':None,'3':None,'4':None,'5':None,'6':None,'7':None,'8':None,'9':None,'10':None},'endcount':0,"counter":rand["counter"]},Query().channelid==msg.channel.id)
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url('https://discord.com/api/webhooks/847130597071519754/Wv235UB6fZc3bB-2R1pl33KZNud_NJBK0f5DZI1kJ82iYtRnDC4-PzquIU_7pOyf6U8b', adapter=discord.AsyncWebhookAdapter(session))
                await webhook.send(rand)
                return await client.process_commands(msg)
            await client.process_commands(msg)
        search=currentdb.search(Query().channelid==msg.channel.id)
        if len(search)==0:
            return await client.process_commands(msg)
        if search[0]['current']==False:
            return await client.process_commands(msg)
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
            await client.process_commands(msg)
            return await msg.channel.send("You have guessed all the answers! This is the final list of guesses.",embed=discord.Embed(
                title=search[0]['top10']['0'],
                description=desc,
                color=colors['green']
            ).set_footer(text=search[0]['counter']))
        if msg.content.startswith(prefix_for_guesses):
            search=currentdb.search(Query().channelid==msg.channel.id)
            if len(search)==0:
                return await client.process_commands(msg)
            if search[0]['current']==False:
                return await client.process_commands(msg)
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
                await client.process_commands(msg)
                return await msg.channel.send("You have run out of time! This is the final list, with the ones not guessed in spoilers.",embed=discord.Embed(
                    title=search[0]['top10']['0'],
                    description=desc,
                    color=colors['red']
                ).set_footer(text=search[0]['counter']))

            top10n=list(search[0]['top10'].values())
            top10n.pop(0)
            top10x=list(map(str.lower, top10n))
            toptemp=[]
            for i in top10x:
                i=purify(i)
                toptemp.append(i)
            top10x=toptemp
            boolx=False
            listw=['the','pokemon','is','in']
            for i in top10x:
                if len(purify(message.lower())) < 3:
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
                    await client.process_commands(msg)
                    return await msg.reply("Already guessed!")
                for num,i in enumerate(top10x):
                    if purify(i.lower()).find(purify(message.lower())) >= 0:
                        guessed[str(num+1)]=top10n[num]+f" (Guessed by: <@{msg.author.id}>)"

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
                    await client.process_commands(msg)
                    return await msg.channel.send("You have guessed all the answers! This is the final list of guesses.",embed=discord.Embed(
                        title=search[0]['top10']['0'],
                        description=desc,
                        color=colors['green']
                    ).set_footer(text=search[0]['counter']))
                gval=list(guessed.values())
                desc=''
                c=1
                for i in gval:
                    if i == None:
                        i=''
                    desc=desc + '\n' + str(c) + '. ' + i
                    c+=1
                await client.process_commands(msg)                
                return await msg.reply(embed=discord.Embed(
                        title=search[0]['top10']['0'],
                        description=desc,
                        color=colors['green']
                    ).set_footer(text=search[0]['counter']))
            else:
                await msg.add_reaction("<a:oop:846648466859229234>")
                await client.process_commands(msg)
        await client.process_commands(msg)


    @bot.event
    async def on_reaction_add(reaction,user):
        if user==bot.user:
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
                    if search[0]['endcount'] >= 3:
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
                        channel=client.get_channel(search[0]['channelid'])
                        await channel.send("You have voted to end! This is the final list, with the ones not guessed in spoilers.",embed=discord.Embed(
                            title=search[0]['top10']['0'],
                            description=desc,
                            color=colors['red'],
                        ).set_footer(text=search[0]['counter']))
            pass
        pass


    @tasks.loop(minutes=1)
    async def check():
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
                channel=client.get_channel(search['channelid'])
                await channel.send("You have run out of time! This is the final list, with the ones not guessed in spoilers.",embed=discord.Embed(
                    title=search['top10']['0'],
                    description=desc,
                    color=colors['red']
                ).set_footer(text=search['counter']))
            else:
                pass
        pass

    @client.event
    async def on_command_error(ctx,error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please input all required arguments.', delete_after=25)
        elif isinstance(error, commands.CommandNotFound):
            return 
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f'You are missing permissions to run this command. `{error}`', delete_after=25)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Invalid user!")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'You\'re on {str(error.cooldown.type).split(".")[-1]} cooldown for this command. Try again in {round(error.retry_after)} seconds.')
        else:
            channel = client.get_channel(716538413397835799)
            await channel.send(f"----------\nholup-guessing: \n`{error}`\n\n`{ctx.guild.id}` <@602569683543130113>")



    @bot.command()
    async def dm(ctx,id,*,message):
        if ctx.author.id!=602569683543130113 and ctx.author.id!=200621124768235521:
            return
        search=dmdb.search(Query().userid==int(id))
        if len(search)==0:
            return await ctx.reply(f"This user is blocked for {search[0]['reason']} by <@{search[0]['blockedby']}>",allowed_mentions=None)
        if search[0]['current'] == True:
            return await ctx.reply(f"This user is blocked for {search[0]['reason']} by <@{search[0]['blockedby']}>",allowed_mentions=None)
        try:
            user=bot.get_user(int(id))
        except:
            return
        await user.send(message)
        await ctx.send(f"Messaged {user.name}#{user.discriminator} {message}")




    @bot.command() 
    async def dmblock(ctx,id,*,reason):
        if ctx.author.id!=602569683543130113 and ctx.author.id!=200621124768235521:
            return
        search=dmdb.search(Query().userid==int(id))
        if search[0]['current']==True:
            dmdb.upsert({"userid":int(id),"blockedby":ctx.author.id,"reason":reason,"current":False},Query().userid==int(id))
            await ctx.reply(f"Unblocked <@{search[0]['userid']}>")
        if search[0]['current']==False:
            dmdb.upsert({"userid":int(id),"blockedby":ctx.author.id,"reason":reason,"current":True},Query().userid==int(id))
            await ctx.reply(f"Blocked <@{search[0]['userid']}>")
        pass


    @bot.command()
    async def remove(ctx,counter):
        if ctx.author.id!=602569683543130113 and ctx.author.id!=200621124768235521:
            return
        topdb.remove(Query().counter==counter)
        await ctx.send(f"Removed No. {counter}")


    web.keep_alive()
    bot.run(os.environ.get("token"))

def purify(x):
    x=x.replace(" ","").replace('\'',"").replace("\"","").replace(",","").replace(";","").replace("-","").replace(":","").replace("’","").replace(".","")
    return x

def getlist(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    listx=soup.find_all('b')
    listz=soup.find_all('h1')
    listy=[listz[0].get_text()]
    for i in listx:
        if len(listy)==11:
            break
        if i.get_text()==None or i.get_text()=="" or i.get_text()=='\n':
            pass
        else:
            listy.append(i.get_text())
    return listy


#adds all the data to db from scratch. run only if db gets corrupted. also change to upsert somtime soon

def login_and_add_data():

    login_url = 'https://secure.thetoptens.com/v5/login.asp'
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(login_url)
    username = driver.find_element_by_xpath('//input[@placeholder="Username"]')
    username.send_keys("holupmod")
    password = driver.find_element_by_xpath('//input[@placeholder="Password"]')
    password.send_keys("holup1984")
    log_in_button = driver.find_element_by_class_name('orangebutton')
    log_in_button.click()
    driver.implicitly_wait(10)
    driver.get('https://www.thetoptens.com/m/holupmod/')
    listy=[]
    for i in range(125):
        try:
            driver.execute_script(f"ShowFavorites({i}0)")
        except Exception as e:
            print(e)
            pass
        driver.implicitly_wait(10)
        index_page=driver.page_source
        soup = BeautifulSoup(index_page, 'html.parser')
        for a in soup.find_all('a',{'style':'font-size:16px;line-height:30px;text-decoration:none'}):
            listy.append(a['href'])
    print("got links")
    for link in listy:
        listx=getlist(link)
        title=listx.pop(0)
        try:
            dictx={0:title}
            for i,value in enumerate(listx):
                dictx[i+1]=value
            topdb.upsert({'counter':len(topdb.all())+1,"top10":dictx},Query().top10==dictx)
        except Exception as e:
            print(e)
    print('done')
    driver.close()
main()
# login_and_add_data()
