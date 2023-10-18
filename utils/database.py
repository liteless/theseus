from mongoengine import *


class Tag(EmbeddedDocument):
    name = StringField(required=True)
    members = ListField(IntField())


class Guild(Document):
    guild_id = IntField(required=True)
    admins = ListField(IntField())
    tags = EmbeddedDocumentListField(Tag)


class TagNotFoundException(Exception):
    pass


class NotInTagException(Exception):
    pass


class AlreadyInTagException(Exception):
    pass


class Database():
    def __init__(self, uri=None, db=None) -> None:
        assert uri is not None, "No URI provided."
        assert db is not None, "No database provided."
        # print(uri)
        connect(host=uri, db=db)

    async def list_tags(self, guild_id: int) -> dict:
        guild = Guild.objects(guild_id=guild_id).first()

        tags = {}

        if guild is None:
            return tags

        for tag in Guild.objects(guild_id=guild_id).first().tags:
            tags[tag.name] = len(tag.members)

        return tags

    async def join_tag(self, guild_id: int, tag_name: str, member_id: int) -> bool:
        guild = Guild.objects(guild_id=guild_id).first()
        new = False

        if guild is None:
            guild = Guild(guild_id=guild_id)
            new = True

        tag = guild.tags.filter(name=tag_name).first()

        if tag is None:
            guild.tags.append(Tag(name=tag_name, members=[member_id]))
        elif member_id in tag.members:
            raise AlreadyInTagException()
        else:
            tag.members.append(member_id)

        guild.save()

        return new

    async def leave_tag(self, guild_id: int, tag_name: str, member_id: int) -> bool:
        guild = Guild.objects(guild_id=guild_id).first()

        if guild is None:
            return TagNotFoundException()

        tag = guild.tags.filter(name=tag_name).first()

        if tag is None:
            raise TagNotFoundException()
        elif member_id not in tag.members:
            raise NotInTagException()

        tag.members.remove(member_id)
        empty = len(tag.members) == 0

        if empty:
            guild.tags.remove(tag)

        guild.save()

        return empty

    async def get_tags_by_user(self, guild_id: int, member_id: int) -> list:
        guild = Guild.objects(guild_id=guild_id).first()

        tags = []

        if guild is None:
            return tags

        for tag in guild.tags:
            if member_id in tag.members:
                tags.append(tag.name)

        return tags

    async def get_users_in_tag(self, guild_id: int, tag_name: str) -> list:
        guild = Guild.objects(guild_id=guild_id).first()

        if guild is None:
            guild = TagNotFoundException()

        tag = guild.tags.filter(name=tag_name).first()

        if tag is None:
            raise TagNotFoundException()

        return tag.members

    async def is_admin(self, guild_id: int, user: int) -> bool:
        guild = Guild.objects(guild_id=guild_id).first()

        if guild is None:
            return False

        return user in guild.admins
