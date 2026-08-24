import discord
from typing import Optional
from discord.ext import commands
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "assets" / "hobi.png"

class PickRole_Hobby(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="post_role-hobi", description="Ngirim chat Pewarna Nickname ke channel ambil-role")
    @commands.has_permissions(administrator=True)
    async def post_rolehobi(self, ctx):
        ambil_gambar = discord.File(IMAGE_PATH, filename="hobi.png")

        embed = discord.Embed(
            description = "🏯 <@&1054710978413068378>\n💻 <@&1054710741757870111>\n🎮 <@&1054711107379548223>\n🎨 <@&1054711278469390387>\n🎵 <@&1285067697222189096>\n👟 <@&1285067967758860318>\n🎀 <@&1328263742072553602>",
            color = discord.Color(0xFFF3FD)
        ).set_footer(text="React dengan emoji sesuai pada teks untuk mengamil role yang diinginkan.")

        channel = self.bot.get_channel(1539871181765611560)
        if channel is None:
            await ctx.send("❌ Channel-nya gaada. Coba cek lagi ID-nya.")
            return
        
        await channel.send(file=ambil_gambar)
        await channel.send(embed=embed)

        await ctx.send(f"✅ Pesan info server server terkirim di channel {channel.mention}.")

async def setup(bot):
    await bot.add_cog(PickRole_Hobby(bot))