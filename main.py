import web
import discord
from discord.ext import commands
import os
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from cogs.helpers import actual_prefix,prefix_for_guesses

actual_prefix=actual_prefix()
prefix_for_guesses=prefix_for_guesses()

'''
cogs.brackets => tournament bracket creation
cogs.dm => checks dms to send it to #stream 
cogs.guess => start command, checks guesses 
cogs.helpers => helper functions, no commands 
cogs.manipulate => eval, add , remove and anything to do with manipulating the db directly
cogs.check => checks

cogs.textcreate => [ in progress ] create text effects
'''

bot = commands.Bot(command_prefix=actual_prefix,
intents=discord.Intents.all())
client = bot

bot.remove_command("help")

cog_imports = [
    "cogs.brackets",
    "cogs.dm",
    "cogs.guess",
    "cogs.manipulate",
    "cogs.check",
    "cogs.show",
    "cogs.vote"
]





@bot.event
async def on_ready():
    print("started")


@bot.command()
async def help(ctx):
    await ctx.send(embed=discord.Embed(
        title="get help",
        description=f"Use `{actual_prefix}start` to start a game in any channel.\nUse `{prefix_for_guesses}guess` to guess during a game.\nUse `{actual_prefix}new` to Vote to start a new game.\nUse `{actual_prefix}hint` for one answer, can be used once per game.\nGuess the top 10 things about the topic, using {prefix_for_guesses}guess to guess"
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
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'You\'re on {str(error.cooldown.type).split(".")[-1]} cooldown for this command. Try again in {round(error.retry_after)} seconds.')
    else:
        channel = client.get_channel(716538413397835799)
        await channel.send(f"----------\nholup-guessing: \n`{error}`\n\n`{ctx.guild.id}` <@602569683543130113>")






web.keep_alive()
for extension in cog_imports:
    bot.load_extension(extension)
    print(f"Loaded {extension}")
bot.run(os.environ.get("token"))









#adds all the data to db from scratch. run only if db gets corrupted. also change to upsert somtime soon. Maybe add to cog? removed import for db.
"""
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
            topdb.upsert({'counter':list(topdb.all())[-1]["counter"]+1,"top10":dictx},Query().top10==dictx)
        except Exception as e:
            print(e)
    print('done')
    driver.close()
"""

# login_and_add_data()
# sync()