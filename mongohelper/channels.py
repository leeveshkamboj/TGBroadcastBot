from mongohelper import instance, logger
from umongo import Document, fields
from marshmallow.exceptions import ValidationError


@instance.register
class Channel(Document):
    chat_id = fields.IntegerField(attribute='_id')

    class Meta:
        collection_name = "channels"


async def in_channels(chat_id):
    try:
        user = await Channel.find_one({"chat_id": chat_id})
        if user:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


async def add_channel(chat_id):
    try:
        channel = Channel(
            chat_id=chat_id
        )
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
    else:
        try:
            await channel.commit()
        except DuplicateKeyError:
            logger.warning(f"{channel.chat_id} is already saved in database")
        else:
            logger.info(f"{channel.chat_id} is saved in database")


async def rm_channel(chat_id):
    try:
        channel = await Channel.find_one({"chat_id": chat_id})
        if channel:
            await channel.delete()

    except Exception as e:
        print(e)


async def get_all_channels():
    cursor = Channel.find()
    return await cursor.to_list(None)
