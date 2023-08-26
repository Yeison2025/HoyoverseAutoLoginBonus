import aiohttp

class GenshinWrapper:
    def __init__(self, cookies, user_agent) -> None:
        self.cookies = cookies
        self.user_agent = user_agent
        self.auth_host =  "https://api-account-os.hoyolab.com/auth/api"
        self.binding_host = "https://api-os-takumi.mihoyo.com/binding/api"
        self.headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://act.hoyolab.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': self.cookies
        }
    
    async def get_user_info(self) -> str:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            token_url = self.auth_host + "/getUserAccountInfoByLToken"
            response = await session.get(token_url)
            response_json = await response.json()
        
        user_data = response_json.get("data")
        print(response_json)
        if user_data == None:
            return {"error": True, "message": "The cookies have wrong or invalid value", "response": response_json}
        
        login_message = user_data.get("message")
        if login_message and login_message != "OK":
            return {"error": True, "message": "The cookies have wrong or invalid value"}
        
        self.uid = user_data["account_id"]
        self.user_name = user_data["account_name"]

        return {
            "error": False,
            "hoyoverse_uid": self.uid,
            "hoyoverse_user_name": self.user_name
        }

    async def user_games_list(self):
        headers = self.headers
        async with aiohttp.ClientSession(headers=headers) as session:
            games_url = self.binding_host + "/getUserGameRolesByCookie"
            response = await session.get(games_url)
            response_json = await response.json()
        
        user_data = response_json.get("data")
        login_message = user_data.get("message")
        if login_message and login_message != "OK":
            return {"error": True, "message": "The cookies have wrong or invalid value"}
        
        user_games = {}
        for game in user_data["list"]:
            game_biz = game["game_biz"]
            if game_biz == "hk4e_global":
                game_name = "GenshinImpact"
                act_id = "e202102251931481"
                url_type = "sol"

            elif game_biz == "hkrpg_global":
                game_name = "HonkaiStarRail"
                act_id = "e202303301540311"
                url_type = "luna"

            else:
                continue

            uid = game["game_uid"]
            nickname = game["nickname"]
            user_games[game_name] = {"uid": uid, "nickname": nickname, "act_id": act_id, "url_type": url_type}
        
        return user_games
    
    async def claim_daily_bonus(self):
        user_games_list = await self.user_games_list()
        user_claim_result = {}
        for game in user_games_list:
            game_name = game
            game_data = user_games_list[game_name]
            act_id = game_data["act_id"]
            game_result = {}
            async with aiohttp.ClientSession(headers=self.headers) as session:
                login_info_url = "https://sg-hk4e-api.hoyolab.com/event/"+ game_data["url_type"] + "/info?act_id=" + act_id
                response = await session.get(login_info_url)
                user_login_info = await response.json()
            
            user_bonus_data = user_login_info.get("data")
            user_bonus_message = user_bonus_data.get("message")
            if user_bonus_message:
                user_bonus_data = user_bonus_data.get("total_sign_day")
            else:
                user_bonus_data = 0

            user_sign_day = user_bonus_data

            async with aiohttp.ClientSession(headers=self.headers) as session:
                reward_url = "https://sg-hk4e-api.hoyolab.com/event/"+ game_data["url_type"] + "/home?act_id=" + act_id
                response = await session.get(reward_url)
                reward_info = await response.json()
            
            awards = reward_info["data"]["awards"]
            claimed_award = awards[user_sign_day-1]

            async with aiohttp.ClientSession(headers=self.headers) as session:
                claim_url = "https://sg-hk4e-api.hoyolab.com/event/"+ game_data["url_type"] + "/sign?act_id=" + act_id
                json_data = {"act_id": act_id}
                response = await session.post(claim_url, json=json_data)
                result = await response.json()
            
            user_result = result.get("data")
            if user_result == None:
                user_error_message = result.get("message")
                if user_error_message == "Traveler, you've already checked in today~":
                    game_result = {
                        "error": True,
                        "message": "Already checked in.",
                        "user_sign_day": user_sign_day,
                        "claimed_award": None
                    }
                else:
                    game_result = {
                        "error": True,
                        "message": "Something went wrong",
                        "user_sign_day": user_sign_day,
                        "claimed_award": None
                    }

            else:
                is_risk = user_result.get("is_risk")
                if is_risk:
                    game_result = {
                        "error": True,
                        "message": "Captcha Error.",
                        "user_sign_day": user_sign_day,
                        "claimed_award": None
                    }
                else:
                    game_result = {
                        "error": False,
                        "message": "Claimed Successfully.",
                        "user_sign_day": user_sign_day,
                        "claimed_award": claimed_award
                    }
            
            user_claim_result[game_name] = game_result
        
        return user_claim_result
