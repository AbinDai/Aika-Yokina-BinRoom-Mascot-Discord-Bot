import discord
from discord.ext import commands

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="link-invite-binroom", description="Kirimin link invite server BinRoom")
    async def invite(self, ctx:commands.Context):
        await ctx.send("https://discord.gg/cDMxkAkMYm")

async def setup(bot):
    await bot.add_cog(Invite(bot))