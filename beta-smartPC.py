'''
Software Use License

Copyright © 2024 Dmitry Lesin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to use the Software subject to the following conditions:

Copyright Notice and Permission
The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

Restrictions on Use and Distribution
The licensee may not:

• Sell, transfer, or sublicense the Software in any form, including modified versions.
• Use the Software for commercial purposes without prior written consent from the Licensor.
• Modify, adapt, create derivative works based on the Software, or distribute such works
without prior written consent from the Licensor.

Personal Use
The Software may only be used for personal, non-commercial purposes. Commercial use of the Software
in any project is prohibited without prior written consent from the Licensor.

Disclaimer
The Software is provided "as is," without any warranties, express or implied, including but not
limited to warranties of merchantability, fitness for a particular purpose, and non-infringement.
In no event shall the authors or copyright holders be liable for any claims, damages, or other
liabilities, whether in an action of contract, tort, or otherwise, arising from, out of, or in
connection with the Software or the use or other dealings in the Software.
'''



import sys
import threading
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram import F
import asyncio
import webbrowser
import random
import os
import time
import sounddevice as sd
import scipy.io.wavfile as wav
import mss
import pyautogui
import keyboard
import platform
import psutil
import requests
import re
import pygetwindow as gw

# Write your Telegram bot token
API_TOKEN = " "
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Enter your IP
user_ids = []

youtube_context = {}
user_notifications = {}
user_data = {}

youtube_pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$"
url_pattern = r"^(https?://)?[^\s/$.?#].[^\s]*$"
disk_d_path = "D:/"

voiceover_enabled_en = False
voiceover_enabled_ru = False
voiceover_status = {
    "ru": False,
    "en": False,
}

# enter the SHODAN IP
SHODAN_API_KEY = " "

authorized_user_id = None

def is_authorized(message):
    # Check if the chat ID matches the authorized one
    return str(message.chat.id) == authorized_user_id


@dp.message(Command("start"))
async def start_command(message: types.Message):
    if is_authorized(message):
        btn_en = InlineKeyboardButton(text="🇬🇧", callback_data="lang_en")
        btn_ru = InlineKeyboardButton(text="🇷🇺", callback_data="lang_ru")
        markup_start = InlineKeyboardMarkup(inline_keyboard=[[btn_en, btn_ru]])

        # Sending a message with the keyboard
        await message.answer(
            """👋 I’m your assistant, ready to help you with PC management and much more. 
To get started, please choose your preferred language. 🌍:\n\n
👋 Я — ваш помощник, готов помочь вам с управлением ПК и многим другим. 
Для начала, пожалуйста, выбери язык, с которым тебе удобнее работать. 🌍""",
            reply_markup=markup_start,
        )
    else:
        access = await message.reply("Доступ запрещён!")
        await asyncio.sleep(15)
        await access.delete()


@dp.callback_query(lambda call: call.data in ['lang_en', 'lang_ru'])
async def choose_language(call: types.CallbackQuery):
    if call.data == 'lang_en':
        await call.message.delete()
        global voiceover_enabled_en

        # Saving the user's choice (voice acting is enabled by default)
        voiceover_enabled_en = True

        voiceover_en_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Yes✅", callback_data="btn_voiceover_en_yes")],
                [InlineKeyboardButton(text="No❌", callback_data="btn_voiceover_en_no")]
            ]
        )

        await call.message.answer(
            "You selected English. Do you want to use Jarvis's voice acting?🎙️",
            reply_markup=voiceover_en_markup
        )
    elif call.data == 'lang_ru':
        await call.message.delete()
        global voiceover_enabled_ru

        # Saving the user's choice (voice acting is enabled by default)
        voiceover_enabled_ru = True

        voiceover_ru_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Да✅", callback_data="btn_voiceover_ru_yes")],
                [InlineKeyboardButton(text="Нет❌", callback_data="btn_voiceover_ru_no")]
            ]
        )

        await call.message.answer(
            "Вы выбрали русский. Хотите использовать озвучку Jarvis?🎙️",
            reply_markup=voiceover_ru_markup
        )


@dp.callback_query(lambda call: call.data == 'btn_voiceover_en_yes')
async def enable_voiceover_en(call: types.CallbackQuery):
    await call.message.delete()
    global voiceover_enabled_en
    voiceover_enabled_en = True
    markup_en_cont = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Continue", callback_data="en_cont")]
        ]
    )
    await call.message.answer("Voice acting enabled!🔊 Now you can continue➡️", reply_markup=markup_en_cont)


@dp.callback_query(lambda call: call.data == 'btn_voiceover_en_no')
async def disable_voiceover_en(call: types.CallbackQuery):
    await call.message.delete()
    global voiceover_enabled_en
    voiceover_enabled_en = False
    markup_en_cont = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Continue", callback_data="en_cont")]
        ]
    )
    await call.message.answer("Voice acting disabled!🔇 Now you can continue➡️", reply_markup=markup_en_cont)


@dp.callback_query(lambda call: call.data == 'btn_voiceover_ru_yes')
async def enable_voiceover_ru(call: types.CallbackQuery):
    await call.message.delete()
    global voiceover_enabled_ru
    voiceover_enabled_ru = True
    markup_ru_cont = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="ru_cont")]
        ]
    )
    await call.message.answer("Включена озвучка!🔊 Теперь вы можете продолжать➡️", reply_markup=markup_ru_cont)


@dp.callback_query(lambda call: call.data == 'btn_voiceover_ru_no')
async def disable_voiceover_ru(call: types.CallbackQuery):
    await call.message.delete()
    global voiceover_enabled_ru
    voiceover_enabled_ru = False

    markup_ru_cont = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="ru_cont")]
        ]
    )
    await call.message.answer("Озвучка отключена!🔇 Теперь вы можете продолжать➡️", reply_markup=markup_ru_cont)


@dp.callback_query(lambda call: call.data == 'en_cont')
async def cont_en(call: types.CallbackQuery):
    await call.message.delete()

    try:
        photo = FSInputFile("assets/image/jarvis.jpg")

        btn_main_en = InlineKeyboardButton(text="Basic commands ⚙️", callback_data="main_commands_en")
        btn_apps_en = InlineKeyboardButton(text="Applications 📱", callback_data="apps_commands_en")
        apps_youtube_en = InlineKeyboardButton(text="YouTube ▶️", callback_data="apps_youtube_en")
        btn_sait_en = InlineKeyboardButton(text="Sites 🌐", callback_data="sait_commands_en")
        btn_my_computer_en = InlineKeyboardButton(text="About my computer", callback_data="my_computer_en")
        btn_personal_account_en = InlineKeyboardButton(text="Personal account", callback_data="personal_account_en")
        btn_telegraph_en = InlineKeyboardButton(text="Basic information",
                                                url="https://telegra.ph/smartPC-Your-Smart-Assistant-for-PC-Management-in-Jarvis-Style-11-21")
        markup_en = InlineKeyboardMarkup(inline_keyboard=[
            [btn_main_en, btn_apps_en],
            [apps_youtube_en, btn_sait_en],
            [btn_my_computer_en],
            [btn_personal_account_en],
            [btn_telegraph_en]
        ])

        await call.message.answer_photo(
            photo=photo,
            caption="Below are the sections with the available functions for your PC:",
            reply_markup=markup_en
        )
    except Exception as e:
        error = await call.message.answer(f"An error has occurred: {str(e)}")
        await asyncio.sleep(15)
        await error.delete()


@dp.callback_query(lambda call: call.data == 'ru_cont')
async def cont_ru(call: types.CallbackQuery):
    await call.message.delete()

    try:
        photo = FSInputFile("assets/image/jarvis.jpg")

        btn_main_ru = InlineKeyboardButton(text="Основные команды ⚙️", callback_data="main_commands_ru")
        btn_apps_ru = InlineKeyboardButton(text="Приложения 📱", callback_data="apps_commands_ru")
        apps_youtube_ru = InlineKeyboardButton(text="YouTube ▶️", callback_data="apps_youtube_ru")
        btn_sait_ru = InlineKeyboardButton(text="Сайты 🌐", callback_data="sait_commands_ru")
        btn_my_computer_ru = InlineKeyboardButton(text="Про мой компьютер", callback_data="my_computer_ru")
        btn_personal_account_ru = InlineKeyboardButton(text="Личный кабинет", callback_data="personal_account_ru")
        btn_telegraph_ru = InlineKeyboardButton(text="Основная информация",
                                                url="https://telegra.ph/smartPC-Vash-lichnyj-pomoshchnik-po-upravleniyu-PK-v-stile-Dzharvisa-11-21")
        markup_ru = InlineKeyboardMarkup(inline_keyboard=[
            [btn_main_ru, btn_apps_ru],
            [apps_youtube_ru, btn_sait_ru],
            [btn_my_computer_ru],
            [btn_personal_account_ru],
            [btn_telegraph_ru]
        ])

        await call.message.answer_photo(
            photo=photo,
            caption="Ниже представлены разделы с доступными функциями для вашего ПК:",
            reply_markup=markup_ru
        )
    except Exception as e:
        error = await call.message.answer(f"Произошла ошибка: {str(e)}")
        await asyncio.sleep(15)
        await error.sleep()


