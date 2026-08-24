import discord
from discord.ext import commands
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "assets" / "info role.png"

class InfoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="post_inforole", description="Ngirim chat info role ke channel info-server")
    @commands.has_permissions(administrator=True)
    async def post_inforole(self, ctx):
        ambil_gambar = discord.File(IMAGE_PATH, filename="info role.png")

        embed = discord.Embed(
            description = "`*` = Obtainable, bisa diambil di <#904992841753841694>.",
            color = discord.Color(0xAE76A5)
        )
        embed.add_field( #1
            name="Para staf",
            value="- <@&904996218491506759>: Pemilik server, alias <@1524951093560213638>\n- <@&1539777729820364850>: Saya 🩷\n- <@&904996395260477450>: Pengawas server, dengan kata lain, atmint.\n- <@&1290940007334416406>: Anggap aja asisten ygy.",
            inline=False)
        embed.add_field( #2
            name="Anggota",
            value="- <@&904996437304172544>: Member aktif.\n- <@&905209301918974002>: Kawan-kawan real life nya owner.\n- <@&905000893836034048>: Kenalan owner walaupun jarang nimbrung.\n- <@&906029626894221315>: Anggota biasa.\n- <@&905000566931992596>: Khusus bot.",
            inline=False)
        embed.add_field( #3
            name="Penghargaan",
            value="- <@&1539781798991626372>: Mereka yang pernah berjasa jadi atmint.\n- <@&1539782121969815572>: Mereka yang pernah menang nominasi BinRoom Awards 2022.\n- <@&1053988818862223452>: Pendukung server via boost 🥰\n- <@&925543386222567494>: Member yang lagi ultah 🥳",
            inline=False)
        embed.add_field( #4
            name="Pewarna nickname `*`",
            value="<@&919900780889260102>\n<@&919901034523009065>\n<@&919901201078845480>\n<@&919901293819076648>\n<@&919901530457526272>\n<@&919901659310739526>\n<@&919901944057847865>",
            inline=True)
        embed.add_field( #5
            name="Hobi `*`",
            value="<@&1054710978413068378>\n<@&1054710741757870111>\n<@&1054711107379548223>\n<@&1054711278469390387>\n<@&1285067697222189096>\n<@&1285067967758860318>\n<@&1328263742072553602>",
            inline=True)
        embed.add_field( #6
            name="Pulau asal `*`",
            value="<@&1054702961684656188>\n<@&1054707380128059454>\n<@&1054707443856310332>\n<@&1054707561603010690>\n<@&1054707644415365170>\n<@&926527589378572419>",
            inline=True)            
        embed.add_field( #7
            name="Spesifik GD `*`",
            value="<@&918060425336201276>\n<@&1285064320019071008>\n<@&1285064235822616616>\n<@&1285063711723360268>\n<@&1285063849036349500>\n<@&1285063979357700207>\n<@&1285064119522951210>\n<@&905034343796314132>",
            inline=True)
        embed.add_field( #8
            name="More gaming `*`",
            value="<@&1054711107379548223>\n<@&918149638572371968>\n<@&918149510381858886>\n<@&918060425336201276>\n<@&1427220753786343544>\n<@&1502672334027493436>",
            inline=True)            
        embed.add_field( #9
            name="Khusus",
            value="<@&1307982731333865513>\n<@&905034343796314132> `*`\n<@&1539844848251707423> `*`\n<@&960106628689039391> `*`\n<@&965955546735849472>\n<@&905348329595076628>",
            inline=True)
        
        embed.set_footer(text="Selengkapnya di channel [# 📛・ambil-role].")

        channel = self.bot.get_channel(904972338687270992)
        if channel is None:
            await ctx.send("❌ I couldn't find the target channel.")
            return
        
        await channel.send(file=ambil_gambar)
        await channel.send(embed=embed)

        await ctx.send(f"✅ Pesan info role sukses terkirim di channel {channel.mention}.")

async def setup(bot):
    await bot.add_cog(InfoRole(bot))