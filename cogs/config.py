from discord.ext import commands
from tinydb import TinyDB,Query



configdb=TinyDB("database.json").table("config",cache_size=0)


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def config(self,ctx,typex=None,*,params=None):
        if typex == None or params==None:
            return await ctx.send("""
Format is: `config {type} {parameters}`
Valid types: votecount <num>
""")
        if typex=="votecount":
            try:
                int(params)
            except:
                return await ctx.send("It has to be a numerical value below 500!")
            if int(params) > 500 or int(params) < 1:
                return await ctx.send("It has to be a numerical value below 500 , and above 0!")
            configdb.upsert({'guildid':ctx.guild.id,'votecount':int(params)},Query().guildid==ctx.guild.id)
            return await ctx.send(f"Config for {ctx.guild.name} has been updated!")


        pass


def setup(bot):
    bot.add_cog(Config(bot))