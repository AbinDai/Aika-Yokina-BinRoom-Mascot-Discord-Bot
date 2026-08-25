import discord, time, re
from discord.ext import commands

class CekKuotaAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_ai_cog(self):
        cog = self.bot.get_cog("AIPersona")
        if not cog:
            print("[Aika] Gagal menemukan instance cog 'AIPersona'.")
        return cog

    @commands.hybrid_command(name="cek_kuota_ai", description="Menampilkan sisa kuota real-time Groq API.")
    async def cek_kuota_ai(self, ctx:commands.Context):
        def ubah_reset_groq_ke_unix(reset_str:str) -> int:
            if not reset_str or reset_str == "N/A":
                return None
            
            total_detik = 0.0
            jam = re.search(r'(\d+(\.\d+)?)h', reset_str)
            menit = re.search(r'(\d+(\.\d+)?)m', reset_str)
            detik = re.search(r'(\d+(\.\d+)?)s', reset_str)
            
            if jam:
                total_detik += float(jam.group(1)) * 3600
            if menit:
                total_detik += float(menit.group(1)) * 60
            if detik:
                total_detik += float(detik.group(1))
                
            if total_detik == 0.0:
                return None
                
            return int(time.time() + total_detik)

        def bikin_progress_bar(jumlah:int, total:int, panjang:int=13) -> str:
            if total <= 0:
                return "\u001b[30m░"*panjang+"\u001b[0m"
            
            progress = min(max(jumlah/total, 0.0), 1.0)
            terisi = int(round(panjang*progress))
            
            MERAH = "\u001b[31m"
            KUNING = "\u001b[33m"
            IJO = "\u001b[32m"
            ABUABU = "\u001b[30m"
            RESET = "\u001b[0m"

            bar = ""
            for i in range(panjang):
                if i < terisi:
                    rasio = i / panjang

                    if rasio < 0.25: warna = MERAH
                    elif rasio < 0.50: warna = KUNING
                    else: warna = IJO

                    bar += f"{warna}█"
                else:
                    bar += f"{ABUABU}░"
                    
            return bar + RESET

        ai_cog = self.get_ai_cog()
        if not ai_cog:
            msg = "❌ Error: Cog AIPersona belum dimuat."
            if ctx.interaction:
                await ctx.interaction.response.send_message(msg, ephemeral=True)
            else:
                await ctx.send(msg)
            return

        meta = getattr(ai_cog, "last_api_meta", {})

        embed = discord.Embed(title="Kuota Chatbot Aika", color=0xF05237)
        embed.set_author(name="Ditenagai oleh Groq Qwen 3.6 27B", icon_url="https://cdn.discordapp.com/attachments/863959650448703538/1541385549254885506/groq-icon-logo-png_seeklogo-605779.png?ex=6a8eb828&is=6a8d66a8&hm=210df3a52c0d20e870523919d668d7be881ca5c3862e4735e12c65f4955f762a&")

        if meta:
            rem_rpd = int(meta.get("rem_req_daily", 0)) if str(meta.get("rem_req_daily")).isdigit() else 0
            limit_rpd = int(meta.get("limit_req_daily", 1000)) if str(meta.get("limit_req_daily")).isdigit() else 1000

            rem_tpm = int(meta.get("rem_tok_min", 0)) if str(meta.get("rem_tok_min")).isdigit() else 0
            limit_tpm = int(meta.get("limit_tok_min", 8000)) if str(meta.get("limit_tok_min")).isdigit() else 8000

            bar_rpd = bikin_progress_bar(rem_rpd, limit_rpd, panjang=12)
            pct_rpd = int((rem_rpd / limit_rpd) * 100) if limit_rpd > 0 else 0

            bar_tpm = bikin_progress_bar(rem_tpm, limit_tpm, panjang=10)
            pct_tpm = int((rem_tpm / limit_tpm) * 100) if limit_tpm > 0 else 0

            rpd_unix = ubah_reset_groq_ke_unix(meta.get("reset_req_daily"))
            tpm_unix = ubah_reset_groq_ke_unix(meta.get("reset_tok_min"))

            rpd_str = f"<t:{rpd_unix}:R>" if rpd_unix else meta.get("reset_req_daily", "N/A")
            tpm_str = f"<t:{tpm_unix}:R>" if tpm_unix else meta.get("reset_tok_min", "N/A")

            rpd_field_value = (
                "```ansi\n"
                f"0 [{bar_rpd}] {rem_rpd}\n"
                "```\n"
                f"-# Reset {rpd_str}"
            )

            tpm_field_value = (
                "```ansi\n"
                f"0 [{bar_tpm}] {rem_tpm}\n"
                "```\n"
                f"-# Reset {tpm_str}"
            )

            embed.add_field(name=f"Kuota request harian: {pct_rpd}%", value=rpd_field_value, inline=True)
            embed.add_field(name=f"Kuota token per menit: {pct_tpm}%", value=tpm_field_value, inline=True)
        else:
            embed.description = "*Menunggu header respon pertama dari API...*"

        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CekKuotaAI(bot))