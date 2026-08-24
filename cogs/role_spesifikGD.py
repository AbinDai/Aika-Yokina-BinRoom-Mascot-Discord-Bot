import discord
from typing import Optional
from discord.ext import commands
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "assets" / "spesifik GD.png"

class PickRole_GDspecific(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="post_role-spesifikgd", description="Ngirim chat Pewarna Nickname ke channel ambil-role")
    @commands.has_permissions(administrator=True)
    async def post_rolespesifikgd(self, ctx):
        ambil_gambar = discord.File(IMAGE_PATH, filename="spesifik GD.png")

        embed = discord.Embed(
            description = "<:standard_cube:1267294528541560882> <@&1285064320019071008>\n<:creator_icon:1285063466532605974> <@&1285064235822616616>\n<:gd_star:1285063657839136869> <@&1285063711723360268>\n<:gd_moon:1285063495154536480> <@&1285063849036349500>\n<:hard_demon:1285063566742781984> <@&1285063979357700207>\n<:extreme_demon:1285063534379532388> <@&1285064119522951210>",
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
    await bot.add_cog(PickRole_GDspecific(bot))