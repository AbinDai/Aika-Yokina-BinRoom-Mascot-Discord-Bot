import discord
from typing import Optional
from discord.ext import commands
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "assets" / "pewarna nickname.png"

class PickRole_NicknameColor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="post_pewarna-nickname", description="Ngirim chat Pewarna Nickname ke channel ambil-role")
    @commands.has_permissions(administrator=True)
    async def post_infoserver(self, ctx):
        ambil_gambar = discord.File(IMAGE_PATH, filename="pewarna nickname.png")
        embed = discord.Embed(
            description = "🔴 <@&919900780889260102>\n🔵 <@&919901034523009065>\n🟤 <@&919901201078845480>\n🟢 <@&919901293819076648>\n🟣 <@&919901530457526272>\n🟡 <@&919901659310739526>\n🟠 <@&919901944057847865>",
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
    await bot.add_cog(PickRole_NicknameColor(bot))