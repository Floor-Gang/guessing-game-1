import discord
from discord.ext import commands
from tinydb import TinyDB,Query
import aiohttp



xdb=TinyDB("database.json")
dmdb=xdb.table("dm",cache_size=0)




class Dm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
    @commands.command()
    async def dm(self,ctx,id,*,message):
        if ctx.author.id!=602569683543130113 and ctx.author.id!=200621124768235521:
            return
        search=dmdb.search(Query().userid==int(id))

        if len(search)!=0:
            if search[0]['current'] == True:
                return await ctx.reply(f"This user is blocked for {search[0]['reason']} by <@{search[0]['blockedby']}>",allowed_mentions=None)
        try:
            user=self.bot.get_user(int(id))
        except:
            return
        await user.send(message)
        await ctx.send(f"Messaged {user.name}#{user.discriminator} {message}")

    @commands.command(aliases=["lb",'leaderboard','points'])
    async def rank(self,ctx):
        pass



    @commands.command(aliases=['reportblock','block']) 
    async def dmblock(self,ctx,id,*,reason):
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


    @commands.command() 
    async def report(self,ctx,id,*,reason=None):
        if not reason:
            reason="Not given"
        dmsearch = dmdb.search(Query().userid==ctx.author.id)
        if len(dmsearch) != 0 and dmsearch[0]["current"]==True:
            return await ctx.send("You are blocked from sending DMs and Reports.")
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url('https://discord.com/api/webhooks/847191143129153546/ik2wF1P69DUFPqwaFmdcdOyRkmy7Vkem_jHGUR9ttaDFm7mDxy_9v-tkx0iKhEasVr3j', adapter=discord.AsyncWebhookAdapter(session))
            nmsg = f"Report\n**From: {ctx.author.name}#{ctx.author.discriminator}**({ctx.author.id})\nList ID: {id}\n**Reason:**\n{reason}"
            await webhook.send(nmsg)
        await ctx.send("Reported")
        pass

def setup(bot):
    bot.add_cog(Dm(bot))