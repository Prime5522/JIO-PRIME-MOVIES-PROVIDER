#don't remove credit please 
#this code design by https://t.me/Prime_Botz 
#developer https://t.me/Prime_Nayem
#Let me know if there is any problem while deploying it https://t.me/Prime_Nayem
#thank you for using this Code 

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from info import CHANNELS, MOVIE_UPDATE_CHANNEL, ADMINS, LOG_CHANNEL
from database.ia_filterdb import save_file, unpack_new_file_id
from utils import get_poster, temp
import re
from database.users_chats_db import db
#from pyrogram.types import CallbackQuery
processed_movies = set()
media_filter = filters.document | filters.video

# প্রতিটি মেসেজের জন্য রিঅ্যাকশন সংরক্ষণ করতে ডিকশনারি ব্যবহার করা হচ্ছে
reactions_data = {}

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    bot_id = bot.me.id
    media = getattr(message, message.media.value, None)
    if media.mime_type in ['video/mp4', 'video/x-matroska']:
        media.file_type = message.media.value
        media.caption = message.caption
        success_sts = await save_file(media)
        if success_sts == 'suc' and await db.get_send_movie_update_status(bot_id):
            file_id, file_ref = unpack_new_file_id(media.file_id)
            await send_movie_updates(bot, file_name=media.file_name, caption=media.caption, file_id=file_id)

async def get_imdb(file_name):
    imdb_file_name = await movie_name_format(file_name)
    imdb = await get_poster(imdb_file_name)
    if imdb:
        return imdb.get('poster'), imdb.get('title'), imdb.get('genres'), imdb.get('year'), imdb.get('rating')
    return None, None, None, None, None

async def movie_name_format(file_name):
    filename = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name).replace('_', ' ').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('{', '').replace('}', '').replace('.', ' ').replace('@', '').replace(':', '').replace(';', '').replace("'", '').replace('-', '').replace('!', '')).strip()
    return filename

async def check_qualities(text, qualities: list):
    quality = []
    for q in qualities:
        if q in text:
            quality.append(q)
    quality = ", ".join(quality)
    return quality[:-2] if quality.endswith(", ") else quality

