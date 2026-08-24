import discord
from typing import Optional
from discord.ext import commands

class ForceEditEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="paksa_edit-embed-di-infoserver", description="Ngedit isi embed di info server (jangan lupa kasih ID pesannya)")
    @commands.has_permissions(administrator=True)
    async def forceeditembed(
        self, ctx:commands.Context,
        message_id: str
    ):
        await ctx.defer(ephemeral=False)

        channel = self.bot.get_channel(904972338687270992)
        if channel is None:
            await ctx.send("❌ Channel-nya gaada.")
            return

        try:
            msg_id = int(message_id)
            target_message = await channel.fetch_message(msg_id)

            if not target_message.embeds:
                await ctx.send("❌ Pesannya gaada embed.")
                return

            old_embed = target_message.embeds[0]
            new_embed = old_embed.copy()
            new_embed.description = "BinRoom adalah sebuah komunitas kecil yang didirikan oleh <@1524951093560213638>. BinRoom berisi para gamer (khususnya player Geometry Dash), orang-orang kreatif, desainer grafis, ilustrator, dan masih banyak lagi. Server ini bertemakan rumah, disusun layaknya rumah betulan, dan punya tema role kayak penghuni rumah asli. Penentuan tema ini bermakna agar semoga para member betah di sini layaknya rumah.\n\n<:Discordpink:1539758228131414136> [Link invite](https://discord.gg/cDMxkAkMYm) <:webpink:1539758261866340403> [Carrd](https://binroom.carrd.co/) <:Youtube_logopink:1539757059183222804> [YouTube](https://youtube.com/playlist?list=PLQx-Pk4-PW8pYpaIAZC6-N-ByDUcjhgoK) <:facebookpink:1539758478661521478> [Facebook](https://www.facebook.com/share/1Bv9XpzuaR/)"

            await target_message.edit(embed=new_embed)

            message_url = f"https://discord.com/channels/{ctx.guild.id}/{channel.id}/{target_message.id}"
            
            await ctx.send(f"✅ Embed berhasil diperbarui. [Silakan liat di sini.]({message_url})")

        except ValueError:
            await ctx.send("❌ ID pesannya salah.")
        except discord.NotFound:
            await ctx.send("❌ Pesannya gaada.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Gagal ngedit pesan: {e}")

async def setup(bot):
    await bot.add_cog(ForceEditEmbed(bot))