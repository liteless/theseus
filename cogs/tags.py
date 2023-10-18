import discord
from discord.ext.commands.context import Context
from discord.ext import commands
from utils.database import TagNotFoundException, NotInTagException, AlreadyInTagException
from utils.helper import guild_admins_only


class Tags(commands.Cog, name="tags"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_group(
        name="tag",
        description="Manage tag groups.",
    )
    async def tag(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("<:B_down:773702309364367420> Please specify a sub-command!", ephemeral=True)

    @tag.command(
        name="join",
        description="Join a group, or create a tag group if one doesn't already exist."
    )
    @discord.app_commands.describe(
        group="The group to join / create."
    )
    async def tag_join(self, ctx: commands.Context, group: str = None):
        if group is None:
            await ctx.send("<:B_down:773702309364367420> Please specify a group!", ephemeral=True)
            return

        group = group.lower()

        try:
            new = await self.bot.database.join_tag(ctx.guild.id, group, ctx.author.id)
            await ctx.send(f"<:B_online:773702309414043658> {'Created and j' if group else 'J'}oined group `{group}`!", ephemeral=True)
        except AlreadyInTagException:
            await ctx.send(f"<:B_down:773702309364367420> You are already in group `{group}`!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"<:B_down:773702309364367420> An unexpected error occured! Try again later.", ephemeral=True)
            raise e

    @tag.command(
        name="leave",
        description="Leave a group."
    )
    @discord.app_commands.describe(
        group="The group to leave."
    )
    async def tag_leave(self, ctx: commands.Context, group: str = None):
        if group is None:
            await ctx.send("<:B_down:773702309364367420> Please specify a group!", ephemeral=True)
            return

        group = group.lower()

        try:
            deleted = await self.bot.database.leave_tag(ctx.guild.id, group, ctx.author.id)
            await ctx.send(f"<:B_online:773702309414043658> Left group `{group}`! {'This group now has no members, so it has been deleted.' if deleted else ''}", ephemeral=True)
        except TagNotFoundException:
            await ctx.send(f"<:B_down:773702309364367420> Group `{group}` does not exist!", ephemeral=True)
        except NotInTagException:
            await ctx.send(f"<:B_down:773702309364367420> You are not in group `{group}`!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"<:B_down:773702309364367420> An unexpected error occured! Try again later.", ephemeral=True)
            raise e

    @tag.command(
        name="all",
        description="List all the tags."
    )
    async def tag_all(self, ctx: commands.Context):
        tags = await self.bot.database.list_tags(ctx.guild.id)

        if len(tags) == 0:
            await ctx.send("<:B_partial:773702309245878304> There are no groups in this guild!", ephemeral=True)
            return

        embed = discord.Embed(
            color=0x2b2d31,
            description="\n".join(
                f"* **`{key}`** - {val} member(s)" for key, val in tags.items()) + f"\n\n> Use `/tag join` to join a group!",
        ).set_author(name=f"{ctx.guild.name}'s tags", icon_url=ctx.guild.icon)

        await ctx.send(embed=embed, ephemeral=True)

    @tag.command(
        name="ping",
        description="Pings all the members of a given tag."
    )
    @discord.app_commands.describe(
        group="The group to ping."
    )
    async def tag_ping(self, ctx: commands.Context, group: str = None):
        if group is None:
            await ctx.send("<:B_down:773702309364367420> Please specify a group!", ephemeral=True)
            return

        group = group.lower()

        try:
            users = await self.bot.database.get_users_in_tag(ctx.guild.id, group)
            await ctx.send(f"`{group}`: " + " ".join(f"<@{user}>" for user in users))
        except TagNotFoundException:
            await ctx.send(f"<:B_down:773702309364367420> Group `{group}` does not exist!", ephemeral=True)

    @tag.command(
        name="add",
        description="Add a user to a tag."
    )
    @discord.app_commands.describe(
        users="The user to add to the tag.",
        group="The group to add the user to."
    )
    # @guild_admins_only()
    async def tag_add(self, ctx: commands.Context, users: commands.Greedy[discord.Member], group: str):
        group = group.lower()

        exists = []

        for user in users:
            try:
                await self.bot.database.join_tag(ctx.guild.id, group, user.id)
            except AlreadyInTagException:
                exists.append(user.id)

        await ctx.send(f"Added {len(users) - len(exists)} user(s) to group `{group}`! " + ((f" ".join(f"<@{user.id}>" for user in users) + " are already in the group.") if len(exists) else ""), ephemeral=True)

    @tag.command(
        name="members",
        description="Lists all the users under a tag."
    )
    @discord.app_commands.describe(
        group="The group to list."
    )
    async def tag_members(self, ctx: commands.Context, group: str):
        group = group.lower()

        try:
            users = await self.bot.database.get_users_in_tag(ctx.guild.id, group)
            embed = discord.Embed(
                color=0x2b2d31,
                description="\n".join(f"* <@{user}>" for user in users)).set_author(name=f"Users in '{group}'", icon_url=ctx.guild.icon)

            await ctx.send(embed=embed, ephemeral=True)
        except TagNotFoundException:
            await ctx.send(f"<:B_down:773702309364367420> Group `{group}` does not exist!", ephemeral=True)

    @tag.command(
        name="list",
        description="Lists all the tags a user is a part of."
    )
    @discord.app_commands.describe(
        user="The user to list tags for."
    )
    async def tag_list(self, ctx: commands.Context, user: discord.Member = None):
        if user is None:
            user = ctx.author
            print("saving")

        tags = await self.bot.database.get_tags_by_user(ctx.guild.id, user.id)

        if len(tags) == 0:
            await ctx.send(f"<:B_partial:773702309245878304> {user.mention} is not in any groups!", ephemeral=True)
            return

        embed = discord.Embed(
            color=0x2b2d31,
            description="\n".join(f"* **`{tag}`**" for tag in tags)).set_author(name=f"{user}'s tags", icon_url=user.avatar)

        await ctx.send(embed=embed, ephemeral=True)


async def setup(client) -> None:
    await client.add_cog(Tags(client))