@dp.callback_query(lambda call: call.data == 'main_commands_en')
async def main_commands_en(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("""Basic commands:\n
""", reply_markup=markup_main_en)


@dp.callback_query(lambda call: call.data == 'main_commands_ru')
async def main_commands_ru(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("""Основные команды:\n
    """, reply_markup=markup_main_ru)


btn_back_en = InlineKeyboardButton(text="Back🔙", callback_data="btn_back_en")
btn_shutdown_en = InlineKeyboardButton(text="Completion of work ✅", callback_data="btn_shutdown_en")
btn_restart_en = InlineKeyboardButton(text="Reboot 🔄", callback_data="btn_restart_en")
btn_lock_en = InlineKeyboardButton(text="Screen Lock 👀", callback_data="btn_lock_en")
btn_screenshot_en = InlineKeyboardButton(text="Screenshot 📸", callback_data="btn_screenshot_en")
btn_switch_layout_en = InlineKeyboardButton(text="Change the language 🌐", callback_data="btn_switch_layout_en")
btn_collapse_en = InlineKeyboardButton(text="Minimize all windows 🖱️", callback_data="btn_collapse_en")
btn_scroll_up_en = InlineKeyboardButton(text="Scroll up ⬆️", callback_data="btn_scroll_up_en")
btn_scroll_down_en = InlineKeyboardButton(text="Scroll down ⬇️", callback_data="btn_scroll_down_en")
btn_full_screen_en = InlineKeyboardButton(text="Full screen 🖥️", callback_data="btn_full_screen_en")
btn_empty_trash_en = InlineKeyboardButton(text="Cleaning the trash 🗑️", callback_data="btn_empty_trash_en")
markup_main_en = InlineKeyboardMarkup(inline_keyboard=[
    [btn_back_en],
    [btn_shutdown_en],
    [btn_restart_en],
    [btn_lock_en],
    [btn_screenshot_en],
    [btn_collapse_en],
    [btn_scroll_up_en, btn_scroll_down_en],
    [btn_full_screen_en],
    [btn_empty_trash_en],
])


@dp.callback_query(F.data == 'btn_back_en')
async def go_back_en(call: CallbackQuery):
    if is_authorized(call.message):
        await cont_en(call)
    else:
        access = await call.message.answer("Access is denied!")
        await asyncio.sleep(15)
        await access.delete()


# Completion of work in English
@dp.callback_query(F.data == 'btn_shutdown_en')
async def shutdown_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return

    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/i-am-switching-off.wav"]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        shutdown = await call.message.reply("Turning off the PC...")

        os.system("shutdown /s /t 1")

        await asyncio.sleep(30)
        await shutdown.delete()
    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Restart in English
@dp.callback_query(F.data == 'btn_restart_en')
async def restart_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return

    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/i-am-switching-off.wav"]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        restart = await call.message.reply("Rebooting the PC")

        os.system("shutdown /r /t 1")

        await asyncio.sleep(30)
        await restart.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Lock screen in English
@dp.callback_query(F.data == 'btn_lock_en')
async def lock_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return
    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/i-am-doing-a-reboot.wav"]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        lock = await call.message.reply("The screen is locked")

        os.system("rundll32 user32.dll,LockWorkStation")

        await asyncio.sleep(30)
        await lock.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Screenshot in English
@dp.callback_query(F.data == 'btn_screenshot_en')
async def screenshot_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return

    try:
        screenshot_path = "screenshot.png"
        with mss.mss() as sct:
            sct.shot(output=screenshot_path)

        photo = FSInputFile(screenshot_path)
        await call.message.answer_photo(photo)

        os.remove(screenshot_path)

    except Exception as e:
        await call.message.reply(f"Error occurred: {str(e)}")


# Change the language to English
@dp.callback_query(F.data == 'btn_switch_layout_en')
async def switch_layout_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return
    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/the-language-has-been-changed.wav"]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        layout = await call.message.reply("The keyboard layout has been changed!")

        pyautogui.hotkey('win', 'space')

        await asyncio.sleep(30)
        await layout.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Minimize windows in English
@dp.callback_query(F.data == 'btn_collapse_en')
async def collapse_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return
    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav"]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        collapse = await call.message.reply("The windows are rolled up")

        pyautogui.hotkey('win', 'm')

        await asyncio.sleep(30)
        await collapse.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Scroll up in English
@dp.callback_query(F.data == 'btn_scroll_up_en')
async def scroll_up(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return
    scroll = await call.message.reply("Scroll up")
    pyautogui.scroll(745)
    await asyncio.sleep(3)
    await scroll.delete()


# Scroll down in English
@dp.callback_query(F.data == 'btn_scroll_down_en')
async def scroll_down(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return
    scroll = await call.message.reply("Scroll down")
    pyautogui.scroll(-745)
    await asyncio.sleep(3)
    await scroll.delete()


# Full screen in English
@dp.callback_query(F.data == 'btn_full_screen_en')
async def full_screen_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return
    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav"]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        screen = await call.message.reply("The full screen is completed")

        pyautogui.hotkey('win', 'up')

        await asyncio.sleep(30)
        await screen.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Empty the trash in English
@dp.callback_query(F.data == 'btn_empty_trash_en')
async def empty_trash_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return
    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/the-cleanup-was-successful.wav"]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        os.system('PowerShell -Command "Clear-RecycleBin -Force"')

        trash = await call.message.reply("The trash has been successfully cleared!")

        await asyncio.sleep(30)
        await trash.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


btn_back_ru = InlineKeyboardButton(text="Назад🔙", callback_data="btn_back_ru")
btn_shutdown_ru = InlineKeyboardButton(text="Завершение работы✅", callback_data="btn_shutdown_ru")
btn_rstart_ru = InlineKeyboardButton(text="Перезагрузка 🔄", callback_data="btn_restart_ru")
btn_lock_ru = InlineKeyboardButton(text="Блокировка экрана 👀", callback_data="btn_lock_ru")
btn_screenshot_ru = InlineKeyboardButton(text="Скриншот 📸", callback_data="btn_screenshot_ru")
btn_switch_layout_ru = InlineKeyboardButton(text="Сменить язык 🌐", callback_data="btn_switch_layout_ru")
btn_collapse_ru = InlineKeyboardButton(text="Свернуть все окна 🖱️", callback_data="btn_collapse_ru")
btn_scroll_up_ru = InlineKeyboardButton(text="Скролл вверх ⬆️", callback_data="btn_scroll_up_ru")
btn_scroll_down_ru = InlineKeyboardButton(text="Скролл вниз ⬇️", callback_data="btn_scroll_down_ru")
btn_full_screen_ru = InlineKeyboardButton(text="Полный экран 🖥️", callback_data="btn_full_screen_ru")
btn_empty_trash_ru = InlineKeyboardButton(text="Очистить корзину 🗑️", callback_data="btn_empty_trash_ru")
btn_create_folder_ru = InlineKeyboardButton(text="Создать папку", callback_data="btn_create_folder_ru")
markup_main_ru = InlineKeyboardMarkup(inline_keyboard=[
    [btn_back_ru],
    [btn_shutdown_ru],
    [btn_rstart_ru],
    [btn_lock_ru],
    [btn_screenshot_ru],
    [btn_switch_layout_ru],
    [btn_collapse_ru],
    [btn_scroll_up_ru, btn_scroll_down_ru],
    [btn_full_screen_ru],
    [btn_empty_trash_ru],
])


@dp.callback_query(F.data == 'btn_back_ru')
async def go_back_ru(call: CallbackQuery):
    if is_authorized(call.message):
        await cont_ru(call)
    else:
        access = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(15)
        await access.delete()


# The Shutdown button in Russian and the command "/shutdown"
@dp.callback_query(lambda call: call.data == 'btn_shutdown_ru')
@dp.message(Command("shutdown"))
async def shutdown_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["sounds/Отключаю питание.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            shutdown = await message.reply("Выключение ПК...")
            os.system("shutdown /s /t 1")

            await asyncio.sleep(30)
            await shutdown.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Restart" button in Russian and the "/restart" command
@dp.callback_query(lambda call: call.data == 'btn_restart_ru')
@dp.message(Command("restart"))
async def restart_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/Отключаю питание, начинаю диагностику системы.wav",
                               "assets/sounds/Начинаю диагностику системы.wav",
                               "assets/sounds/Начинаю диагностику системы (второй).wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            restart = await message.reply("Перезагрузка ПК")

            os.system("shutdown /r /t 1")

            await asyncio.sleep(30)
            await restart.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Lock screen" button in Russian and the "/lock" command
@dp.callback_query(lambda call: call.data == 'btn_lock_ru')
@dp.message(Command("lock"))
async def lock_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/Отключаю питание.wav",
                               "assets/sounds/как-пожелаете.wav", ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            lock = await message.reply("Экран заблокирован")

            os.system("rundll32 user32.dll,LockWorkStation")

            await asyncio.sleep(30)
            await lock.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Screenshot" button in Russian and the "/screenshot" command
@dp.callback_query(lambda call: call.data == 'btn_screenshot_ru')
@dp.message(Command("screenshot"))
async def screenshot_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            screenshot_path = "screenshot.png"
            with mss.mss() as sct:
                sct.shot(output=screenshot_path)

            photo = FSInputFile(screenshot_path)
            await message.answer_photo(photo)

            os.remove(screenshot_path)
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Change language" button in Russian and the command "/switch_layout"
@dp.callback_query(lambda call: call.data == 'btn_switch_layout_ru')
@dp.message(Command("switch_layout"))
async def switch_layout_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/есть.wav",
                               "assets/sounds/да-сэр-два.wav",
                               "assets/sounds/Всегда к вашим услугам сэр.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            pyautogui.hotkey('win', 'space')

            layout = await message.reply("Раскладка клавиатуры изменена!")

            await asyncio.sleep(30)
            await layout.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Minimize windows" button in Russian and the "/collapse" command
@dp.callback_query(lambda call: call.data == 'btn_collapse_ru')
@dp.message(Command("collapse"))
async def collapse_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/есть.wav",
                               "assets/sounds/да-сэр.wav",
                               "assets/sounds/Запрос выполнен сэр.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            collapse_msg = await message.reply("Окна свернуты")

            keyboard.send('win+m')

            await asyncio.sleep(30)
            await collapse_msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Scroll up" button in Russian and the command "/scroll_up"
@dp.callback_query(lambda call: call.data == 'btn_scroll_up_ru')
@dp.message(Command("scroll_up"))
async def scroll_up_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            scroll = await message.reply("Scroll выполнен наверх")
            pyautogui.scroll(745)
            await asyncio.sleep(3)
            await scroll.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Scroll down" button in Russian and the "/scroll_down" command
@dp.callback_query(lambda call: call.data == 'btn_scroll_down_ru')
@dp.message(Command("scroll_down"))
async def scroll_down_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            scroll = await message.reply("Scroll выполнен вниз")
            pyautogui.scroll(-745)
            await asyncio.sleep(3)
            await scroll.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The Full screen button in Russian and the command "/full_screen"
@dp.callback_query(lambda call: call.data == 'btn_full_screen_ru')
@dp.message(Command("full_screen"))
async def full_screen_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/есть.wav",
                               "assets/sounds/да-сэр-два.wav",
                               "assets/sounds/Всегда к вашим услугам сэр.wav",
                               "assets/sounds/как-пожелаете.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            screen = await message.reply("Полный экран")

            pyautogui.hotkey('win', 'up')

            await asyncio.sleep(30)
            await screen.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Empty trash" button in Russian and the command "/empty_trash"
@dp.callback_query(lambda call: call.data == 'btn_empty_trash_ru')
@dp.message(Command("empty_trash"))
async def empty_trash_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/есть.wav",
                               "assets/sounds/Всегда к вашим услугам сэр.wav",
                               "assets/sounds/как-пожелаете.wav",
                               "assets/sounds/Запрос выполнен сэр.wav",
                               "assets/sounds/Начинаю диагностику системы.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            os.system('PowerShell -Command "Clear-RecycleBin -Force"')

            trash = await message.reply("Корзина успешно очищена!")

            await asyncio.sleep(30)
            await trash.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# APPLICATION COMMANDS IN ENGLISH
@dp.callback_query(lambda call: call.data == 'apps_commands_en')
async def apps_commands_en(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("""Application Commands:\n
""", reply_markup=markup_app_en)


btn_back_en = InlineKeyboardButton(text="Back🔙", callback_data="btn_back_en")
btn_telegram_en = InlineKeyboardButton(text="Telegram✈️", callback_data="btn_telegram_en")
btn_chrome_en = InlineKeyboardButton(text="Google Chrome🌐🔍", callback_data="btn_chrome_en")
btn_opera_en = InlineKeyboardButton(text="Opera🌍", callback_data="btn_opera_en")
btn_edge_en = InlineKeyboardButton(text="Microsoft Edge🔍", callback_data="btn_edge_en")
btn_firefox_en = InlineKeyboardButton(text="Firefox🦊🌍", callback_data="btn_firefox_en")
btn_discord_en = InlineKeyboardButton(text="Discord💬🎧", callback_data="btn_discord_en")
btn_steam_en = InlineKeyboardButton(text="Steam🎮🔥", callback_data="btn_steam_en")
btn_console_en = InlineKeyboardButton(text="Console🖥️", callback_data="btn_console_en")
markup_app_en = InlineKeyboardMarkup(inline_keyboard=[
    [btn_back_en],
    [btn_telegram_en],
    [btn_chrome_en],
    [btn_opera_en],
    [btn_edge_en],
    [btn_firefox_en],
    [btn_discord_en],
    [btn_steam_en],
    [btn_console_en]
])


# Back button in English
@dp.callback_query(F.data == 'btn_back_en')
async def go_back_en(call: CallbackQuery):
    if is_authorized(call.message):
        await cont_en(call)
    else:
        access = await call.message.answer("Access is denied!")
        await asyncio.sleep(15)
        await access.delete()


# Telegram button in English
@dp.callback_query(F.data == 'btn_telegram_en')
async def telegram_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return

    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/opening-telegram.wav",
                           "assets/js/of-course.wav",
                           "assets/js/yes-sir.wav",
                           "assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/i-am-launching-a-telegram.wav",
                           "assets/js/application-launched-successfully-ready-to-execute-commands.wav",
                           "assets/js/command-executed-successfully-what-is-next.wav",
                           "assets/js/executing-your-command-please-hold-on.wav",
                           "assets/js/processing-complete-ready-for-the-next-step.wav",
                           "assets/js/task-completed-you-may-proceed.wav",
                           "assets/js/your-request-has-been-received-beginning-execution.wav",
                           "assets/js/your-request-is-my-priority-starting-work-now.wav"]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        app = await call.message.answer("Launching Telegram", reply_markup=btn_exit_telegram_en)
        pyautogui.press("win")
        time.sleep(1)
        keyboard.write("Telegram")
        time.sleep(1)
        pyautogui.press('enter')

        await asyncio.sleep(30)
        await app.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Google Chrome button in English
@dp.callback_query(F.data == 'btn_chrome_en')
async def chrome_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return

    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/i-open-google-chrome.wav",
                           "assets/js/of-course.wav",
                           "assets/js/yes-sir.wav",
                           "assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/application-launched-successfully-ready-to-execute-commands.wav",
                           "assets/js/command-executed-successfully-what-is-next.wav",
                           "assets/js/executing-your-command-please-hold-on.wav",
                           "assets/js/processing-complete-ready-for-the-next-step.wav",
                           "assets/js/task-completed-you-may-proceed.wav",
                           "assets/js/your-request-has-been-received-beginning-execution.wav",
                           "assets/js/your-request-is-my-priority-starting-work-now.wav"
                           ]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        app = await call.message.reply("Launching Google Chrome", reply_markup=btn_exit_chrome_en)
        pyautogui.press("win")
        time.sleep(1)
        keyboard.write("Google Chrome")
        time.sleep(1)
        pyautogui.press('enter')

        await asyncio.sleep(30)
        await app.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Opera button in English
@dp.callback_query(F.data == 'btn_opera_en')
async def opera_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return
    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/launching-opera.wav",
                           "assets/js/of-course.wav",
                           "assets/js/yes-sir.wav",
                           "assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/application-launched-successfully-ready-to-execute-commands.wav",
                           "assets/js/command-executed-successfully-what-is-next.wav",
                           "assets/js/executing-your-command-please-hold-on.wav",
                           "assets/js/processing-complete-ready-for-the-next-step.wav",
                           "assets/js/task-completed-you-may-proceed.wav",
                           "assets/js/your-request-has-been-received-beginning-execution.wav",
                           "assets/js/your-request-is-my-priority-starting-work-now.wav"
                           ]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        app = await call.message.reply("Launching Opera", reply_markup=btn_exit_opera_en)
        pyautogui.press("win")
        time.sleep(1)
        keyboard.write("Opera")
        time.sleep(1)
        pyautogui.press('enter')

        await asyncio.sleep(30)
        await app.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Edge button in English
@dp.callback_query(F.data == 'btn_edge_en')
async def edge_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return

    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/of-course.wav",
                           "assets/js/yes-sir.wav",
                           "assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/application-launched-successfully-ready-to-execute-commands.wav",
                           "assets/js/command-executed-successfully-what-is-next.wav",
                           "assets/js/executing-your-command-please-hold-on.wav",
                           "assets/js/processing-complete-ready-for-the-next-step.wav",
                           "assets/js/task-completed-you-may-proceed.wav",
                           "assets/js/your-request-has-been-received-beginning-execution.wav",
                           "assets/js/your-request-is-my-priority-starting-work-now.wav"
                           ]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        app = await call.message.reply("Launching Microsoft Edge", reply_markup=btn_exit_edge_en)
        pyautogui.press("win")
        time.sleep(1)
        keyboard.write("Microsoft Edge")
        time.sleep(1)
        pyautogui.press('enter')

        await asyncio.sleep(30)
        await app.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Firefox button in English
@dp.callback_query(F.data == 'btn_firefox_en')
async def firefox_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return

    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/of-course.wav",
                           "assets/js/yes-sir.wav",
                           "assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/application-launched-successfully-ready-to-execute-commands.wav",
                           "assets/js/command-executed-successfully-what-is-next.wav",
                           "assets/js/executing-your-command-please-hold-on.wav",
                           "assets/js/processing-complete-ready-for-the-next-step.wav",
                           "assets/js/task-completed-you-may-proceed.wav",
                           "assets/js/your-request-has-been-received-beginning-execution.wav",
                           "assets/js/your-request-is-my-priority-starting-work-now.wav"
                           ]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        app = await call.message.reply("Launching Firefox", reply_markup=btn_exit_firefox_en)
        pyautogui.press("win")
        time.sleep(1)
        keyboard.write("Firefox")
        time.sleep(1)
        pyautogui.press('enter')

        await asyncio.sleep(30)
        await app.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Discord button in English
@dp.callback_query(F.data == 'btn_discord_en')
async def discord_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return

    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/of-course.wav",
                           "assets/js/yes-sir.wav",
                           "assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/application-launched-successfully-ready-to-execute-commands.wav",
                           "assets/js/command-executed-successfully-what-is-next.wav",
                           "assets/js/executing-your-command-please-hold-on.wav",
                           "assets/js/processing-complete-ready-for-the-next-step.wav",
                           "assets/js/task-completed-you-may-proceed.wav",
                           "assets/js/your-request-has-been-received-beginning-execution.wav",
                           "assets/js/your-request-is-my-priority-starting-work-now.wav"
                           ]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        app = await call.message.reply("Launching Discord", reply_markup=btn_exit_discord_en)
        pyautogui.press("win")
        time.sleep(1)
        keyboard.write("Discord")
        time.sleep(1)
        pyautogui.press('enter')

        await asyncio.sleep(30)
        await app.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Steam button in English
