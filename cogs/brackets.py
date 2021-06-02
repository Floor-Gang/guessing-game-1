# [ main cog for brackets/tournaments ]
import discord
from discord.ext import commands
from tinydb import TinyDB,Query


xdb=TinyDB("database.json")
tournamentdb=xdb.table("tournament",cache_size=30)

class Brackets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):
        reaction=payload.emoji
        user=self.bot.get_user(payload.user_id)
        if user==self.bot.user:
            return
        if str(reaction)=="✍️":
            msgid=payload.message_id
            searchd=tournamentdb.search(Query().msgid==msgid)
            if len(searchd)!=0:
                if searchd[0]["closed"]==False:
                    listx=searchd[0]["people"]
                    if user.id in listx:
                        listx.remove(user.id)
                        await user.send("You have removed your entry!")
                    else:
                        await user.send("You haven't signed up!")
                    tournamentdb.update({"people":listx},Query().msgid==msgid)
                    
                else:
                    try:
                        if user.bot==False:
                            await user.send("Signups have been closed for this!")
                    except:
                        pass
            pass
        


    @commands.command(aliases=["brackets","tournament",'signups','signup'])
    async def bracket(self,ctx,channel :discord.TextChannel,*,reason):
        if ctx.author.id != 602569683543130113 and ctx.author.id!=200621124768235521:
            return
        count=len(tournamentdb.all())+1
        
        m = await channel.send(embed=discord.Embed(
            description=f"React to this with :writing_hand: to sign up for {reason}."
            ).set_footer(text=count))
        tournamentdb.insert({"number":len(tournamentdb.all())+1,"people":[],"msgid":m.id,"closed":False})
        await m.add_reaction("✍️")
        await ctx.send(f"Added reaction-bracket for {reason} in #{channel.name} with id {count}")
        pass

    @commands.command(aliases=["open",'toggle'])
    async def close(self,ctx,id):
        pass
        if ctx.author.id != 602569683543130113 and ctx.author.id!=200621124768235521:
            return
        search=tournamentdb.search(Query().number==id)
        if len(search)!=0:
            state="Closed"
            if search[0]['current']==False:
                boolx=True
                state="Open"
            else:
                boolx=False
            tournamentdb.update({"current":boolx},Query().number==id)
            
            await ctx.send(f"The signup is {state}")
        else:
            await ctx.send("Invalid id")

    @commands.command()
    async def create(self,ctx,number:int):
        list1,list2=[],[]
        search=tournamentdb.search(Query().number==number)
        if len(search)==0:
            return await ctx.send("No signups with that id")
        for i in list(search[0]['people']):
            list2.append(i)
            if len(list2)==2:
                list1.append(list2)
                list2=[]
        if len(list(search[0]["people"]))%2!=0:
            list1.append(list2)
        desc=""
        for num,i in enumerate(list1):
            if len(i)==1:
                desc=desc+str(num+1)+". <@"+str(i[0])+"> passes on due to odd no. of people.""\n"
            else:
                desc=desc+str(num+1)+". <@"+str(i[0])+"> x <@"+str(i[1])+">\n"
        await ctx.send(embed=discord.Embed(title=f"Signups for {number}",description=desc))

def setup(bot):
    bot.add_cog(Brackets(bot))