import json
import random
import datetime

import disnake
from disnake.ext.commands import Bot, Cog, slash_command
from disnake.ext import commands, tasks

from .GenshinWrapper import GenshinWrapper

class GenshinCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_login_info(self):
        with open("genshin_login_info.json") as f:
            info = json.loads(f.read())

        return info

    async def write_login_info_to_json(self, user_id, user_agent, cookies):
        info = await self.get_login_info()
        info[user_id] = {"user_agent": user_agent, "cookies": cookies}

        with open("genshin_login_info.json", "w") as f:
            f.write(json.dumps(info))
    
    @slash_command(name="genshin", description="原神関係のコマンドを使用することができます。")
    async def genshin(self, inter):
        pass

    @genshin.sub_command(name="login", description="原神のログインボーナスを受け取るためのログインをします。")
    async def slash_login(self, inter):
        modal_custom_id = str(random.randint(11111,99999))
        modal_components = [
            disnake.ui.TextInput(
                label="User Agent",
                custom_id="user_agent",
                style=disnake.TextInputStyle.short,
                min_length=3,
                max_length=1024,
                placeholder="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ),
            disnake.ui.TextInput(
                label="Cookies",
                custom_id="cookies",
                style=disnake.TextInputStyle.short,
                min_length=5,
                max_length=1024,
                placeholder="ltoken=**************; "
            )
        ]
        await inter.response.send_modal(
            title="ログイン",
            custom_id=modal_custom_id,
            components=modal_components
        )
        modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
            "modal_submit",
            check=lambda x: x.custom_id == modal_custom_id,
            timeout=700
        )

        await modal_inter.response.defer(ephemeral=True)

        user_agent = modal_inter.text_values["user_agent"]
        cookies = modal_inter.text_values["cookies"]

        wrapper = GenshinWrapper(cookies=cookies, user_agent=user_agent)
        user_info = await wrapper.get_user_info()
        if user_info["error"] == True:
            await modal_inter.send("ログインできませんでした。クッキーなどが間違っている可能性があります。", ephemeral=True)
            return
        
        else:
            user_games_data = await wrapper.user_games_list()
            genshin_data = user_games_data.get("GenshinImpact")
            if genshin_data:
                nickname = genshin_data["nickname"]
                uid = genshin_data["uid"]
        
                await modal_inter.send(f"原神のログインが完了しました。\nUID: {uid}\nニックネーム: {nickname}", ephemeral=True)
        
        await self.write_login_info_to_json(user_id=inter.user.id, user_agent=user_agent, cookies=cookies)
        return

    @genshin.sub_command(name="claim", description="原神のログインボーナスを手動で受け取ります。")
    async def slash_claim(self, inter):
        await inter.response.defer(ephemeral=True)

        user_id = str(inter.user.id)
        all_users_login_info = await self.get_login_info()
        user_info = all_users_login_info.get(user_id)
        if user_info == None:
            await inter.send("ログイン情報が見つかりませんでした。\n/genshin login でログインしてから行ってください。", ephemeral=True)
            return
        
        cookies = user_info["cookies"]
        user_agent = user_info["user_agent"]
        wrapper = GenshinWrapper(cookies=cookies, user_agent=user_agent)
        bonus_info = await wrapper.claim_daily_bonus()

        claimed_game_name = ", ".join([x for x in bonus_info])
        await inter.send(f"{claimed_game_name}のログインボーナスを受け取りました！", ephemeral=True)
        return
    
    @tasks.loop(seconds=1)
    async def login_crawler(self, inter):
        now_datetime = datetime.datetime.now()
        now_time = now_datetime.strftime('%H:%M:%S')
        if now_time != "06:00:01":
            return
        
        all_users_login_info = await self.get_login_info()
        for user_id in all_users_login_info:
            user_info = all_users_login_info.get(user_id)

            cookies = user_info["cookies"]
            user_agent = user_info["user_agent"]
            wrapper = GenshinWrapper(cookies=cookies, user_agent=user_agent)
            bonus_info = await wrapper.claim_daily_bonus()

            claimed_game_name = ", ".join([x for x in bonus_info])
            await inter.user.send(f"{claimed_game_name}のログインボーナスを受け取りました！", ephemeral=True)

def setup(bot: Bot):
    bot.add_cog(GenshinCog(bot))
    print("Added cog: GenshinCog")