@dp.callback_query(F.data == 'btn_steam_en')
async def steam_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return

    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/of-course.wav",
                           "assets/js/yes-sir.wav",
                           "assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/application-launched-successfully-ready-to-execute-commands.wav",
                           "assets/js/command-executed-successfully-what-is-next.wav",
                           "assets/js/executing-your-command-please-hold-on.wav",
                           "assets/js/processing-complete-ready-for-the-next-step.wav",
                           "assets/js/task-completed-you-may-proceed.wav",
                           "assets/js/your-request-has-been-received-beginning-execution.wav",
                           "assets/js/your-request-is-my-priority-starting-work-now.wav"
                           ]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        app = await call.message.reply("Launching Steam", reply_markup=btn_exit_steam_en)
        pyautogui.press("win")
        time.sleep(1)
        keyboard.write("Steam")
        time.sleep(1)
        pyautogui.press('enter')

        await asyncio.sleep(30)
        await app.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# console button in English
@dp.callback_query(F.data == 'btn_console_en')
async def console_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return

    try:
        if voiceover_enabled_en:
            sound_files = ["assets/js/of-course.wav",
                           "assets/js/yes-sir.wav",
                           "assets/js/as-you-wish-sir.wav",
                           "assets/js/yes-sir-1.wav",
                           "assets/js/application-launched-successfully-ready-to-execute-commands.wav",
                           "assets/js/command-executed-successfully-what-is-next.wav",
                           "assets/js/executing-your-command-please-hold-on.wav",
                           "assets/js/processing-complete-ready-for-the-next-step.wav",
                           "assets/js/task-completed-you-may-proceed.wav",
                           "assets/js/your-request-has-been-received-beginning-execution.wav",
                           "assets/js/your-request-is-my-priority-starting-work-now.wav"
                           ]
            sound_path = random.choice(sound_files)
            rate, data = wav.read(sound_path)
            sd.play(data, rate)
            sd.wait()

        app = await call.message.reply("Launching Console", reply_markup=btn_exit_console_en)
        os.system("start cmd")

        await asyncio.sleep(30)
        await app.delete()

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# APPLICATION COMMANDS IN RUSSIAN
@dp.callback_query(lambda call: call.data == 'apps_commands_ru')
async def apps_commands_ru(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("""Команды по приложениям:\n
""", reply_markup=markup_app_ru)


btn_back_ru = InlineKeyboardButton(text="Назад 🔙", callback_data="btn_back_ru")
btn_telegram_ru = InlineKeyboardButton(text="Telegram ✈️", callback_data="btn_telegram_ru")
btn_chrome_ru = InlineKeyboardButton(text="Google Chrome 🌐", callback_data="btn_chrome_ru")
btn_opera_ru = InlineKeyboardButton(text="Opera 🌍", callback_data="btn_opera_ru")
btn_edge_ru = InlineKeyboardButton(text="Microsoft Edge 🔍", callback_data="btn_edge_ru")
btn_firefox_ru = InlineKeyboardButton(text="Firefox 🦊", callback_data="btn_firefox_ru")
btn_discord_ru = InlineKeyboardButton(text="Discord 💬", callback_data="btn_discord_ru")
btn_steam_ru = InlineKeyboardButton(text="Steam 🎮", callback_data="btn_steam_ru")
btn_console_ru = InlineKeyboardButton(text="Консоль 🖥️", callback_data="btn_console_ru")
markup_app_ru = InlineKeyboardMarkup(inline_keyboard=[
    [btn_back_ru],
    [btn_telegram_ru],
    [btn_chrome_ru],
    [btn_opera_ru],
    [btn_edge_ru],
    [btn_firefox_ru],
    [btn_discord_ru],
    [btn_steam_ru],
    [btn_console_ru]
])


# Back button in Russian
@dp.callback_query(F.data == 'btn_back_ru')
async def go_back_ru(call: CallbackQuery):
    if is_authorized(call.message):
        await cont_ru(call)
    else:
        access = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(15)
        await access.delete()


# The "Telegram" button in Russian and the "/telegram" command
@dp.callback_query(lambda call: call.data == 'btn_telegram_ru')
@dp.message(Command("telegram"))
async def telegram_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.wav",
                               "assets/sounds/Загружаю-сэр.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            app = await message.reply("Запуск Telegram", reply_markup=btn_exit_telegram_ru)
            pyautogui.press("win")
            time.sleep(1)
            keyboard.write("Telegram")
            time.sleep(1)
            pyautogui.press('enter')

            await asyncio.sleep(30)
            await app.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Google_chrome" button in Russian and the "/google_chrome" command
@dp.callback_query(lambda call: call.data == 'btn_chrome_ru')
@dp.message(Command("google_chrome"))
async def google_chrome_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.wav",
                               "assets/sounds/Загружаю-сэр.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            app = await message.reply("Запуск Google Chrome", reply_markup=btn_exit_chrome_ru)
            pyautogui.press("win")
            time.sleep(1)
            keyboard.write("Google Chrome")
            time.sleep(1)
            pyautogui.press('enter')

            await asyncio.sleep(30)
            await app.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Opera" button in Russian and the "/opera" command
@dp.callback_query(lambda call: call.data == 'btn_opera_ru')
@dp.message(Command("opera"))
async def opera_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.wav",
                               "assets/sounds/Загружаю-сэр.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            app = await message.reply("Запуск Opera", reply_markup=btn_exit_opera_ru)
            pyautogui.press("win")
            time.sleep(1)
            keyboard.write("Opera")
            time.sleep(1)
            pyautogui.press('enter')

            await asyncio.sleep(30)
            await app.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Edge" button in Russian and the "/edge" command
@dp.callback_query(lambda call: call.data == 'btn_edge_ru')
@dp.message(Command("edge"))
async def edge_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.wav",
                               "assets/sounds/Загружаю-сэр.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            app = await message.reply("Запуск Microsoft Edge", reply_markup=btn_exit_edge_ru)
            pyautogui.press("win")
            time.sleep(1)
            keyboard.write("Microsoft Edge")
            time.sleep(1)
            pyautogui.press('enter')

            await asyncio.sleep(30)
            await app.delete()

        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Firefox" button in Russian and the "/firefox" command
@dp.callback_query(lambda call: call.data == 'btn_firefox_ru')
@dp.message(Command("firefox"))
async def firefox_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.wav",
                               "assets/sounds/Загружаю-сэр.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            app = await message.reply("Запуск Firefox", reply_markup=btn_exit_firefox_ru)
            pyautogui.press("win")
            time.sleep(1)
            keyboard.write("Firefox")
            time.sleep(1)
            pyautogui.press('enter')

            await asyncio.sleep(30)
            await app.delete()

        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Discord" button in Russian and the "/discord" command
@dp.callback_query(lambda call: call.data == 'btn_discord_ru')
@dp.message(Command("discord"))
async def discord_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.wav",
                               "assets/sounds/Загружаю-сэр.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            app = await message.reply("Запуск Discord", reply_markup=btn_exit_discord_ru)
            pyautogui.press("win")
            time.sleep(1)
            keyboard.write("Discord")
            time.sleep(1)
            pyautogui.press('enter')

            await asyncio.sleep(30)
            await app.delete()

        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "steam" button in Russian and the "/steam" command
@dp.callback_query(lambda call: call.data == 'btn_steam_ru')
@dp.message(Command("steam"))
async def steam_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.wav",
                               "assets/sounds/Загружаю-сэр.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            app = await message.reply("Запуск Steam", reply_markup=btn_exit_steam_ru)
            pyautogui.press("win")
            time.sleep(1)
            keyboard.write("Steam")
            time.sleep(1)
            pyautogui.press('enter')

            await asyncio.sleep(30)
            await app.delete()

        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The "Console" button in Russian and the "/console" command
@dp.callback_query(lambda call: call.data == 'btn_console_ru')
@dp.message(Command("console"))
async def console_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.wav",
                               "assets/sounds/Загружаю-сэр.wav",
                               "assets/sounds/Мы работаем над проектом сэр 2.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            app = await message.reply("Запуск консоли", reply_markup=btn_exit_console_ru)
            os.system("start cmd")

            await asyncio.sleep(30)
            await app.delete()

        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()



# Exit buttons from applications in English
btn_exit_telegram_en = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Exit❌", callback_data="exit_telegram_en")]
    ]
)
btn_exit_chrome_en = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Exit❌", callback_data="exit_chrome_en")]
    ]
)
btn_exit_opera_en = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Exit❌", callback_data="exit_opera_en")]
    ]
)
btn_exit_edge_en = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Exit❌", callback_data="exit_edge_en")]
    ]
)
btn_exit_firefox_en = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Exit❌", callback_data="exit_firefox_en")]
    ]
)
btn_exit_discord_en = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Exit❌", callback_data="exit_discord_en")]
    ]
)
btn_exit_steam_en = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Exit❌", callback_data="exit_steam_en")]
    ]
)
btn_exit_console_en = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Exit❌", callback_data="exit_console_en")]
    ]
)


