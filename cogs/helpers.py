import requests
import ast
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
from tinydb import TinyDB , Query
import discord

xdb = TinyDB('database.json')
topdb=xdb.table('topten',cache_size=0)
SAMPLE_SPREADSHEET_ID = '181E99091FvrIaQDtJJWOTV3VmqPVr5sCGfXGExb6mx0'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'guess10keys.json'

credentials = None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


def actual_prefix():
    return "!!"
def prefix_for_guesses():
    return ".."
def purify(x):
    x=x.replace(" ","").replace('\'',"").replace("\"","").replace(",","").replace(";","").replace("-","").replace(":","").replace("’","").replace(".","")
    return x
async def insert_returns(body):
	if isinstance(body[-1], ast.Expr):
		body[-1] = ast.Return(body[-1].value)
		ast.fix_missing_locations(body[-1])
	if isinstance(body[-1], ast.If):
		insert_returns(body[-1].body)
		insert_returns(body[-1].orelse)
	if isinstance(body[-1], ast.With):
		insert_returns(body[-1].body)
	if isinstance(body[-1], ast.AsyncWith):
		insert_returns(body[-1].body)


def getlist(link):
    try:
        domain = link.split('/')[2]
    except:
        return
    if domain == "www.thetoptens.com":
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
    elif domain == "www.shortlist.com":
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        listx=soup.find_all('h3')
        listz=soup.find_all('h2')
        listy=[listz[0].get_text()]
        for i in listx:
            if len(listy)==11:
                break
            if i.get_text()==None or i.get_text()=="" or i.get_text()=='\n':
                pass
            else:
                listy.append(i.get_text().split("\n")[0].strip(f"{len(listy)}. "))
        return listy
        pass
    elif domain == "www.ranker.com":
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        listx=soup.find_all('h1')
        listz=soup.find_all('h2')
        listy=[listx[0].get_text()]
        for i in listz:
            if len(listy)==10:
                break
            if i.get_text()==None or i.get_text()=="" or i.get_text()=='\n':
                pass
            else:
                listy.append(i.get_text().split("\n")[0].strip(f"{len(listy)}. "))

        return listy
    else:
        return None
def sheet_up():
    service = build('sheets', 'v4', credentials=credentials)
    list1=[['Title',1,2,3,4,5,6,7,8,9,10, 'pack / category (leave empty for none)' , 'counter [ DO NOT CHANGE ]']]
    list2=[]
    for i in topdb.all():
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
    service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Guess10!A:M",
        valueInputOption="USER_ENTERED", body=body).execute()


def sheet_sync_down():
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range="Guess10!A:M").execute()
    values = result.get('values', [])
    values.pop(0)
    xdb.drop_table("topten")
    topdb=xdb.table('topten',cache_size=0)
    for num,i in enumerate(values):
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
        try:
            pac=i[11]
        except:
            pac=None
        topdb.insert({"counter":num,'top10':top10dict,'pack': pac})
    print(len(topdb))
    for num,i in enumerate(topdb.all()):
        topdb.update({"counter":num+1},Query().top10==i["top10"])
    return
def ua():
    tup = ("guess10","https://media.discordapp.net/attachments/850764519344701470/850778722742304829/image4.jpg")
    return tup






def footers():
    listx = [
        ' | Don\'t like the lists? Want more variety? DM the bot with your own!',
        " | Join discord.gg/holup for more fun games!",
        " | Use the report command if you see a list unfit for the bot!",
        " | Need help with the bot? DM the bot and we might get back to you!"
    ]
    # return random.choice(listx)
    return " | A nitro event is going on! Use !!event to find out more!"
def endemotes():
    listx= [
        "<:x1:840749980800385074><:x2:840749956771479562><:x3:840749904216981526><:x4:840749868326322236>",
        "<:w1:852244012144263169><:w2:852244011946213416><:w3:852244011964039170><:w4:852244012101926962>",
        "<:tile000:852244011678171207><:tile001:852244012139151360><:tile002:852244011796398101><:tile003:852244012240601109>",
        "<:st1:852244008552890389><:st2:852244008499413012><:st3:852244008343961630><:st4:852244008502951966>",
        "<:q1:852244012021973043><:q2:852244011577114706><:q3:852244012295651379><:q4:852244012290539590>",
        "<:gt1:852244006548144158><:gt2:852244005344509963><:gt4:852244004044537857><:gt3:852244004329226260>",
        "<:ep1:852270097136353311><:ep2:852270096969760809><:ep3:852270096918773770><:ep4:852270096881287208>",
        "<:mm1:852269425021288499><:mm2:852269425213440061><:mm3:852269425359847424><:mm4:852269425545314384>",
        "<:gtt1:852278410755309608><:gtt2:852278410692657233><:gtt3:852278411023613952><:gtt4:852278410519511080>",
        "<:h1:852279658438721546><:h2:852278997596241991><:h3:852278997614460949><:h4:852278997940568064>",
        ""
    ]
    # return random.choice(listx)
    return "Did you know? A nitro event is going on right now! Use !!event to find out more!"

