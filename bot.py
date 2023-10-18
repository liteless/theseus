import sys
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json

from utils.database import Database


class Client(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or(),
            intents=intents
        )

        if os.path.exists("config.json"):
            with open("config.json") as f:
                self.config = json.load(f)
        else:
            sys.exit(
                "'config.json' not found. Please configure the bot before running it.")

    async def load_cogs(self) -> None:
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to load extension {extension}\n{exception}")

    async def setup_hook(self) -> None:
        self.database = Database(
            uri=os.getenv("MONGODB_URI"),
            db=self.config["database"]
        )
        await self.load_cogs()
        await self.tree.sync()

    async def on_ready(self) -> None:
        print("THESEUS is ready.")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.author == self.user:
            return

        await self.process_commands(message)


if __name__ == "__main__":
    load_dotenv(override=True)

    client = Client()
    client.run(os.getenv("TOKEN"))
