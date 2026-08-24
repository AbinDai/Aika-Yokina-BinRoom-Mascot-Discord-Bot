import discord, datetime
from discord.ext import commands

class Uptime(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.datetime.now(datetime.timezone.utc)

    def format_stopwatch(self, delta: datetime.timedelta) -> str:
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if days > 0:
            return f"{days}:{hours:02d}:{minutes:02d}:{seconds:02d}"
        elif hours >= 10:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elif hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    @commands.hybrid_command(name="uptime", description="Menampilkan waktu aktif Aika.")
    async def uptime(self, ctx:commands.Context):
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - self.start_time

        uptime_str = self.format_stopwatch(delta)
        start_timestamp = int(self.start_time.timestamp())

        embed = discord.Embed(
            title="⏲️ Waktu Aktif Aika",
            color=0xD675C1 
        )
        embed.add_field(name="Online selama", value=f"`{uptime_str}`", inline=True)
        embed.add_field(name="Terakhir restart", value=f"<t:{start_timestamp}:d> <t:{start_timestamp}:T> (<t:{start_timestamp}:R>)", inline=True)

        await ctx.send(embed=embed)

async def setup(bot:commands.Bot):
    await bot.add_cog(Uptime(bot))