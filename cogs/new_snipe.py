import discord
import datetime
from discord.ext import commands
import asyncio

class Snipe(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.snipes = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        # Store message data along with creation time
        self.snipes[message.channel.id] = {
            "author": message.author,
            "content": message.content,
            "created_at": message.created_at,  # discord.py provides timezone-aware datetime
            "attachment": message.attachments[0].url if message.attachments else None
        }

        # Clear memory automatically after 5 minutes (300 seconds)
        await asyncio.sleep(300)
        if message.channel.id in self.snipes and self.snipes[message.channel.id]["content"] == message.content:
            del self.snipes[message.channel.id]

    @commands.hybrid_command(name="snipe", description="Lihat pesan yang paling baru dihapus")
    async def snipe(self, ctx: commands.Context):
        sniped_data = self.snipes.get(ctx.channel.id)

        if not sniped_data:
            await ctx.send("Tidak ada pesan yang barusan dihapus di channel ini.")
            return

        # Convert datetime to Unix integer timestamp
        unix_timestamp = int(sniped_data["created_at"].timestamp())
        
        # Build embed
        embed = discord.Embed(
            title="Pesan yang Baru Saja Dihapus di Channel Ini",
            description=sniped_data["content"] or "*[Pesan tidak berisi teks]*",
            color=ctx.guild.me.color if ctx.guild else discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        
        # Adds the dynamic relative timestamp in the embed footer
        embed.add_field(
            name="Dikirim Pada", 
            value=f"<t:{unix_timestamp}:R>", 
            inline=False
        )
        
        avatar_url = sniped_data["author"].display_avatar.url
        embed.set_author(name=f"Dikirim oleh {sniped_data['author']}", icon_url=avatar_url)

        if sniped_data["attachment"]:
            embed.set_image(url=sniped_data["attachment"])

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Snipe(bot))