import web
import discord
from discord.ext import commands , tasks
import os
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from cogs.helpers import actual_prefix,prefix_for_guesses
from google.oauth2 import service_account
from googleapiclient.discovery import build
from tinydb import TinyDB,Query
import threading

xdb=TinyDB("database.json")
topdb=xdb.table("topten",cache_size=0)


actual_prefix=actual_prefix()
prefix_for_guesses=prefix_for_guesses()


SAMPLE_SPREADSHEET_ID = '181E99091FvrIaQDtJJWOTV3VmqPVr5sCGfXGExb6mx0'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'guess10keys.json'

credentials = None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


'''
main => gsheets, errors, help , startup&cog imports, webserver imports

cogs.brackets => tournament bracket creation
cogs.dmreport => dm block, dm back, report lists
cogs.guess => start command, checks guesses 
cogs.helpers => helper functions, no commands 
cogs.manipulate => eval, add , remove and anything to do with manipulating the db directly
cogs.check => checks
cogs.show => end and hint , rank
cogs.vote => vote to end game

cogs.textcreate => [ in progress ] create text effects
'''

bot = commands.Bot(command_prefix=actual_prefix,
intents=discord.Intents.all())
client = bot

bot.remove_command("help")

cog_imports = [
    "cogs.brackets",
    "cogs.dmreport",
    "cogs.guess",
    "cogs.manipulate",
    "cogs.check",
    "cogs.show",
    "cogs.vote"
]





@bot.event
async def on_ready():
    sheet_sync.start()
    print("Started")


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



service = build('sheets', 'v4', credentials=credentials)
lastno = list(topdb.all())[-1]['counter']+1
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="Guess10!A:M").execute()

values = result.get('values', [])

list1=[['Title',1,2,3,4,5,6,7,8,9,10, 'pack / category (leave empty for none)' , 'counter [ DO NOT CHANGE ]']]
list2=[]

for i in topdb.all():
    i0 = i['top10']['0']
    i1 = i['top10']['1']
    list2 = [
    i['top10']['0'],
    i['top10']['1'],
    i['top10']['2'],
    i['top10']['3'],
    i['top10']['4'],
    i['top10']['5'],
    i['top10']['6'],
    i['top10']['7'],
    i['top10']['8'],
    i['top10']['9'],
    i['top10']['10'],
    i['pack'],
    i['counter']
    ]
    list1.append(list2)
    list2=[]

body = {
    'values': list1
}

result = service.spreadsheets().values().update(
    spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Guess10!A:M",
    valueInputOption="USER_ENTERED", body=body).execute()

class BackgroundTasks(threading.Thread):
    def sheet_sync_down():
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Guess10!A:M").execute()
        values = result.get('values', [])
        values.pop(0)
        for i in values:
            top10dict = {
                '0': i[0],
                '1': i[1],
                '2': i[2],
                '3': i[3],
                '4': i[4],
                '5': i[5],
                '6': i[6],
                '7': i[7],
                '8': i[8],
                '9': i[9],
                '10': i[10],
            }
            topdb.upsert({"counter":int(i[12]),'top10':top10dict,'pack': i[11]},Query().counter==int(i[12]))
        print(len(topdb))
t = BackgroundTasks()

@tasks.loop(minutes=10)
async def sheet_sync():
    t.start()




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