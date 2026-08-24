import discord
from typing import Optional
from discord.ext import commands
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "assets" / "tentang server.png"

class InfoServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="post_infoserver", description="Ngirim chat info server ke channel info-server")
    @commands.has_permissions(administrator=True)
    async def post_infoserver(self, ctx):
        ambil_gambar = discord.File(IMAGE_PATH, filename="tentang server.png")

        embed = discord.Embed(
            title = "Selamat datang di BinRoom!",
            description = "BinRoom adalah sebuah komunitas kecil yang dibangun oleh <@1524951093560213638>. BinRoom berisi para gamer (khususnya player Geometry Dash), orang-orang kreatif, desainer grafis, ilustrator, dan masih banyak lagi.\n\n<:Discordpink:1539758228131414136> [Link invite](https://discord.gg/cDMxkAkMYm)   <:webpink:1539758261866340403> [Carrd](https://binroom.carrd.co/)   <:Youtube_logopink:1539757059183222804> [YouTube](https://youtube.com/playlist?list=PLQx-Pk4-PW8pYpaIAZC6-N-ByDUcjhgoK)   <:facebookpink:1539758478661521478> [Facebook](https://www.facebook.com/share/1Bv9XpzuaR/)",
            color = discord.Color(11433637)
        )

        channel = self.bot.get_channel(904972338687270992)
        if channel is None:
            await ctx.send("❌ I couldn't find the target channel.")
            return
        
        await channel.send(file=ambil_gambar)
        await channel.send(embed=embed)

        await ctx.send(f"✅ Pesan info server server terkirim di channel {channel.mention}.")

async def setup(bot):
    await bot.add_cog(InfoServer(bot))