@dp.callback_query(lambda call: call.data == 'exit_telegram_en')
async def exit_telegram_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Telegram.exe /F")
            exit_message = await call.message.answer("Telegram is closed")

            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_chrome_en')
async def exit_chrome_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Chrome.exe /F")
            exit_message = await call.message.answer("Google Chrome is closed")

            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_opera_en')
async def exit_opera_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Opera.exe /F")
            exit_message = await call.message.answer("Opera is closed")

            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_edge_en')
async def exit_edge_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM msedge.exe /F")
            exit_message = await call.message.answer("Microsoft Edge is closed")

            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_firefox_en')
async def exit_firefox_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Firefox.exe /F")
            exit_message = await call.message.answer("Firefox is closed")

            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_discord_en')
async def exit_discord_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Discord.exe /F")
            exit_message = await call.message.answer("Discord is closed")

            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_steam_en')
async def exit_steam_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Steam.exe /F")
            exit_message = await call.message.answer("Steam is closed")

            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_console_en')
async def exit_console_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM cmd.exe /F")
            exit_message = await call.message.answer("Console is closed")

            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


# Exit buttons from applications in Russian
btn_exit_telegram_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Закрыть❌", callback_data="exit_telegram_ru")]
    ]
)
btn_exit_chrome_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Закрыть❌", callback_data="exit_chrome_ru")]
    ]
)
btn_exit_opera_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Закрыть❌", callback_data="exit_opera_ru")]
    ]
)
btn_exit_edge_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Закрыть❌", callback_data="exit_edge_ru")]
    ]
)
btn_exit_firefox_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Закрыть❌", callback_data="exit_firefox_ru")]
    ]
)
btn_exit_discord_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Закрыть❌", callback_data="exit_discord_ru")]
    ]
)
btn_exit_steam_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Закрыть❌", callback_data="exit_steam_ru")]
    ]
)
btn_exit_console_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Закрыть❌", callback_data="exit_console_ru")]
    ]
)


