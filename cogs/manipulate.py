# [ main cog for eval,add,link,remove ]
from discord.ext import commands
from tinydb import TinyDB,Query
from cogs.helpers import getlist,insert_returns , sheet_up
import ast
import discord


xdb=TinyDB("database.json")
topdb=xdb.table("topten",cache_size=30)

class Manipulate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 


    @commands.command()
    async def add(self,ctx,*,message:str):
        if ctx.author.id != 602569683543130113 and ctx.author.id!=200621124768235521:
            return
        message=str(message).split('\n')
        title=message.pop(0)
        dictx={"0":title}
        if len(message) != 10:
            return await ctx.send("List doesnt have 10 values exactly")
        for num,i in enumerate(message):
            i=i.strip(f"{num+1}. ")
            dictx[str(num+1)]=i
        print(dictx)
        print(list(topdb.all())[-1]["counter"]+1)
        topdb.upsert({'counter':list(topdb.all())[-1]["counter"]+1,"top10":dictx},Query().top10==dictx)
        topdb.clear_cache()
        sheet_up()
        await ctx.send("Added")



        
    @commands.command()
    async def link(self,ctx,link):
        if ctx.author.id != 602569683543130113 and ctx.author.id!=200621124768235521:
            return

        listx=getlist(link)
        title=listx.pop(0)
        try:
            dictx={0:title}
            for i,value in enumerate(listx):
                dictx[i+1]=value
            topdb.insert({'counter':list(topdb.all())[-1]["counter"]+1,"top10":dictx})
            topdb.clear_cache()
            sheet_up()
            await ctx.send(f"Added {title} with {listx}")
        except Exception as e:
            await ctx.send(e)




    @commands.command(aliases= ['eval'])
    async def _eval(self,ctx, * , cmd):
        if ctx.author.id != 602569683543130113 and ctx.author.id!=200621124768235521:
            return
        fn_name = "_eval_expr"
        cmd = cmd.strip("`py ")
        cmd = cmd.strip("` ")
        cmd = "\n".join(f"	{i}" for i in cmd.splitlines())
        body = f"async def {fn_name}():\n{cmd}"
        parsed = ast.parse(body)
        body = parsed.body[0].body	
        await insert_returns(body)
        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        try:
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            await eval(f"{fn_name}()", env)
        except Exception as e:
            return await ctx.send(f"```{e.__class__.__name__}: {e}```")

    

    @commands.command()
    async def remove(self,ctx,counter):
        if ctx.author.id!=602569683543130113 and ctx.author.id!=200621124768235521:
            return
        topdb.remove(Query().counter==counter)
        topdb.clear_cache()
        sheet_up()
        await ctx.send(f"Removed No. {counter}")


def setup(bot):
    bot.add_cog(Manipulate(bot))