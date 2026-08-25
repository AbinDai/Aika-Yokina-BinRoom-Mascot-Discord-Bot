import discord
from discord.ext import commands

def warna_dinamis(latensi:int) -> int:
    # titik patokan: (latensi_ms, (R, G, B))
    PATOKAN = (
        (0,    (0, 255, 102)),   #ijo terang
        (100,  (46, 204, 113)),  #ijo muda
        (200,  (163, 230, 53)),  #ijo kekuningan
        (300,  (255, 235, 59)),  #kuning hangat
        (400,  (255, 152, 0)),   #oren
        (500,  (255, 0, 0)),     #merah darah menyala (FF0000)
        (700,  (153, 0, 0)),     #merah tua
        (900,  (91, 0, 24)),     #merah gelap / Crimson
        (1000, (74, 14, 78)),    #ungu tua / Plum
    )
    # batas bawah (0ms kebawah)
    if latensi <= PATOKAN[0][0]:
        r, g, b = PATOKAN[0][1]
        return (r << 16) + (g << 8) + b
    
    # batas atas (1000ms keatas) -> ungu tua (0x2E003E)
    if latensi >= PATOKAN[-1][0]:
        return 0x2E003E
    
    # itung gradasi rgb di antara 2 titik terdekat
    for i in range(len(PATOKAN)-1):
        p1, c1 = PATOKAN[i]
        p2, c2 = PATOKAN[i+1]
        if p1 <= latensi <= p2:
            t = (latensi-p1) / (p2-p1)
            r = int(c1[0]+t*(c2[0]-c1[0]))
            g = int(c1[1]+t*(c2[1]-c1[1]))
            b = int(c1[2]+t*(c2[2]-c1[2]))
            return (r << 16) + (g << 8) + b
    return 0x2E003E

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Nge-ping bot dan liat latensinya")
    async def ping(self, ctx:commands.Context):
        latensi = round(self.bot.latency*1000)
        kode_hex = warna_dinamis(latensi)

        embed = discord.Embed(title=f"`{latensi}` ms", color=discord.Color(kode_hex))
        embed.set_author(name="📶 Latensi Aika")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))
