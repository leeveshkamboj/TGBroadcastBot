from telethon.sync import TelegramClient
from telethon import events, Button, functions
from sqlhelper.channels import add_channel, rm_channel, in_channels, get_all_channels
from config import Config
import asyncio
import re


bot = TelegramClient('bot', Config.api_id, Config.api_hash).start(bot_token=Config.token)

default_start_msg = """To use this bot, add the bot in your channel aur send /add"""


@bot.on(events.NewMessage(func = lambda e: e.is_private, pattern=r'/start'))
async def handler(event):
    entity = await bot.get_entity(event.chat_id)
    first_name = entity.first_name
    button = [[(Button.url("Repo Link", "https://github.com/leeveshkamboj/TGBroadcastBot"))]] 
    if Config.start_msg:
        start_msg = Config.start_msg
    else:
        start_msg = default_start_msg
    msg = f"**Yo {first_name}**\n\n{start_msg}\n\nEnter /help for more commands"
    try:
        owner = await bot.get_entity(Config.ownerID)
        name = owner.name
        if name:
            msg += f"\n\n**Made By {name}**"
    except Exception as e:
        print(e)
    await bot.send_message(event.chat_id, msg, buttons = button)


@bot.on(events.NewMessage(func = lambda e: e.is_private, pattern=r'/help'))
async def handler(event):
    msg = "**Commands available-**\n\n/add - Add channel to database\n/rem - Remove channel from database"
    if event.chat_id == Config.ownerID:
        msg += "\n/send - Reply /send to any message to send it to all channels\n/list - to list all channels in database\n/clean - to clean database"
    await bot.send_message(event.chat_id, msg)


@bot.on(events.NewMessage(func = lambda e: e.is_channel, pattern = r'/add'))
async def handler(event):
    if in_channels(event.chat_id):
        try:
            reply = await event.reply("Already in database")
            await asyncio.sleep(3)
            await reply.delete()
            await event.delete()
        except:
            pass
    else:
        add_channel(event.chat_id)
        try:
            reply = await event.reply("Added to database")
        except:
            rm_channel(event.chat_id)
        try:
            await asyncio.sleep(3)
            await reply.delete()
            await event.delete()
        except:
            pass


@bot.on(events.NewMessage(pattern = (r'/rem(.*)')))
async def handler(event):
    if event.chat_id == Config.ownerID:
        ID = int(event.pattern_match.group(1))
    elif event.is_channel:
        ID = event.chat_id
    else:
        return
    if in_channels(ID):
        rm_channel(ID)
        try:
            await event.reply("Removed from database")
        except:
            pass
    else:
        try:
            await event.reply("Channel is not in database")
        except:
            pass


@bot.on(events.NewMessage(func = lambda e: e.is_private, pattern=r'/list'))
async def handler(event):
    channels = get_all_channels()
    if channels:
        msg = f"Total {len(channels)} channels=>\n\n"
        for channel in channels:
            try:
                channel_get = await bot.get_entity(channel.chat_id)
                name = channel_get.title
                username = channel_get.username
                if username:
                    msg += f"`{str(channel.chat_id)}` -  [{name}](https://telegram.me/{username})\n"
                else:
                    try:
                        link = await bot(functions.messages.ExportChatInviteRequest(channel.chat_id))
                        link = link.link
                        msg += f"`{str(channel.chat_id)}` -  [{name}]({link})\n"
                    except:
                        msg += f"`{str(channel.chat_id)} - {name}` \n"
            except Exception as e:
                print(e)
                msg += f"`{str(channel.chat_id)}` \n"
    else:
        msg = "Empty"
    if len(msg) > 4096:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "channels.txt"
            await bot.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="List of Channels."
            )
    else:
        await bot.send_message(event.chat_id, msg, link_preview = False)


@bot.on(events.NewMessage(func = lambda e: e.is_private, pattern=r'/clean'))
async def handler(event):
    msg = await bot.send_message(event.chat_id, "Cleaning...")
    channels = get_all_channels()
    for channel in channels:
        try:
            rm_channel(channel.chat_id)
        except:
            pass
    await msg.edit("Done")


@bot.on(events.NewMessage(func = lambda e: e.is_private, pattern=r'/send'))
async def handler(event):
    if event.chat_id != Config.ownerID:
        await bot.send_message(event.chat_id, "You are not my Owners.")
        return
    if event.reply_to_msg_id:
        broadcast_msg = await bot.send_message(event.chat_id, "Sending...")
        previous_message = await event.get_reply_message()
        if previous_message.poll:
            await broadcast_msg.edit("Polls not supported.")
            return
        channels = get_all_channels()
        count = 0
        errs = 0
        for channel in channels:
            try:
                if previous_message.photo:
                    photo = previous_message.media.photo
                    await bot.send_file(channel.chat_id, photo, caption = previous_message.text, link_preview = False)
                elif previous_message.media and not previous_message.media.webpage::
                    media = previous_message.media.document
                    await bot.send_file(channel.chat_id, media, caption = previous_message.text, link_preview = False)
                else:
                    await bot.send_message(channel.chat_id, previous_message.text, link_preview = False)
                count += 1
                percents = round(100.0 * count / float(len(channels)), 1)
                try:
                    await broadcast_msg.edit(f"Sending ({count}/{len(channels)})... [{percents}%]\n{errs} error(s) till now.")
                except:
                    pass
            except Exception as e:
                errs += 1
                if Config.log_id:
                    button = [[(Button.inline("Remove Now", data=f"remove_{channel.chat_id}"))]]
                    await bot.send_message(Config.log_id, f"Error in sending message to {channel.chat_id} - {e}", buttons = button)
                else:
                    print(e)
        await broadcast_msg.edit(f"Sent to {len(channels) - errs} channels with {errs} errors.")
    else:
        await event.send_message(event.chat_id, "Reply to a message to broadcast.")


@bot.on(events.callbackquery.CallbackQuery(data=re.compile(b"remove_(.*)")))
async def genAcc(event):
    ID = event.data_match.group(1).decode("UTF-8")
    if in_channels(ID):
        rm_channel(ID)
    await event.delete()


@bot.on(events.NewMessage(func = lambda e: e.is_private, pattern=r'yo'))
async def handler(event):
    await event.reply("Yo")



print("Bot Started")
bot.run_until_disconnected()
