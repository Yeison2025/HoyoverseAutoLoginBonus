# HoyoverseAutoLoginBonus
The repository can automate claiming of the hoyoverse login bonus. <br>
It can claim the daily login bonus of Honkai Star Rail and Genshin Impact.

# Usage
```
import GenshinWrapper

USER_AGENT = "Enter User-Agent Here!"
COOKIES = "Enter Your Account Cookies Here!"
wrapper = GenshinWrapper()
print(asyncio.run(wrapper.claim_daily_bonus()))
```

# Require
```
aiohttp
disnake
```

# Using the Bot
1. Clone the Repository
2. Go to /bot
3. Change the bot.py TOKEN variable to your bot token
4. Run the bot

