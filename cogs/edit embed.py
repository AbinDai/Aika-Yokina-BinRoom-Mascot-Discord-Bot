import discord
from typing import Optional
from discord.ext import commands




class EditEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="edit-embed-di-infoserver", description="Ngedit isi embed di info server (jangan lupa kasih ID pesannya)")
    @commands.has_permissions(administrator=True)
    async def editembed(
        self, 
        ctx: commands.Context, 
        *, 
        new_description: str, 
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
            new_embed.description = new_description

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
    await bot.add_cog(EditEmbed(bot))