import discord, datetime
from discord.ext import commands

class Uptime(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.start_time = datetime.datetime.now(datetime.timezone.utc)

    def format_stopwatch(self, delta:datetime.timedelta) -> str:
        hari = delta.days
        jam, remainder = divmod(delta.seconds,3600)
        menit, detik = divmod(remainder,60)

        if hari > 0:
            return f"{hari}:{jam:02d}:{menit:02d}:{detik:02d}"
        elif jam >= 10:
            return f"{jam:02d}:{menit:02d}:{detik:02d}"
        elif jam > 0:
            return f"{jam}:{menit:02d}:{detik:02d}"
        else:
            return f"{menit:02d}:{detik:02d}"

    @commands.hybrid_command(name="uptime", description="Menampilkan waktu aktif Aika.")
    async def uptime(self, ctx:commands.Context):
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - self.start_time

        waktu_aktif = self.format_stopwatch(delta)
        timestamp_awal = int(self.start_time.timestamp())

        embed = discord.Embed(
            title="⏲️ Waktu Aktif Aika",
            color=0xD675C1 
        )
        embed.add_field(name="Online selama", value=f"`{waktu_aktif}`", inline=True)
        embed.add_field(name="Terakhir restart", value=f"<t:{timestamp_awal}:d> <t:{timestamp_awal}:T>", inline=True)

        await ctx.send(embed=embed)

async def setup(bot:commands.Bot):
    await bot.add_cog(Uptime(bot))
