import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Nge-ping bot dan liat latensinya")
    async def ping(self, ctx: commands.Context):
        # Fix: Reference self.bot instead of bot
        latency_ms = round(self.bot.latency * 1000)

        if latency_ms < 100:
            color = discord.Color.green()      
        elif latency_ms < 200:
            color = discord.Color.gold()       
        else:
            color = discord.Color.red()

        embed = discord.Embed(
            title=f"📶 `{latency_ms}`ms",
            color=color
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))