import discord
from typing import Optional
from discord.ext import commands
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "assets" / "pulau asal.png"

class PickRole_IslandOrigin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="post_role-pulauasal", description="Ngirim chat Pewarna Nickname ke channel ambil-role")
    @commands.has_permissions(administrator=True)
    async def post_rolepulauasal(self, ctx):
        file_gambar = r"D:\binroom\webhook\aset visual\v2\pulau asal.png"
        ambil_gambar = discord.File(file_gambar)

        embed = discord.Embed(
            description = "1️⃣ <@&1054702961684656188>\n🔑 <@&1054707380128059454>\n3️⃣ <@&1054707443856310332>\n4️⃣ <@&1054707561603010690>\n5️⃣ <@&1054707644415365170>\n🌏 <@&926527589378572419>",
            color = discord.Color(0xAE76A5)
        ).set_footer(text="React dengan emoji sesuai pada teks untuk mengamil role yang diinginkan.")

        channel = self.bot.get_channel(1539871181765611560)
        if channel is None:
            await ctx.send("❌ Channel-nya gaada. Coba cek lagi ID-nya.")
            return
        
        await channel.send(file=ambil_gambar)
        await channel.send(embed=embed)

        await ctx.send(f"✅ Pesan info server server terkirim di channel {channel.mention}.")

async def setup(bot):
    await bot.add_cog(PickRole_IslandOrigin(bot))