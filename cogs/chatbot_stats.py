import discord, time, re
from discord.ext import commands
from datetime import datetime, timezone, timedelta

wib_tz = timezone(timedelta(hours=7))

class StatsButtonsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        self.add_item(discord.ui.Button(
            label="Info model AI",
            url="https://qwen.ai/blog?id=qwen3.6-27b",
            style=discord.ButtonStyle.link 
        ))
        
        self.add_item(discord.ui.Button(
            label="Source code (repositori GitHub)",
            url="https://github.com/AbinDai/Aika-Yokina-BinRoom-Mascot-Discord-Bot",
            style=discord.ButtonStyle.link
        ))

class AIChatbotStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = int(time.time())

    def get_ai_cog(self):
        cog = self.bot.get_cog("AIPersona")
        if not cog:
            print("[Aika] Gagal menemukan instance cog 'AIPersona'.")
        return cog

    @commands.hybrid_command(name="ai_chatbot_stats", description="Menampilkan statistik API chatbot.")
    async def ai_chatbot_stats(self, ctx:commands.Context):
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
                
            return int(time.time()+total_detik)

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

                    if rasio < 0.25:
                        warna = MERAH
                    elif rasio < 0.50:
                        warna = KUNING
                    else:
                        warna = IJO
                    bar += f"{warna}█"
                else:
                    bar += f"{ABUABU}░"
                    
            return bar + RESET

        ai_cog = self.get_ai_cog()
        if not ai_cog:
            print("[Aika] Command dibatalkan karena cog AIPersona tidak terdeteksi.")
            if ctx.interaction:
                await ctx.interaction.response.send_message("❌ Error: Cog AIPersona belum dimuat.")
            else:
                await ctx.send("❌ Error: Cog AIPersona belum dimuat.")
            return

        # ambil data metadata & session dari AIPersona
        meta = getattr(ai_cog, "last_api_meta", {})
        session = getattr(ai_cog, "session_usage", {
            "total_requests": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        })

        print(f"[Aika] Mengambil data statistik. Total request sesi: {session.get('total_requests', 0)} | Ada data meta: {bool(meta)}")

        embed = discord.Embed(
            title="Statistik AI Aika",
            color=0xF05237,
        )

        icon_footer = "https://cdn.discordapp.com/attachments/863959650448703538/1540201066455371888/bunga.png?ex=6a8c6345&is=6a8b11c5&hm=b8a5432ef12255a46f3f94d6490a5fa22e4517b5182b4a52aea2ae41da76b117&"
        restart_wib = datetime.fromtimestamp(self.start_time, tz=wib_tz).strftime("%H:%M")

        embed.set_author(name="Ditenagai oleh Groq Qwen 3.6 27B", icon_url="https://cdn.discordapp.com/attachments/863959650448703538/1541386627434414160/Groq_Icon_-_Colored_-_338x512_-_zonalogo.com.png?ex=6a8d67a9&is=6a8c1629&hm=c61d6312865796f54c472103ae51b2151c003287f865e61473b29ec7d18d677a&")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/863959650448703538/1541385549254885506/groq-icon-logo-png_seeklogo-605779.png?ex=6a8d66a8&is=6a8c1528&hm=00a831a2abda8bdc02f2cc949b86ca425cfd6b3de293825c35a9e92779000577&")
        embed.set_footer(icon_url=icon_footer, text=f"Aika sempat restart pada {restart_wib} WIB")

        # 1. latensi & performa request Terakhir
        field_1_name = "Performa request terkini"
        if meta:
            tps = meta.get("tok_per_sec", 0.0)
            q_time = meta.get("queue_time", 0.0)
            p_time = meta.get("prompt_time", 0.0)
            c_time = meta.get("completion_time", 0.0)
            t_time = meta.get("total_time", 0.0)

            perf_text = (
                f"`{tps:.1f}` token/detik\n"
                f"Total waktu: `{t_time:.3f}s`\n"
                f"-# └ Antrean: `{q_time:.3f}s`\n"
                f"-# └ Prompt: `{p_time:.3f}s`\n"
                f"-# └ Proses: `{c_time:.3f}s`"
            )
        else:
            perf_text = "*Belum ada rekaman panggilan API pada sesi ini.*"
        embed.add_field(name=field_1_name, value=perf_text, inline=True)

        # 2. total akumulasi token dari sesi skarang
        field_2_name = "Akumulasi sesi"
        session_text = (
            f"Total request: `{session['total_requests']}`\n"
            f"Token prompt: `{session['prompt_tokens']:,}`\n"
            f"Token kelar: `{session['completion_tokens']:,}`\n"
            f"Token total: `{session['total_tokens']:,}`\n"
            f"Pengguna tercatat: `{len(ai_cog.user_chats)}`"
        )
        embed.add_field(name=field_2_name, value=session_text, inline=True)

        # 3. token API terakhir
        field_3_name = "Token API terakhir"
        if meta:
            field_3_desc = (
                f"Input: `{meta.get('prompt_tokens')}`\n"
                f"Output: `{meta.get('completion_tokens')}`\n"
                f"Total: `{meta.get('total_tokens')}`"
            )
        else:
            field_3_desc = "*Menunggu...*"
        embed.add_field(name=field_3_name, value=field_3_desc, inline=True)

        # 4. live rate limit headers dari Groq
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

            # Field 1: Requests
            rpd_field_value = (
                "```ansi\n"
                f"0 [{bar_rpd}] {rem_rpd}\n"
                "```\n"
                f"-# Reset {rpd_str}"
            )

            # Field 2: Tokens
            tpm_field_value = (
                "```ansi\n"
                f"0 [{bar_tpm}] {rem_tpm}\n"
                "```\n"
                f"-# Reset {tpm_str}"
            )

            embed.add_field(name=f"Kuota request harian: {pct_rpd}%", value=rpd_field_value, inline=True)
            embed.add_field(name=f"Kuota token per menit: {pct_tpm}%", value=tpm_field_value, inline=True)
        else:
            embed.add_field(name="Kuota real-time Groq", value="*Menunggu header respon pertama dari API...*", inline=True)

        view = StatsButtonsView()
        print(f"[Aika] Membalas embed statistik")
        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(AIChatbotStats(bot))
