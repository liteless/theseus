import discord
from discord.ext import commands
from typing import Callable


def bot_developers_only() -> Callable[[commands.Context], bool]:
    """
    A decorator that checks if the user invoking the command is a bot developer.
    """

    async def predicate(context: commands.Context) -> bool:
        """
        The predicate that checks if the user invoking the command is a bot developer.

        :param context: The command context.
        :return: Whether the user invoking the command is a bot developer.
        """

        return context.author.id in context.bot.config["developers"]

    return commands.check(predicate)


def guild_admins_only() -> Callable[[commands.Context], bool]:
    async def predicate(context: commands.Context) -> bool:
        return await context.bot.database.is_admin(context.guild.id, context.author.id)

    return commands.check(predicate)
