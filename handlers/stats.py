from vkbottle.bot import Blueprint
from vkbottle import GroupEventType, Keyboard, Callback, KeyboardButtonColor, BaseMiddleware, UserTypes, UserEventType
from vkbottle.bot import Bot, Message, MessageEvent, rules
from database import DB
import re
from vkbottle.tools import PhotoMessageUploader
from elschool import SchoolApi
import datetime, pytz
import math
import time


bp = Blueprint("stats")
SchoolApi = SchoolApi()


async def convert(number):
    return re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(number))


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "menu_stats"})
async def cmd_menu_reload(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass

    result = await DB.select_all_users()

    active_users = 0
    all_users = len(result)

    users = 0
    admins = 0
    curators = 0

    blocked = 0

    for i in result:
        if i[7] != "" and i[8] != "":
            active_users += 1

        type_user = await DB.select_role_by_user_id(i[1])

        if type_user[0] == "Пользователь":
            users += 1
        elif type_user[0] == "Куратор":
            curators += 1
        elif type_user[0] == "Администратор":
            admins += 1

        if i[3] == 1:
            blocked += 1

    count_requests = await DB.select_statistics_requests()
    text = f"""
Статистика в боте!

👾      Юзеры: {users}
👨‍✈️ Кураторы: {curators}
🧛‍♀️ Администраторы: {admins}
💗      Авторизированно: {active_users}

🔴 Заблокировано: {blocked}
👤 Всего пользователей: {all_users}
🤖 Всего отправлено запросов: {await convert(count_requests[0])}
    """
    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "start"}))
            .add(Callback("🔄", payload={"cmd": "menu_stats"}))
            .get_json()
    )

    await event.send_message(text, keyboard=keyboard)


