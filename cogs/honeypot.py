import discord
from discord.ext import commands
import datetime

class Honeypot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.HONEYPOT_CHANNEL_ID = 1498144198577356831

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        unix_timestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

        if message.author.bot or message.channel.id != self.HONEYPOT_CHANNEL_ID:
            return

        if not message.guild or not isinstance(message.author, discord.Member):
            return

        #langsung hapus pesan phishing
        try:
            await message.delete()
        except discord.HTTPException:
            pass  # kalau semisal udah kehapus 

        #langsung gas timeout 28 hari
        try:
            timeout_duration = datetime.timedelta(days=28)
            await message.author.timeout(
                timeout_duration, 
                reason="Anda masuk perangkap honeypot / channel terlarang yang tujuan aslinya untuk menangkap pesan phishing otomatis. Anda langsung dikarantina dan di-timeout dan akan di-review nanti."
            )

            print(f"[Honeypot] Timed out {message.author} ({message.author.id})")

            embed = discord.Embed(
                title=f"Tertangkap di honeypot! 🛑",
                description="Tinjau apabila ini ketidaksengajaan atau konfirmasi dengan pemilik akun jika akses berhasil di-recover.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=0xFF0000
            )
            embed.set_thumbnail(url=f"{message.author.display_avatar.url}")
            embed.add_field(name="User", value=f"{message.author.mention}", inline=True)
            embed.add_field(name="ID", value=f"{message.author.id}", inline=True)

            channel_log = self.bot.get_channel(932191307789656064)
            await channel_log.send(embed=embed)

        except discord.Forbidden:
            print(f"[Honeypot] Failed to timeout {message.author}: Missing Permissions or higher role hierarchy.")
        except discord.HTTPException as e:
            print(f"[Honeypot] HTTP error timing out {message.author}: {e}")

async def setup(bot):
    await bot.add_cog(Honeypot(bot))