async def detect_season_and_episode(caption, file_name):
    """ Improved regex patterns and matching with custom seasons and episodes. Defaults to 'Not Sure' if detection fails. """
    seasons = ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10", "Season 1", "Season 2", "Season 3", "Season 4", "Season 5", "Season 6", "Season 01", "Season 02", "Season 03", "Season 04", "Season 05", "Season 06", "Se01", "Se02", "Se03", "Se04", "Se05", "Se06", "Se07", "Se08", "Se09", "Se10", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "[S01]", "[S02]", "[S03]", "[S04]", "[S05]", "[S06]", "[S07]", "[S08]", "[S09]", "[S10]", "01x01", "02x01", "03x01", "04x01", "05x01", "06x01", "07x01", "08x01", "09x01", "10x01"]
    episodes = ["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "Episode 1", "Episode 2", "Episode 3", "Episode 4", "Episode 5", "Episode 6", "Episode 7", "Episode 8", "Episode 9", "Episode 10", "Ep 1", "Ep 2", "Ep 3", "Ep 4", "Ep 5", "Ep 6", "Ep 7", "Ep 8", "Ep 9", "Ep 10", "[E01]", "[E02]", "[E03]", "[E04]", "[E05]", "[E06]", "[E07]", "[E08]", "[E09]", "[E10]", "1x01", "1x02", "2x01", "2x02", "3x01", "3x02", "4x01", "4x02", "5x01", "5x02", "S01E01", "S01E02", "S02E01", "S02E02", "S03E01", "S03E02", "S04E01", "S04E02", "S05E01", "S05E02", "Se01E01", "Se01E02", "Se02E01", "Se02E02", "Se03E01", "Se03E02", "Se04E01", "Se04E02", "1x1", "1x2", "2x1", "2x2", "3x3", "4x3", "5x1", "5x2", "6x1", "6x2"]
    season_detected = "Not Sure"
    episode_detected = "Not Sure"
    for season in seasons:
        if season.lower() in caption.lower() or season.lower() in file_name.lower():
            season_detected = season
    for ep in episodes:
        if ep.lower() in caption.lower() or ep.lower() in file_name.lower():
            episode_detected = ep
    return season_detected, episode_detected

async def send_movie_updates(bot, file_name, caption, file_id):
    try:
        year_match = re.search(r"\b(19|20)\d{2}\b", caption)
        year = year_match.group(0) if year_match else None
        pattern = r"(?i)(?:s|season)0*(\d{1,2})"
        season = re.search(pattern, caption)
        if not season:
            season = re.search(pattern, file_name)
        if year:
            file_name = file_name[:file_name.find(year) + 4]
        if not year:
            if season:
                season = season.group(1) if season else None
            file_name = file_name[:file_name.find(season) + 1]

        qualities = ["ORG", "org", "hdcam", "HDCAM", "HQ", "hq", "HDRip", "hdrip", "camrip", "WEB-DL", "CAMRip", "hdtc", "predvd", "DVDscr", "dvdscr", "dvdrip", "dvdscr", "HDTC", "dvdscreen", "HDTS", "hdts"]
        quality = await check_qualities(caption.lower(), qualities) or "HDRip"

        language = ""
        nb_languages = ["Hindi", "Bengali", "Bangla", "Hin", "Ban", "বাংলা", "हिन्दी", "Eng", "Tam", "English", "Marathi", "Tamil", "Telugu", "Malayalam", "Kannada", "Punjabi", "Gujrati", "Korean", "Japanese", "Bhojpuri", "Dual", "Multi"]
        for lang in nb_languages:
            if lang.lower() in caption.lower():
                language += f"{lang}, "
        language = language.strip(", ") or "Not Sure"

        movie_name = await movie_name_format(file_name)
        if movie_name in processed_movies:
            return
        processed_movies.add(movie_name)

        season, episode = await detect_season_and_episode(caption, file_name)

        poster_url, title, genres, release_date, rating = await get_imdb(movie_name)

        # নতুন ডিজাইন অনুযায়ী ক্যাপশন
        caption_message = (
            f"📢 **#NEW_FILE_ADDED ✅**\n\n"
            f"➤✉ **𝐓𝐈𝐓𝐋𝐄:** {title or movie_name}\n"
            f"➤📁 **𝐋𝐀𝐍𝐆𝐔𝐀𝐆𝐄:** {language}\n"
            f"➤🔘 **𝐐𝐔𝐀𝐋𝐈𝐓𝐘:** {quality}\n"
            f"──────────────────────────"
        )

        # রিঅ্যাকশন বাটন
        message_id = file_id  # প্রতিটি মেসেজের জন্য আলাদা আইডি
        reactions_data[message_id] = {"like": 0, "thumbs_up": 0, "thumbs_down": 0, "fire": 0}

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"❤️ {reactions_data[message_id]['like']}", callback_data=f"like_{message_id}"),
                InlineKeyboardButton(f"👍 {reactions_data[message_id]['thumbs_up']}", callback_data=f"thumbs_up_{message_id}"),
                InlineKeyboardButton(f"👎 {reactions_data[message_id]['thumbs_down']}", callback_data=f"thumbs_down_{message_id}"),
                InlineKeyboardButton(f"🔥 {reactions_data[message_id]['fire']}", callback_data=f"fire_{message_id}")
            ],
            [InlineKeyboardButton("📂 GET FILE 📂", url=f"https://t.me/{temp.U_NAME}?start=pm_mode_file_{ADMINS[0]}_{file_id}")],
            [InlineKeyboardButton("♻ HOW TO GET FILE TUTORIAL ♻", url="https://t.me/Prime_Movie_Watch_Dawnload/75")]
        ])

        movie_update_channel = await db.movies_update_channel_id()

        if poster_url:
            await bot.send_photo(movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL,
                                 photo=poster_url, caption=caption_message, reply_markup=buttons)
        else:
            no_poster = "https://telegra.ph/file/88d845b4f8a024a71465d.jpg"
            await bot.send_photo(movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL,
                                 photo=no_poster, caption=caption_message, reply_markup=buttons)
    except Exception as e:
        print('Failed to send movie update. Error - ', e)
        await bot.send_message(LOG_CHANNEL, f'Failed to send movie update. Error - {e}')

@Client.on_callback_query()
async def handle_reactions(bot, query: CallbackQuery):
    data = query.data.split("_")  # রিঅ্যাকশন টাইপ ও মেসেজ আইডি বের করা
    if len(data) != 2:
        return

    reaction_type, message_id = data[0], int(data[1])

    if message_id in reactions_data:
        # রিঅ্যাকশন টাইপ অনুযায়ী সংখ্যা +1 আপডেট হবে
        if reaction_type in reactions_data[message_id]:
            reactions_data[message_id][reaction_type] += 1
        else:
            reactions_data[message_id][reaction_type] = 1  # যদি নতুন রিঅ্যাকশন টাইপ হয়

        # বাটন গুলি নতুন রিঅ্যাকশন কাউন্ট অনুযায়ী আপডেট
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"❤️ {reactions_data[message_id].get('like', 0)}", callback_data=f"like_{message_id}"),
                InlineKeyboardButton(f"👍 {reactions_data[message_id].get('thumbs_up', 0)}", callback_data=f"thumbs_up_{message_id}"),
                InlineKeyboardButton(f"👎 {reactions_data[message_id].get('thumbs_down', 0)}", callback_data=f"thumbs_down_{message_id}"),
                InlineKeyboardButton(f"🔥 {reactions_data[message_id].get('fire', 0)}", callback_data=f"fire_{message_id}")
            ],
            [InlineKeyboardButton("📂 GET FILE 📂", url=f"https://t.me/{temp.U_NAME}?start=pm_mode_file_{ADMINS[0]}_{message_id}")],
            [InlineKeyboardButton("♻ HOW TO GET FILE TUTORIAL ♻", url="https://t.me/Prime_Movie_Watch_Dawnload/75")]
        ])

        # নতুন রিঅ্যাকশন কাউন্ট সহ বাটন আপডেট
        await query.message.edit_reply_markup(reply_markup=buttons)