# Functions for closing applications in Russian
@dp.callback_query(lambda call: call.data == 'exit_telegram_ru')
async def exit_telegram_ru(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Telegram.exe /F")
            exit_message = await call.message.answer("Telegram закрыт")

            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.waw",
                               "assets/sounds/да-сэр-два.wav",
                               "assets/sounds/есть.wav",
                               "assets/sounds/как-пожелаете.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_chrome_ru')
async def exit_chrome_ru(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Chrome.exe /F")
            exit_message = await call.message.answer("Google Chrome закрыт")

            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.waw",
                               "assets/sounds/да-сэр-два.wav",
                               "assets/sounds/есть.wav",
                               "assets/sounds/как-пожелаете.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_opera_ru')
async def exit_opera_ru(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Opera.exe /F")
            exit_message = await call.message.answer("Opera закрыта")

            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.waw",
                               "assets/sounds/да-сэр-два.wav",
                               "assets/sounds/есть.wav",
                               "assets/sounds/как-пожелаете.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_edge_ru')
async def exit_edge_ru(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM msedge.exe /F")
            exit_message = await call.message.answer("Microsoft Edge закрыт")

            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.waw",
                               "assets/sounds/да-сэр-два.wav",
                               "assets/sounds/есть.wav",
                               "assets/sounds/как-пожелаете.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_firefox_ru')
async def exit_firefox_ru(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Firefox.exe /F")
            exit_message = await call.message.answer("Firefox закрыт")

            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.waw",
                               "assets/sounds/да-сэр-два.wav",
                               "assets/sounds/есть.wav",
                               "assets/sounds/как-пожелаете.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_discord_ru')
async def exit_discord_ru(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Discord.exe /F")
            exit_message = await call.message.answer("Discord заркыт")

            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.waw",
                               "assets/sounds/да-сэр-два.wav",
                               "assets/sounds/есть.wav",
                               "assets/sounds/как-пожелаете.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_steam_ru')
async def exit_steam_ru(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM Steam.exe /F")
            exit_message = await call.message.answer("Steam закрыт")

            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.waw",
                               "assets/sounds/да-сэр-два.wav",
                               "assets/sounds/есть.wav",
                               "assets/sounds/как-пожелаете.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


@dp.callback_query(lambda call: call.data == 'exit_console_ru')
async def exit_console_ru(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            os.system("taskkill /IM cmd.exe /F")
            exit_message = await call.message.answer("Консоль закрыта")

            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/да-сэр.waw",
                               "assets/sounds/да-сэр-два.wav",
                               "assets/sounds/есть.wav",
                               "assets/sounds/как-пожелаете.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()
            await asyncio.sleep(10)
            await exit_message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# YOUTUBE in English
@dp.callback_query(lambda call: call.data == 'apps_youtube_en')
async def youtube_commands_en(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("""YouTube commands:\n
""", reply_markup=markup_youtube_en)


btn_back_en = InlineKeyboardButton(text="Back 🔙", callback_data="btn_back_en")
btn_play_en = InlineKeyboardButton(text="Pause ⏸️/Continue ▶️", callback_data="btn_play_en")
btn_next_en = InlineKeyboardButton(text="Next video ⏭️", callback_data="btn_next_en")
markup_youtube_en = InlineKeyboardMarkup(inline_keyboard=[
    [btn_back_en],
    [btn_play_en],
    [btn_next_en],
]
)


# Back button in English
@dp.callback_query(F.data == 'btn_back_en')
async def go_back_en(call: CallbackQuery):
    if is_authorized(call.message):
        await cont_en(call)
    else:
        access = await call.message.answer("Access is denied!")
        await asyncio.sleep(15)
        await access.delete()



# pause button in English
@dp.callback_query(F.data == 'btn_play_en')
async def play_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return
    try:
        pyautogui.press('space')
        await call.answer("Done!", show_alert=False)

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# next video button in English
@dp.callback_query(F.data == 'btn_next_en')
async def next_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return
    try:
        keyboard.send('shift+n')
        await call.answer("Done!", show_alert=False)

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Button to turn on full-screen mode in English
@dp.callback_query(F.data == 'btn_fullscreen_en')
async def fullscreen_en(call: CallbackQuery):
    if not is_authorized(call.message):
        await call.message.reply("Access is denied!")
        return
    try:
        keyboard.send('f')
        await call.answer("Full-screen mode is activated!", show_alert=False)

    except Exception as e:
        error = await call.message.reply(f"Error: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# YOUTUBE in Russian
@dp.callback_query(lambda call: call.data == 'apps_youtube_ru')
async def youtube_commands_ru(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("""YouTube команды:\n
""", reply_markup=markup_youtube_ru)


btn_back_ru = InlineKeyboardButton(text="Назад 🔙", callback_data="btn_back_ru")
btn_play_ru = InlineKeyboardButton(text="Пауза ⏸️/Продолжить ▶️", callback_data="btn_play_ru")
btn_next_ru = InlineKeyboardButton(text="Следующее видео ⏭️", callback_data="btn_next_ru")
markup_youtube_ru = InlineKeyboardMarkup(inline_keyboard=[
    [btn_back_ru],
    [btn_play_ru],
    [btn_next_ru]]
)


# Back button in Russian
@dp.callback_query(F.data == 'btn_back_ru')
async def go_back_ru(call: CallbackQuery):
    if is_authorized(call.message):
        await cont_ru(call)
    else:
        access = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(15)
        await access.delete()


# pause button in Russian
@dp.callback_query(F.data == 'btn_play_ru')
async def play_ru(call: CallbackQuery):
    if not is_authorized(call.message):
        access = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(15)
        await access.delete()
        return
    try:
        pyautogui.press('space')
        await call.answer("Выполнено!", show_alert=False)

    except Exception as e:
        error = await call.message.reply(f"Ошибка: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# the next video button is in Russian
@dp.callback_query(F.data == 'btn_next_ru')
async def next_ru(call: CallbackQuery):
    if not is_authorized(call.message):
        access = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(15)
        await access.delete()
        return
    try:
        keyboard.send('shift+n')
        await call.answer("Выполнено!", show_alert=False)

    except Exception as e:
        error = await call.message.reply(f"Ошибка: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()



# Sites in English
@dp.callback_query(lambda call: call.data == 'sait_commands_en')
async def sait_commands_en(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("""Site commands:\n
""", reply_markup=markup_sait_en)


btn_back_en = InlineKeyboardButton(text="Back🔙", callback_data="btn_back_en")
btn_chatgpt_en = InlineKeyboardButton(text="Chat GPT🤖", callback_data="btn_chatgpt_en")
btn_youtube_en = InlineKeyboardButton(text="Youtube▶️", callback_data="btn_youtube_en")
btn_vk_en = InlineKeyboardButton(text="Vk🌐", callback_data="btn_vk_en")
btn_x_en = InlineKeyboardButton(text="X⚡", callback_data="btn_x_en")
btn_rutube_en = InlineKeyboardButton(text="Rutube🎬", callback_data="btn_rutube_en")
btn_binance_en = InlineKeyboardButton(text="Binance💰📈", callback_data="btn_binance_en")
btn_bybit_en = InlineKeyboardButton(text="ByBit💹📊", callback_data="btn_bybit_en")
btn_okx_en = InlineKeyboardButton(text="OKX🔐💵", callback_data="btn_okx_en")
btn_git_en = InlineKeyboardButton(text="GitHub💻", callback_data="btn_git_en")
btn_gmail_en = InlineKeyboardButton(text="Gmail", callback_data="btn_gmail_en")
btn_wiki_en = InlineKeyboardButton(text="Wikipedia", callback_data="btn_wiki_en")
markup_sait_en = InlineKeyboardMarkup(inline_keyboard=[
    [btn_back_en],
    [btn_chatgpt_en, btn_youtube_en],
    [btn_vk_en, btn_x_en, btn_rutube_en],
    [btn_binance_en, btn_bybit_en, btn_okx_en],
    [btn_git_en, btn_gmail_en, btn_wiki_en],
])


# Back button in English
@dp.callback_query(F.data == 'btn_back_en')
async def go_back_en(call: CallbackQuery):
    if is_authorized(call.message):
        await cont_en(call)
    else:
        access = await call.message.answer("Access is denied!")
        await asyncio.sleep(15)
        await access.delete()


# Button click handler
@dp.callback_query(lambda call: call.data == 'btn_open_s_en')
async def prompt_for_website(call: types.CallbackQuery):
    await call.message.answer("Введите домен сайта (например, youtube.com или vk.com):")
    await call.message.answer("Жду вашего ответа...")

    @dp.message()
    async def handle_website_input(message: types.Message):
        website = message.text.strip()

        if website:
            if not website.startswith('http://') and not website.startswith('https://'):
                website = 'http://' + website

            webbrowser.open(website)
            await message.answer(f"Открываю сайт: {website}")
        else:
            error = await message.answer("Вы не ввели домен, попробуйте снова.")
            await asyncio.sleep(15)
            await error.delete()


# chatgpt button in English
@dp.callback_query(lambda call: call.data == 'btn_chatgpt_en')
async def chatgpt_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            if voiceover_enabled_en:
                sound_files = [
                    "assets/js/of-course.wav",
                    "assets/js/yes-sir.wav",
                    "assets/js/as-you-wish-sir.wav",
                    "assets/js/yes-sir-1.wav",
                    "assets/js/opening-chatgpt-can-i-tell-you-something.wav",
                    "assets/js/opening-chatgpt-what-do-you-want-to-find.wav",
                    "assets/js/opening-chatgpt-do-you-need-my-help.wav",
                    "assets/js/i-open-chatgpt-what-is-next.wav"
                ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://chatgpt.com")
            message = await call.message.answer("Launching Chat GPT")

            await asyncio.sleep(15)
            await message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


# YouTube button in English
@dp.callback_query(lambda call: call.data == 'btn_youtube_en')
async def youtube_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav",
                               "assets/js/i-am-opening-youtube.-you-want-to-see-something.wav",
                               "assets/js/i-am-opening-youtube-what-are-we-watching.wav",
                               "assets/js/i-am-opening-youtube-what-can-i-get-you-sir.wav",
                               "assets/js/i-am-opening-youtube-what-is-next.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://youtube.com")
            message = await call.message.answer("Launching YouTube")

            await asyncio.sleep(15)
            await message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


# vk button in English
@dp.callback_query(lambda call: call.data == 'btn_vk_en')
async def vk_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav",
                               "assets/js/i-am-opening-a-vk-do-you-want-to-write-to-someone.wav",
                               "assets/js/i-am-opening-a-vk-if-you-need-my-help-please-contact.wav",
                               "assets/js/i-am-opening-a-vk-who-will-we-write-to.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://vk.com")
            message = await call.message.answer("Launching VK")

            await asyncio.sleep(15)
            await message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


# x button in English
@dp.callback_query(lambda call: call.data == 'btn_x_en')
async def x_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav",
                               ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://x.com")
            message = await call.message.answer("Launching X")

            await asyncio.sleep(15)
            await message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


# rutube button in English
@dp.callback_query(lambda call: call.data == 'btn_rutube_en')
async def rutube_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav",
                               ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://rutube.ru")
            message = await call.message.answer("Launching Rutube")

            await asyncio.sleep(15)
            await message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


# binance button in English
@dp.callback_query(lambda call: call.data == 'btn_binance_en')
async def binance_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav",
                               ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://www.binance.com/en")
            message = await call.message.answer("Launching Binance")

            await asyncio.sleep(15)
            await message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


# bybit button in English
@dp.callback_query(lambda call: call.data == 'btn_bybit_en')
async def bybit_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav",
                               ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://www.bybit.com/en-US/")
            message = await call.message.answer("Launching ByBit")

            await asyncio.sleep(15)
            await message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


# okx button in English
@dp.callback_query(lambda call: call.data == 'btn_okx_en')
async def okx_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav",
                               ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://www.okx.com/en")
            message = await call.message.answer("Launching OKX")

            await asyncio.sleep(15)
            await message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


# GitHub button in English
@dp.callback_query(lambda call: call.data == 'btn_git_en')
async def git_en(call: CallbackQuery):
    if is_authorized(call.message):
        try:
            if voiceover_enabled_en:
                sound_files = ["assets/js/of-course.wav",
                               "assets/js/yes-sir.wav",
                               "assets/js/as-you-wish-sir.wav",
                               "assets/js/yes-sir-1.wav",
                               ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://github.com")
            message = await call.message.answer("Launching GitHub")

            await asyncio.sleep(15)
            await message.delete()
        except Exception as e:
            error_message = await call.message.answer(f"Error: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await call.message.answer("Access is denied!")
        await asyncio.sleep(10)
        await access_message.delete()


# Sites in Russian
@dp.callback_query(lambda call: call.data == 'sait_commands_ru')
async def sait_commands_ru(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("""Команды сайта:\n
""", reply_markup=markup_sait_ru)


btn_back_ru = InlineKeyboardButton(text="Назад🔙", callback_data="btn_back_ru")
btn_chatgpt_ru = InlineKeyboardButton(text="Chat GPT🤖", callback_data="btn_chatgpt_ru")
btn_youtube_ru = InlineKeyboardButton(text="Youtube▶️", callback_data="btn_youtube_ru")
btn_vk_ru = InlineKeyboardButton(text="Vk🌐", callback_data="btn_vk_ru")
btn_x_ru = InlineKeyboardButton(text="X⚡", callback_data="btn_x_ru")
btn_rutube_ru = InlineKeyboardButton(text="Rutube🎬", callback_data="btn_rutube_ru")
btn_binance_ru = InlineKeyboardButton(text="Binance💰📈", callback_data="btn_binance_ru")
btn_bybit_ru = InlineKeyboardButton(text="ByBit💹📊", callback_data="btn_bybit_ru")
btn_okx_ru = InlineKeyboardButton(text="OKX🔐💵", callback_data="btn_okx_ru")
btn_git_ru = InlineKeyboardButton(text="GitHub💻", callback_data="btn_git_ru")
btn_gmail_ru = InlineKeyboardButton(text="Gmail📩", callback_data="btn_gmail_ru")
btn_wiki_ru = InlineKeyboardButton(text="ВикипедиЯ🔎", callback_data="btn_wiki_ru")
markup_sait_ru = InlineKeyboardMarkup(inline_keyboard=[
    [btn_back_ru],
    [btn_chatgpt_ru, btn_youtube_ru],
    [btn_vk_ru, btn_x_ru, btn_rutube_ru],
    [btn_binance_ru, btn_bybit_ru, btn_okx_ru],
    [btn_git_ru, btn_gmail_ru, btn_wiki_ru],
])


# Back button in Russian
@dp.callback_query(F.data == 'btn_back_ru')
async def go_back_ru(call: CallbackQuery):
    if is_authorized(call.message):
        await cont_en(call)
    else:
        access = await call.message.answer("Доступ запрещён!")
        await asyncio.sleep(15)
        await access.delete()


# ChatGPT button in Russian and the command "/chat_gpt"
@dp.callback_query(lambda call: call.data == 'btn_chatgpt_ru')
@dp.message(Command("chat_gpt"))
async def chatgpt_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = [
                    "assets/sounds/да-сэр.wav",
                    "assets/sounds/Загружаю-сэр.wav",
                    "assets/sounds/Запрос выполнен сэр.wav"
                ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://chatgpt.com")
            msg = await message.answer("Запуск Chat GPT")
            await asyncio.sleep(30)
            await msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# YouTube button in Russian and the command "/youtube"
@dp.callback_query(lambda call: call.data == 'btn_youtube_ru')
@dp.message(Command("youtube"))
async def youtube_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = [
                    "assets/sounds/да-сэр.wav",
                    "assets/sounds/Загружаю-сэр.wav",
                    "assets/sounds/Запрос выполнен сэр.wav"
                ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://youtube.com")
            msg = await message.answer("Запуск YouTube")
            await asyncio.sleep(30)
            await msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# vk button in Russian and the command "/vk"
@dp.callback_query(lambda call: call.data == 'btn_vk_ru')
@dp.message(Command("vk"))
async def vk_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = [
                    "assets/sounds/да-сэр.wav",
                    "assets/sounds/Загружаю-сэр.wav",
                    "assets/sounds/Запрос выполнен сэр.wav"
                ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://vk.com")
            msg = await message.answer("Запуск VK")
            await asyncio.sleep(30)
            await msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The x button in Russian and the "/x" command
@dp.callback_query(lambda call: call.data == 'btn_x_ru')
@dp.message(Command("x"))
async def x_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = [
                    "assets/sounds/да-сэр.wav",
                    "assets/sounds/Загружаю-сэр.wav",
                    "assets/sounds/Запрос выполнен сэр.wav"
                ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://x.com")
            msg = await message.answer("Запуск X")
            await asyncio.sleep(30)
            await msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The Rutube button in Russian and the command "/rutube"
@dp.callback_query(lambda call: call.data == 'btn_rutube_ru')
@dp.message(Command("rutube"))
async def rutube_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/О чем я думал обычно у нас все веселенькое.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://rutube.ru")
            msg = await message.answer("Запуск Rutube")
            await asyncio.sleep(30)
            await msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# Binance button in Russian and the command "/binance"
@dp.callback_query(lambda call: call.data == 'btn_binance_ru')
@dp.message(Command("binance"))
async def binance_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = [
                    "assets/sounds/да-сэр.wav",
                    "assets/sounds/Загружаю-сэр.wav",
                    "assets/sounds/Запрос выполнен сэр.wav"
                ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://www.binance.com/ru")
            msg = await message.answer("Запуск Binance")
            await asyncio.sleep(30)
            await msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The ByBit button in Russian and the command "/bybit"
@dp.callback_query(lambda call: call.data == 'btn_bybit_ru')
@dp.message(Command("bybit"))
async def bybit_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = [
                    "assets/sounds/да-сэр.wav",
                    "assets/sounds/Загружаю-сэр.wav",
                    "assets/sounds/Запрос выполнен сэр.wav"
                ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://www.bybit.com/ru-RU/")
            msg = await message.answer("Запуск ByBit")
            await asyncio.sleep(30)
            await msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# OKX button in Russian and the command "/okx"
@dp.callback_query(lambda call: call.data == 'btn_okx_ru')
@dp.message(Command("okx"))
async def okx_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = [
                    "assets/sounds/да-сэр.wav",
                    "assets/sounds/Загружаю-сэр.wav",
                    "assets/sounds/Запрос выполнен сэр.wav"
                ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://www.okx.com/ru")
            msg = await message.answer("Запуск OKX")
            await asyncio.sleep(30)
            await msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# The GitHub button in Russian and the command "/git_hub"
@dp.callback_query(lambda call: call.data == 'btn_git_ru')
@dp.message(Command("git_hub"))
async def git_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = ["assets/sounds/Мы работаем над проектом сэр 2.wav"]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://github.com")
            msg = await message.answer("Запуск GitHub")
            await asyncio.sleep(30)
            await msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# Gmail button in Russian and the command "/gmail"
@dp.callback_query(lambda call: call.data == 'btn_gmail_ru')
@dp.message(Command("gmail"))
async def wiki_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = [
                    "assets/sounds/да-сэр.wav",
                    "assets/sounds/Загружаю-сэр.wav",
                    "assets/sounds/Запрос выполнен сэр.wav"
                ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://gmail.com")
            msg = await message.answer("Запуск Gmail")
            await asyncio.sleep(30)
            await msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# Wikipedia button in Russian and the command "/wikipedia"
@dp.callback_query(lambda call: call.data == 'btn_wiki_ru')
@dp.message(Command("wikipedia"))
async def wiki_ru(event):
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()
    elif isinstance(event, Message):
        message = event

    if is_authorized(message):
        try:
            if voiceover_enabled_ru:
                sound_files = [
                    "assets/sounds/да-сэр.wav",
                    "assets/sounds/Загружаю-сэр.wav",
                    "assets/sounds/Запрос выполнен сэр.wav"
                ]
                sound_path = random.choice(sound_files)
                rate, data = wav.read(sound_path)
                sd.play(data, rate)
                sd.wait()

            webbrowser.open("https://ru.wikipedia.org/wiki/Заглавная_страница")
            msg = await message.answer("Запуск ВикипедиЯ")
            await asyncio.sleep(15)
            await msg.delete()
        except Exception as e:
            error_message = await message.answer(f"Ошибка: {str(e)}")
            await asyncio.sleep(10)
            await error_message.delete()
    else:
        access_message = await message.answer("Доступ запрещён!")
        await asyncio.sleep(10)
        await access_message.delete()


# information about the computer in English
@dp.callback_query(lambda call: call.data == 'my_computer_en')
async def my_computer_en(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("""Commands about my computer:\n
""", reply_markup=markup_my_computer_en)


btn_back_en = InlineKeyboardButton(text="Back 🔙", callback_data="btn_back_en")
btn_systeminfo_en = InlineKeyboardButton(text="Information about the system", callback_data="btn_systeminfo_en")
btn_power_info_en = InlineKeyboardButton(text="Power info", callback_data="btn_power_info_en")
btn_ports_info_en = InlineKeyboardButton(text="Ports info", callback_data="btn_ports_info_en")
markup_my_computer_en = InlineKeyboardMarkup(inline_keyboard=[
    [btn_back_en],
    [btn_systeminfo_en],
    [btn_power_info_en],
    [btn_ports_info_en]
])


# Function for getting system information
def get_system_info_en():
    uname = platform.uname()
    boot_time = psutil.boot_time()
    boot_time_formatted = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot_time))

    system_info = (
        f"🖥️ **System Information**\n"
        f"**OS:** {uname.system} {uname.release} (Version: {uname.version})\n"
        f"**Node Name:** {uname.node}\n"
        f"**Processor:** {uname.processor}\n"
        f"**Boot Time:** {boot_time_formatted}\n\n"
        f"📊 **Usage Stats**\n"
        f"**CPU Usage:** {psutil.cpu_percent()}%\n"
        f"**Memory Usage:** {psutil.virtual_memory().percent}%\n"
        f"**Disk Usage:** {psutil.disk_usage('/').percent}%\n"
        f"**Available Disk Space:** {round(psutil.disk_usage('/').free / 1024 ** 3, 2)} GB\n"
    )
    return system_info


# Button handler for displaying system information
@dp.callback_query(lambda call: call.data == "btn_systeminfo_en")
async def send_system_info_en(call: CallbackQuery):
    try:
        info = get_system_info_en()
        await call.message.reply(info, parse_mode="Markdown")
    except Exception as e:
        error = await call.message.reply(f"Error while getting information about the system: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Function for getting nutrition information
def get_power_info_en():
    try:
        battery = psutil.sensors_battery()
        if battery:
            plugged = "Plugged In" if battery.power_plugged else "On Battery"
            percent = battery.percent
            time_left = (
                f"{battery.secsleft // 3600}h {(battery.secsleft % 3600) // 60}m"
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED
                else "Calculating..."
            )

            power_info = (
                f"🔋 **Power Information**\n"
                f"**Charge Level:** {percent}%\n"
                f"**Status:** {plugged}\n"
                f"**Time Left:** {time_left}\n"
            )
        else:
            power_info = "⚠️ Unable to retrieve battery information. Are you using a desktop PC without a battery?"

        return power_info
    except Exception as e:
        return f"Error retrieving power information: {e}"


# Button handler for displaying power information
@dp.callback_query(lambda call: call.data == "btn_power_info_en")
async def send_power_info_en(call: CallbackQuery):
    power_info = get_power_info_en()
    await call.message.answer(power_info, parse_mode="Markdown")


# Function for getting information about ports
async def get_ports_info_en(call: CallbackQuery):
    try:
        open_ports = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_LISTEN:
                open_ports.append(conn.laddr.port)

        if not open_ports:
            ports_info = "🔒 No open ports were found. Your PC is safe."
        else:
            ports_info = "🔓 Open ports found:\n" + "\n".join([f"• Port {port}" for port in open_ports])

        # Information about public IP via ipify
        public_ip = requests.get("https://api.ipify.org").text
        shodan_response = requests.get(f"https://api.shodan.io/shodan/host/{public_ip}?key={SHODAN_API_KEY}")

        if shodan_response.status_code == 200:
            shodan_data = shodan_response.json()
            advice = "🛡️ Safety recommendations:\n" + "\n".join(
                [f"• {item['port']} - {item['transport']} ({item['product']})" for item in shodan_data.get('data', [])]
            )
        else:
            advice = "The security data could not be retrieved from Shodan."

        await call.message.answer(f"{ports_info}\n\n🌍 Your public IP: {public_ip}\n\n{advice}")
    except Exception as e:
        await call.message.answer(f"An error has occurred: {e}")


# Button handler for getting information about ports
@dp.callback_query(lambda call: call.data == "btn_ports_info_en")
async def handle_ports_info_en(call: CallbackQuery):
    await get_ports_info_en(call)


# information about the computer in Russian
@dp.callback_query(lambda call: call.data == 'my_computer_ru')
async def my_computer_ru(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("""Команды о моём ПК:\n
""", reply_markup=markup_my_computer_ru)


btn_back_ru = InlineKeyboardButton(text="Назад 🔙", callback_data="btn_back_ru")
btn_systeminfo_ru = InlineKeyboardButton(text="Информация о системе", callback_data="btn_systeminfo_ru")
btn_power_info_ru = InlineKeyboardButton(text="Информация о заряде", callback_data="btn_power_info_ru")
btn_ports_info_ru = InlineKeyboardButton(text="Порты", callback_data="btn_ports_info_ru")
markup_my_computer_ru = InlineKeyboardMarkup(inline_keyboard=[
    [btn_back_ru],
    [btn_systeminfo_ru],
    [btn_power_info_ru],
    [btn_ports_info_ru]
])


# Back button in English
@dp.callback_query(F.data == 'btn_back_ru')
async def go_back_ru(call: CallbackQuery):
    if is_authorized(call.message):
        await cont_ru(call)
    else:
        await call.message.answer("Доступ запрещён!")


# Function for getting system information
def get_system_info_ru():
    uname = platform.uname()
    boot_time = psutil.boot_time()
    boot_time_formatted = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot_time))

    system_info = (
        f"🖥️ **Информация о системе**\n"
        f"**ОС:** {uname.system} {uname.release} (Версия: {uname.version})\n"
        f"**Имя узла:** {uname.node}\n"
        f"**Процессор:** {uname.processor}\n"
        f"**Время загрузки:** {boot_time_formatted}\n\n"
        f"📊 **Статистика использования**\n"
        f"**Загрузка CPU:** {psutil.cpu_percent()}%\n"
        f"**Использование памяти:** {psutil.virtual_memory().percent}%\n"
        f"**Загрузка диска:** {psutil.disk_usage('/').percent}%\n"
        f"**Доступное место на диске:** {round(psutil.disk_usage('/').free / 1024 ** 3, 2)} ГБ\n"
    )

    return system_info


# Button handler for displaying system information
@dp.callback_query(lambda call: call.data == "btn_systeminfo_ru")
async def send_system_info_ru(call: CallbackQuery):
    try:
        info = get_system_info_en()
        await call.message.reply(info, parse_mode="Markdown")
    except Exception as e:
        error = await call.message.reply(f"Ошибка при получении информации о системе: {str(e)}")
        await asyncio.sleep(10)
        await error.delete()


# Function for getting nutrition information
def get_power_info_ru():
    try:
        battery = psutil.sensors_battery()
        if battery:
            plugged = "Подключено к сети" if battery.power_plugged else "Работает от батареи"
            percent = battery.percent
            time_left = (
                f"{battery.secsleft // 3600}h {(battery.secsleft % 3600) // 60}m"
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED
                else "Подсчитывается..."
            )
            power_info = (
                f"🔋 **Информация о питании**\n"
                f"**Уровень заряда:** {percent}%\n"
                f"**Состояние:** {plugged}\n"
                f"**Оставшееся время:** {time_left}\n"
            )
        else:
            power_info = "⚠️ Невозможно получить информацию о батарее. Вы используете настольный ПК без батареи?"

        return power_info
    except Exception as e:
        return f"Ошибка при получении информации о питании: {e}"


# Button handler for displaying power information
@dp.callback_query(lambda call: call.data == "btn_power_info_ru")
async def send_power_info_ru(call: CallbackQuery):
    power_info = get_power_info_ru()
    await call.message.answer(power_info, parse_mode="Markdown")


# Function for getting information about ports
async def get_ports_info_ru(call: CallbackQuery):
    try:
        open_ports = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_LISTEN:
                open_ports.append(conn.laddr.port)
        if not open_ports:
            ports_info = "🔒 Открытые порты не обнаружены. Ваш ПК в безопасности."
        else:
            ports_info = "🔓 Найдены открытые порты:\n" + "\n".join([f"• Порт {port}" for port in open_ports])

        # Information about public IP via ipify
        public_ip = requests.get("https://api.ipify.org").text
        shodan_response = requests.get(f"https://api.shodan.io/shodan/host/{public_ip}?key={SHODAN_API_KEY}")

        if shodan_response.status_code == 200:
            shodan_data = shodan_response.json()
            advice = "🛡️ Рекомендации по безопасности:\n" + "\n".join(
                [f"• {item['port']} - {item['transport']} ({item['product']})" for item in shodan_data.get('data', [])]
            )
        else:
            advice = "Не удалось получить данные о безопасности из Shodan."

        await call.message.answer(f"{ports_info}\n\n🌍 Ваш публичный IP: {public_ip}\n\n{advice}")
    except Exception as e:
        await call.message.answer(f"Произошла ошибка: {e}")


# Button handler for getting information about ports
@dp.callback_query(lambda call: call.data == "btn_ports_info_ru")
async def handle_ports_info_ru(call: CallbackQuery):
    await get_ports_info_en(call)




# PERSONAL ACCOUNT in English
btn_back_en = InlineKeyboardButton(text="Back 🔙", callback_data="btn_back_en")


def create_voice_button_en():
    if voiceover_enabled_en:
        return InlineKeyboardButton(
            text="Disable voice acting 🔇", callback_data="btn_disable_voice_en"
        )
    else:
        return InlineKeyboardButton(
            text="Enable voice acting 🔊", callback_data="btn_enable_voice_en"
        )


def create_personal_account_markup_en():
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn_back_en],
        [create_voice_button_en()]
    ])


@dp.callback_query(lambda call: call.data == 'personal_account_en')
async def personal_account_en(call: CallbackQuery):
    await call.message.delete()
    global voiceover_enabled_en
    username = call.from_user.username or "Not specified"
    user_id = call.from_user.id

    voiceover_status = "on✅" if voiceover_enabled_en else "off❌"

    text = f"""
👤 PERSONAL ACCOUNT — {username} :


🎙️ Voiceover: {voiceover_status}

🌍 Language: 🇬🇧

📁 The main folder: {disk_d_path}

🛠️ Version: Basic

🆔 Your ID: {user_id}
    """

    message = await call.message.answer(text, reply_markup=create_personal_account_markup_en())

    user_data[call.from_user.id] = {"message_id": message.message_id}


@dp.callback_query(lambda call: call.data == 'btn_enable_voice_en')
async def enable_voice_en(call: CallbackQuery):
    global voiceover_enabled_en
    voiceover_enabled_en = True

    user_id = call.from_user.id
    voiceover_status = "on✅" if voiceover_enabled_en else "off❌"
    text = f"""
👤 PERSONAL ACCOUNT — {call.from_user.username or 'Not specified'} :


🎙️ Voiceover: {voiceover_status}

🌍 Language: 🇬🇧

📁 The main folder: {disk_d_path}

🛠️ Version: Basic

🆔 Your ID: {user_id}
    """

    await call.message.edit_text(text)
    await call.message.edit_reply_markup(reply_markup=create_personal_account_markup_en())

    await call.answer("Voice acting is enabled 🔊")


@dp.callback_query(lambda call: call.data == 'btn_disable_voice_en')
async def disable_voice_en(call: CallbackQuery):
    global voiceover_enabled_en
    voiceover_enabled_en = False

    user_id = call.from_user.id
    voiceover_status = "on✅" if voiceover_enabled_en else "off❌"
    text = f"""
👤PERSONAL ACCOUNT — {call.from_user.username or 'Not specified'} :


🎙️ Voiceover: {voiceover_status}

🌍 Language: 🇬🇧

📁 The main folder: {disk_d_path}

🛠️ Version: Basic

🆔 Your ID: {user_id}
    """

    await call.message.edit_text(text)
    await call.message.edit_reply_markup(reply_markup=create_personal_account_markup_en())

    await call.answer("Voice acting is disabled 🔇")



# PERSONAL ACCOUNT in Russian
btn_back_ru = InlineKeyboardButton(text="Назад 🔙", callback_data="btn_back_ru")


def create_voice_button_ru():
    if voiceover_enabled_ru:
        return InlineKeyboardButton(
            text="Отключить озвучку 🔇", callback_data="btn_disable_voice_ru"
        )
    else:
        return InlineKeyboardButton(
            text="Включить озвучку 🔊", callback_data="btn_enable_voice_ru"
        )

def create_personal_account_markup_ru():
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn_back_ru],
        [create_voice_button_ru()]
    ])


@dp.callback_query(lambda call: call.data == 'personal_account_ru')
async def personal_account_ru(call: CallbackQuery):
    await call.message.delete()
    global voiceover_enabled_ru
    username = call.from_user.username or "Не указан"
    user_id = call.from_user.id

    voiceover_status = "вкл✅" if voiceover_enabled_ru else "выкл❌"

    text = f"""
👤 ЛИЧНЫЙ КАБИНЕТ — {username} :


🎙️ Озвучка: {voiceover_status}

🌍 Язык: 🇷🇺

📁 Основная папка: {disk_d_path}

🛠️ Версия: Базовая

🆔 Ваш ID: {user_id}

    """

    message = await call.message.answer(text, reply_markup=create_personal_account_markup_ru())

    user_data[user_id] = {"message_id": message.message_id}



# Handler for enabling voice acting
@dp.callback_query(lambda call: call.data == 'btn_enable_voice_ru')
async def enable_voice_ru(call: CallbackQuery):
    global voiceover_enabled_ru
    voiceover_enabled_ru = True

    user_id = call.from_user.id
    voiceover_status = "вкл✅" if voiceover_enabled_ru else "выкл❌"

    text = f"""
👤 ЛИЧНЫЙ КАБИНЕТ — {call.from_user.username or 'Не указан'} :


🎙️ Озвучка: {voiceover_status}

🌍 Язык: 🇷🇺

📁 Основная папка: {disk_d_path}

🛠️ Версия: Базовая

🆔 Ваш ID: {user_id}
    """

    await call.message.edit_text(text)
    await call.message.edit_reply_markup(reply_markup=create_personal_account_markup_ru())

    await call.answer("Озвучка включена 🔊")


# Handler for disabling voice acting
@dp.callback_query(lambda call: call.data == 'btn_disable_voice_ru')
async def disable_voice_ru(call: CallbackQuery):
    global voiceover_enabled_ru
    voiceover_enabled_ru = False

    user_id = call.from_user.id
    voiceover_status = "вкл✅" if voiceover_enabled_ru else "выкл❌"

    text = f"""
👤 ЛИЧНЫЙ КАБИНЕТ — {call.from_user.username or 'Не указан'} :


🎙️ Озвучка: {voiceover_status}

🌍 Язык: 🇷🇺

📁 Основная папка: {disk_d_path}

🛠️ Версия: Базовая

🆔 Ваш ID: {user_id}
    """

    await call.message.edit_text(text)
    await call.message.edit_reply_markup(reply_markup=create_personal_account_markup_ru())

    await call.answer("Озвучка отключена 🔇")




# Bot launch function
async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# A function to run the bot in a separate thread
def run_bot():
    asyncio.run(start_bot())


def main():
    global authorized_user_id

    print("Введите ваш ID Telegram для запуска бота:")
    input_id = input("ID: ").strip()

    if input_id in user_ids:
        print(f"Бот запущен для пользователя с ID: {input_id}")
        authorized_user_id = input_id

        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()

        bot_thread.join()
    else:
        print(f"Пользователь с ID {input_id} не имеет доступа!")


if __name__ == "__main__":
    main()