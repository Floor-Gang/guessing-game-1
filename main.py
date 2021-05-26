import web
import discord
from discord.ext import commands,tasks
import os
from tinydb import TinyDB,Query
import random
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

prefix_for_guesses=">"
actual_prefix="!!"
bot = commands.Bot(command_prefix=actual_prefix,
intents=discord.Intents.all())
client = bot

bot.remove_command("help")

xdb=TinyDB("database.json")

topdb=xdb.table("topten",cache_size=30)
pointdb=xdb.table("points",cache_size=30)
currentdb=xdb.table("current",cache_size=30)
def main():

    @bot.event
    async def on_ready():
        check.start()
        print("started")

    @bot.command(aliases=['show','hint'])
    async def reveal(ctx):
        search=currentdb.search(Query().channelid==ctx.channel.id)
        if search[0]['current']==False:
            return await ctx.send("There is no game going on in this channel right now")
        gval=list(search[0]['guessed'].values())
        tval=list(search[0]['top10'].values())
        tvalx=list(search[0]['top10'].values())
        for i in gval:
            if i!=None:
                tvalx.remove(i)
        rand=random.choice(tvalx)
        guessed={}
        for j in range(10):
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
        return await ctx.send(f"{tval.index(rand)+1}. {rand}",embed=discord.Embed(
            title=search[0]['top10']['0'],
            description=desc
        ))
        pass

    @bot.command()
    async def add(ctx,link):
        if ctx.author.id != 602569683543130113:
            return
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


    @bot.command()
    async def help(ctx):
        await ctx.send(embed=discord.Embed(
            title="get help",
            description=f"Use `{actual_prefix}start` to start a game in any channel.\nUse `{prefix_for_guesses}guess` to guess during a game."
        ))
        pass


    @bot.event
    async def on_message(msg):
        if msg.author == bot.user: 
            await client.process_commands(msg)
            return
        if msg.content.startswith(f"{actual_prefix}start"):
            search=currentdb.search(Query().channelid==msg.channel.id)
            if len(search)!=0:
                if search[0]['current']==True:
                    await client.process_commands(msg)
                    return await msg.reply(f"A game is already in progress! Theres {int(search[0]['start']+60*5 - time.time())}s left for it to end!")
            rand=random.choice(topdb.all())

            print(rand)

            await msg.channel.send(embed=discord.Embed(
                title=rand['top10']['0'],
                description='1.\n2.\n3.\n4.\n5.\n6.\n7.\n8.\n9.\n10.'
            ))
            currentdb.upsert({'current':True,'top10':rand['top10'],'start':time.time(),'channelid':msg.channel.id,'userid':msg.author.id,'guessed':{'1':None,'2':None,'3':None,'4':None,'5':None,'6':None,'7':None,'8':None,'9':None,'10':None}},Query().channelid==msg.channel.id)
            return await client.process_commands(msg)
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
                    description=desc
                ))
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
                    description=desc
                ))
            top10n=list(search[0]['top10'].values())
            top10n.pop(0)
            top10x=list(map(str.lower, top10n))
            toptemp=[]
            for i in top10x:
                i=purify(i)
                toptemp.append(i)
            top10x=toptemp
            boolx=False
            for i in top10x:
                t=i.find(purify(message.lower()))
                if t>=0:
                    boolx=True
                    if len(i)>len(purify(message.lower()))+3:
                        boolx=False
            if boolx:
                guessed=search[0]['guessed']
                listg=list(guessed.values())
                listn=[]
                for i in listg:
                    if i == None:
                        pass
                    else:
                        listn.append(purify(i.lower()))
                for i in list(map(str.lower, listn)):
                    tempint = i.find(purify(message.lower()))
                    if tempint >= 0:
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
                        description=desc
                    ))
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
                        description=desc
                    ))
            else:
                await msg.add_reaction("<a:oop:846648466859229234>")
                await client.process_commands(msg)
        await client.process_commands(msg)

    @tasks.loop(minutes=5)
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
                    description=desc
                ))
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
        else:
            await ctx.send(f"An unknown error occured, please contact 25#1037 about this!\n`{error}`")
            channel = client.get_channel(716538413397835799)
            await channel.send(f"----------\holup-guessing: \n`{error}`\n\n`{ctx.guild.id}` <@602569683543130113>")




    web.keep_alive()
    bot.run(os.environ.get("token"))

def purify(x):
    x=x.replace(" ","").replace('\'',"").replace("\"","").replace(",","").replace(";","").replace("-","")
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
