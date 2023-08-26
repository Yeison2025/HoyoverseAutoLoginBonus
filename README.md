# HoyoverseAutoLoginBonus
The repository can automate claiming hoyoverse login bonus

# Usage
```
import GenshinWrapper

USER_AGENT = "Enter User-Agent Here!"
COOKIES = "Enter Your Account Cookies Here!"
wrapper = GenshinWrapper()
print(asyncio.run(wrapper.claim_daily_bonus()))
```
