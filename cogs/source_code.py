from discord.ext import commands

class SourceCode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="source_code", description="Tampilkan source code nya Aika")
    async def source_code(self, ctx):
        await ctx.send("Oh, kamu mau liat isi kodinganku? 😳\n\nhttps://github.com/AbinDai/Aika-Yokina-BinRoom-Mascot-Discord-Bot/")
    
async def setup(bot):
    await bot.add_cog(SourceCode(bot))
