import disnake
from disnake.ext import commands

TOKEN = "TOKEN"
intents = disnake.Intents.all()

sync_cmd = commands.CommandSyncFlags(sync_commands_debug=True)
bot = commands.InteractionBot(intents=intents,command_sync_flags=sync_cmd)

if __name__ == "__main__":
    bot.load_extension("Genshin.GenshinCog")
    bot.run(TOKEN)
