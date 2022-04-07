from vkbottle.bot import Blueprint
from vkbottle import GroupEventType, Keyboard, Callback, KeyboardButtonColor, BaseMiddleware, UserTypes, UserEventType
from vkbottle.bot import Bot, Message, MessageEvent, rules
from database import DB
from elschool import SchoolApi
import datetime, pytz, time
import dateutil
import calendar, locale
import math
import aiohttp
import imgkit
from vkbottle.tools import PhotoMessageUploader
import os
import matplotlib.pyplot as plt
import numpy as np
import socket


bp = Blueprint("start")
SchoolApi = SchoolApi()
locale.setlocale(locale.LC_ALL, 'Russian')

@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "menu_dnevnik"})
async def cmd_start(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Дневник", payload={"cmd": "menu_select_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .add(Callback("Табель оценок", payload={"cmd": "menu_select_tabel"}), color=KeyboardButtonColor.SECONDARY)
            .row()
            .add(Callback("Средний балл", payload={"cmd": "menu_middle_ball"}), color=KeyboardButtonColor.SECONDARY)
            .add(Callback("Последние оценки", payload={"cmd": "menu_last_marks"}), color=KeyboardButtonColor.SECONDARY)
            .row()
            .add(Callback("Рейтинг", payload={"cmd": "menu_elschool_top"}), color=KeyboardButtonColor.SECONDARY)
            .row()
            .add(Callback("Назад", payload={"cmd": "start"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )

    await event.send_message("Выберите тип получения данных:", keyboard=keyboard)

@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "menu_elschool_top"})
async def cmd_start(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass

    result_db = await DB.get_token_by_user_id(event.user_id)

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "menu_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )

    if result_db[0] == "" and result_db[1] == "":
        await event.send_message("Вы не авторизованы в боте...", keyboard=keyboard)
        return

    all_values = await DB.select_elschool_top()
    if len(all_values) == 0:
        await event.send_message("Данные обновляются. Попробуте позже.", keyboard=keyboard)
        return


    role = await DB.select_role_by_user_id(event.user_id)
    settings_users = await DB.select_all_settings_by_userid(event.user_id)

    number = 1
    text = "Средний балл среди всех авторизированных:\n\n"
    for i in list(reversed(sorted(all_values, key=lambda d: d[3])))[:10]:
        settings = await DB.select_all_settings_by_userid(i[1])

        if settings is None:
            continue

        if settings[1] == 1 or role[0].lower() == "администратор":
            if i[1] == event.user_id:
                text += f"\n{number}. Вы - {i[3]}"
            else:
                if settings_users[1] == 0 and role[0].lower() != "администратор":
                    text += f"\n{number}. Скрыт вашими настройками - {i[3]}"
                else:
                    text += f"\n{number}. {i[2]} - {i[3]}"
        elif settings[1] == 0:
            if i[1] == event.user_id:
                text += f"\n{number}. Вы - {i[3]}"
            else:
                text += f"\n{number}. Скрыто - {i[3]}"
        number += 1

    user_top = 1
    for i in list(reversed(sorted(all_values, key=lambda d: d[3]))):
        if i[1] == event.user_id:
            break
        else:
            user_top += 1

    user_elschool_top = await DB.select_elschool_top_by_userid(event.user_id)
    if user_elschool_top is not None and ". Вы - " not in text:
        text += f"\n.....\n{user_top}. Вы - {user_elschool_top[3]}"

    result = await DB.select_first_top()
    time_updated_1 = datetime.datetime.fromtimestamp(int(result[6]), tz=pytz.timezone('Europe/Moscow'))

    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    time_updated = datetime.datetime.fromtimestamp(int(result[6]) + 43200, tz=pytz.timezone('Europe/Moscow'))

    d = time_updated - now
    mm, ss = divmod(d.seconds, 60)
    hh, mm = divmod(mm, 60)

    text += f"\n\nОбновлено: {time_updated_1.strftime('%Y-%m-%d %H:%M:%S')}"
    text += f"\nСледующее обновление: {hh}:{mm}:{ss}"

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "menu_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .add(Callback("🔄", payload={"cmd": "menu_elschool_top"}))
            .add(Callback("По школе", payload={"cmd": "menu_elschool_top_school"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )
    await event.send_message(text, keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "menu_elschool_top_school"})
async def cmd_start(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass

    result_db = await DB.get_token_by_user_id(event.user_id)

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "menu_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )

    if result_db[0] == "" and result_db[1] == "":
        await event.send_message("Вы не авторизованы в боте...", keyboard=keyboard)
        return

    db = await DB.select_all_value_by_user_id(event.user_id)
    school_id = db[6]

    all_values = await DB.select_elschool_top()
    if len(all_values) == 0:
        await event.send_message("Данные обновляются. Попробуте позже.", keyboard=keyboard)
        return
    role = await DB.select_role_by_user_id(event.user_id)
    settings_users = await DB.select_all_settings_by_userid(event.user_id)

    number = 1
    text = "Средний балл среди вашей школы:\n\n"
    for i in list(reversed(sorted(all_values, key=lambda d: d[3]))):
        if school_id != i[5]:
            continue

        if number == 11:
            continue

        settings = await DB.select_all_settings_by_userid(i[1])

        if settings[1] == 1 or role[0].lower() == "администратор":
            if i[1] == event.user_id:
                text += f"\n{number}. Вы - {i[3]}"
            else:
                if settings_users[1] == 0 and role[0].lower() != "администратор":
                    text += f"\n{number}. Скрыт вашими настройками - {i[3]}"
                else:
                    text += f"\n{number}. {i[2]} - {i[3]}"
        elif settings[1] == 0:
            if i[1] == event.user_id:
                text += f"\n{number}. Вы - {i[3]}"
            else:
                text += f"\n{number}. Скрыто - {i[3]}"
        number += 1

    user_top = 1
    for i in list(reversed(sorted(all_values, key=lambda d: d[3]))):
        if school_id == i[5]:
            if i[1] == event.user_id:
                break
            else:
                user_top += 1

    user_elschool_top = await DB.select_elschool_top_by_userid(event.user_id)
    if ". Вы - " not in text:
        text += f"\n.....\n{user_top}. Вы - {user_elschool_top[3]}"


    result = await DB.select_first_top()
    time_updated_1 = datetime.datetime.fromtimestamp(int(result[6]), tz=pytz.timezone('Europe/Moscow'))

    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    time_updated = datetime.datetime.fromtimestamp(int(result[6]) + 43200, tz=pytz.timezone('Europe/Moscow'))

    d = time_updated - now
    mm, ss = divmod(d.seconds, 60)
    hh, mm = divmod(mm, 60)

    text += f"\n\nОбновлено: {time_updated_1.strftime('%Y-%m-%d %H:%M:%S')}"
    text += f"\nСледующее обновление: {hh}:{mm}:{ss}"

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "menu_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .add(Callback("🔄", payload={"cmd": "menu_elschool_top_school"}))
            .add(Callback("Среди всех пользователей", payload={"cmd": "menu_elschool_top"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )
    await event.send_message(text, keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "menu_select_dnevnik"})
async def cmd_start(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass
    weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    unix = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    week = unix.isocalendar()[1] + 1

    if (unix.weekday() + 1) == 7:
        tomorrow = 0
        week += 1
    else:
        tomorrow = unix.weekday() + 1


    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Понедельник", payload={"cmd": f"{week}_{weekday[0]}", "type": "select_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .add(Callback("Вторник", payload={"cmd": f"{week}_{weekday[1]}", "type": "select_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .add(Callback("Среда", payload={"cmd": f"{week}_{weekday[2]}", "type": "select_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .row()
            .add(Callback("Четверг", payload={"cmd": f"{week}_{weekday[3]}", "type": "select_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .add(Callback("Пятница", payload={"cmd": f"{week}_{weekday[4]}", "type": "select_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .row()
            .add(Callback("Сегодня", payload={"cmd": f"{week}_{weekday[unix.weekday()]}", "type": "select_dnevnik"}), color=KeyboardButtonColor.POSITIVE)
            .add(Callback("Завтра", payload={"cmd": f"{week}_{weekday[tomorrow]}", "type": "select_dnevnik"}), color=KeyboardButtonColor.POSITIVE)
            .row()
            .add(Callback("Выбрать день", payload={"cmd": "change_month"}), color=KeyboardButtonColor.POSITIVE)
            # .add(Callback("Месяц", payload={"type": "select_dnevnik_month"}),color=KeyboardButtonColor.POSITIVE)
            .row()
            .add(Callback("Назад", payload={"cmd": "menu_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )

    await event.send_message("Выберите дату:", keyboard=keyboard)

@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload_contains={"cmd": "change_month"})
async def cmd_start(event: MessageEvent):
    data = event.get_payload_json()

    try:
        data["month"]
    except:
        data["month"] = 0

    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    data["month"] = now.month
    my_calendar = calendar.monthcalendar(now.year, now.month)

    keyboard = (Keyboard(inline=True))
    month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "1", "1", "1", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

    len_month_row = 0
    len_month = 0
    for _ in range(1, len(month_names) + 1):
        if len_month_row == 3:
            keyboard.row()
            len_month_row = 0

        if _ == 6 or _ == 7 or _ == 8:
            pass
        else:
            if _ == data["month"]:
                weekday = 0
                for i in my_calendar:
                    if now.day in i:
                        break
                    weekday += 1
                keyboard.add(Callback(f"⏺ {calendar.month_name[_]}", payload={"cmd": "select_month", "weekday": int(weekday), "month": _}))
            else:
                keyboard.add(Callback(f"{calendar.month_name[_]}", payload={"cmd": "select_month", "weekday": 0, "month": _}))
            len_month += 1
            len_month_row += 1

    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    year = now.year

    keyboard.row()
    keyboard.add(Callback("Назад", payload={"cmd": "menu_select_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
    await event.edit_message(f"{year} год", keyboard=keyboard.get_json())


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload_contains={"cmd": "select_month"})
async def cmd_start(event: MessageEvent):
    data = event.get_payload_json()

    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    year = now.year
    month = data["month"]
    weekday = data["weekday"]

    keyboard = (Keyboard(inline=True))
    keyboard.row()

    my_calendar = calendar.monthcalendar(year, month)

    weekday_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    len_days = 0
    for days in my_calendar[weekday]:
        if len_days == 5:
            break

        if days == 0:
            keyboard.add(Callback("ᅠ", payload={"cmd": "show_null_day"}))
        else:
            weeknumber = datetime.date(2022, month, days).strftime("%V")
            print(f"WEEK: {weeknumber};;;; {month} {days}")
            if month == now.month and days == now.day:
                keyboard.add(Callback(f"⏺ {days} [{weekday_names[len_days]}]",payload={"type": "select_dnevnik", "cmd": f"{int(weeknumber) + 1}_{weekdays[len_days]}", "day": days, "weekday": len_days, "month": month}))
            else:
                keyboard.add(Callback(f"{days} [{weekday_names[len_days]}]", payload={"type": "select_dnevnik", "cmd": f"{int(weeknumber) + 1}_{weekdays[len_days]}", "day": days, "weekday": len_days, "month": month}))
        len_days += 1
        keyboard.row()

    # print(weekday, len(my_calendar))
    if weekday-1 >= 0:
        keyboard.add(Callback("<", payload={"cmd": "select_month", "weekday": weekday-1, "month": int(month)}))

    keyboard.add(Callback(calendar.month_name[month], payload={"cmd": "change_month", "month": month}))

    if weekday < len(my_calendar) - 1:
        keyboard.add(Callback(">", payload={"cmd": "select_month", "weekday": weekday+1, "month": int(month)}))

    await event.edit_message(calendar.month_name[month] + " " + str(year), keyboard=keyboard.get_json())


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "show_null_day"})
async def cmd_start(event: MessageEvent):
    await event.show_snackbar("Пустой день.")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "menu_middle_ball"})
async def cmd_start(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "menu_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )

    xx = [5, ]
    y = ['test', ]

    result_db = await DB.get_token_by_user_id(event.user_id)

    if result_db[0] == "" and result_db[1] == "":
        await event.send_message("Вы не авторизованы в боте...", keyboard=keyboard)
        return
    result = await SchoolApi.chart_avgmarksbyperiod_get(userid=result_db[0], startdate="2022-01-17", enddate="2022-05-31", token=result_db[1])

    for i in result["result"]:
        if i["AvgMark"] == "None" or i["AvgMark"] is None:
            xx.append(0)
        else:
            xx.append(float(i["AvgMark"]))
        y.append(i["StartDate"].split("T")[0].replace('2022-', ''))

    x = np.arange(len(y))

    fig, ax = plt.subplots(constrained_layout=True)

    plt.bar(x, height=xx)
    plt.xticks(x, y, rotation='vertical')
    plt.xlabel("123123")

    ax.set_xlabel('номер недели')
    ax.set_ylabel('оценка')
    ax.set_title('средний балл')

    plt.savefig('temp.png')
    doc = await PhotoMessageUploader(bp.api).upload('temp.png', peer_id=event.peer_id)

    await event.send_message(attachment=doc, message=f"Ваш средний балл за второе полугодие по неделям:", keyboard=keyboard)
    os.remove('temp.png')


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "menu_select_tabel"})
async def cmd_start(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass
    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "menu_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )
    message = await event.send_message("1")
    await bp.api.messages.edit(message="✅ Обработка сообщения\n🕛 Получение данных\n🕛 Обработка данных\n🕛 Отрисовка табеля", peer_id=event.peer_id, conversation_message_id=message.conversation_message_id)

    t = time.time()
    result_db = await DB.get_token_by_user_id(event.user_id)
    db = await DB.select_all_value_by_user_id(event.user_id)

    if result_db[0] == "" and result_db[1] == "":
        await bp.api.messages.edit(
            message="✅ Обработка сообщения\n❌ Получение данных\n⏹ Обработка данных\n⏹ Отрисовка табеля\n\nВы не авторизованы в боте...",
            peer_id=event.peer_id, conversation_message_id=message.conversation_message_id, keyboard=keyboard)
        return

    try:
        result_dep, result_period, result, lessons, marks, user_info = await SchoolApi.execute_tabel(departmentid=db[6], token=result_db[1], userid=result_db[0])
        """result_dep = await SchoolApi.user_department_get(userid=result_db[0], token=result_db[1])
        result_period = await SchoolApi.department_period_get(userid=result_db[0], token=result_db[1])
        result = await SchoolApi.department_discipline_get(userid=result_db[0], token=result_db[1])
        lessons = await SchoolApi.department_lesson_get(departmentid=db[6], token=result_db[1])

        marks = await SchoolApi.user_markvalue_get(userid=result_db[0], token=result_db[1])"""

        await bp.api.messages.edit(
            message="✅ Обработка сообщения\n✅ Получение данных\n🕛 Обработка данных\n🕛 Отрисовка табеля",
            peer_id=event.peer_id, conversation_message_id=message.conversation_message_id)
    except Exception as e:
        print(f"GET DATA ERROR 1: {e}")
        await bp.api.messages.edit(
            message=f"✅ Обработка сообщения\n❌ Получение данных\n⏹ Обработка данных\n⏹ Отрисовка табеля\n\nОшибка: {e}",
            peer_id=event.peer_id, conversation_message_id=message.conversation_message_id, keyboard=keyboard)
        return

    try:
        """        educationtype = result_dep["result"][-1]["EducationPeriodTypeKeyword"]
                systemperiodid = result_dep["result"][-1]["SystemPeriodId"]
        
                period_list = []
        
                for item in result_period['result']:
                    if item['EducationPeriodTypeKeyword'] == educationtype and item['SystemPeriodId'] == systemperiodid:
                        period_list.append(item)"""


        sorted_result = sorted(result["result"], key=lambda d: d['ShortTitle'])

        after_new_year = datetime.datetime.strptime("2022-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
        values = []
        number = 0

        for mark in sorted(marks["result"], key=lambda d: d['Id']):
            if mark["Active"] == "False":
                continue
            lesson = next(iter(item for item in lessons['result'] if item['Id'] == mark["LessonId"]), None)
            # print(lesson["DateTime"])
            lesson_name = next(iter(item for item in sorted_result if item['Id'] == lesson["DisciplineId"]), None)
            # print(lesson_name)
            lesson_check = next(iter(item for item in values if item['name'] == lesson_name["ShortTitle"]), None)

            if lesson_check is None:
                number += 1
                values.append({
                    "id": number,
                    "name": lesson_name["ShortTitle"],
                    "result": [{"one": {"round": "", "round_total": "", "number_color": "", "lists": []}, "two": {"round": "", "number_color": "", "round_total": "", "lists": []}}]
                })
            count_dict = 0
            for i in values:
                if i["name"] == lesson_name["ShortTitle"]:
                    break
                else:
                    count_dict += 1

            if datetime.datetime.strptime(lesson["DateTime"].split(".")[0], "%Y-%m-%dT%H:%M:%S").timestamp() > after_new_year.timestamp():
                values[count_dict]["result"][0]["two"]["lists"].append(int(mark["MarkTypeValueId"]))
                count_result = 0
                for i in values[count_dict]["result"][0]["two"]["lists"]:
                    count_result += int(i)

                lenn = (count_result / len(values[count_dict]["result"][0]["two"]["lists"]))
                if lenn < 2.5:
                    number_color = 2
                elif 2.5 <= lenn < 3.5:
                    number_color = 3
                elif 3.5 <= lenn < 4.5:
                    number_color = 4
                else:
                    number_color = 5

                values[count_dict]["result"][0]["two"]["number_color"] = number_color
                values[count_dict]["result"][0]["two"]["round"] = round(lenn, 1)
                values[count_dict]["result"][0]["two"]["round_total"] = math.ceil(values[count_dict]["result"][0]["two"]["round"])
                values[count_dict]["result"][0]["two"]["round"] = str(lenn)[:3]
            else:
                values[count_dict]["result"][0]["one"]["lists"].append(int(mark["MarkTypeValueId"]))
                count_result = 0
                for i in values[count_dict]["result"][0]["one"]["lists"]:
                    count_result += int(i)
                lenn = (count_result / len(values[count_dict]["result"][0]["one"]["lists"]))
                if lenn < 2.5:
                    number_color = 2
                elif 2.5 <= lenn < 3.5:
                    number_color = 3
                elif 3.5 <= lenn < 4.5:
                    number_color = 4
                else:
                    number_color = 5

                values[count_dict]["result"][0]["one"]["number_color"] = number_color
                values[count_dict]["result"][0]["one"]["round"] = round(lenn, 1)
                values[count_dict]["result"][0]["one"]["round_total"] = math.ceil(values[count_dict]["result"][0]["one"]["round"])
                values[count_dict]["result"][0]["one"]["round"] = str(lenn)[:3]

        await bp.api.messages.edit(
            message="✅ Обработка сообщения\n✅ Получение данных\n✅ Обработка данных\n🕛 Отрисовка табеля",
            peer_id=event.peer_id, conversation_message_id=message.conversation_message_id)
    except Exception as e:
        print(f"OBRABOTKA DATA ERROR 2: {e}")
        await bp.api.messages.edit(
            message=f"✅ Обработка сообщения\n✅ Получение данных\n❌ Обработка данных\n⏹ Отрисовка табеля\n\nОшибка: {e}",
            peer_id=event.peer_id, conversation_message_id=message.conversation_message_id, keyboard=keyboard)
        return


    try:
        async with aiohttp.ClientSession(trust_env=True) as session:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            async with session.post(f"http://{local_ip}:8000/api", json=values) as res:
                text = await res.text()

        imgkit.from_string(text, 'name.jpg')
        await bp.api.messages.edit(
            message="✅ Обработка сообщения\n✅ Получение данных\n✅ Обработка данных\n✅ Отрисовка табеля",
            peer_id=event.peer_id, conversation_message_id=message.conversation_message_id)

        doc = await PhotoMessageUploader(bp.api).upload('name.jpg', peer_id=event.peer_id)
    except Exception as e:
        print(f"OTRISOVKA ERROR: {e}")
        await bp.api.messages.edit(
            message=f"✅ Обработка сообщения\n✅ Получение данных\n✅ Обработка данных\n❌ Отрисовка табеля\n\nОшибка: {e}",
            peer_id=event.peer_id, conversation_message_id=message.conversation_message_id, keyboard=keyboard)
        return

    try: await bp.api.messages.delete(cmids=message.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except: pass
    await event.send_message(attachment=doc, message=f"Time: {int(time.time() - t)} сек.", keyboard=keyboard)
    os.remove('name.jpg')

@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload_contains={"type": "select_dnevnik"})
async def cmd_start(event: MessageEvent):
    result_db = await DB.get_token_by_user_id(event.user_id)

    if result_db is None:
        await event.show_snackbar(f"Вы не авторизированы в боте....")
        return

    result = await SchoolApi.login_users_get(result_db[1])

    if result["status"] == "ok":
        await event.show_snackbar(f"ok")

        db = await DB.select_all_value_by_user_id(event.user_id)

        unix = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
        year = unix.strftime("%Y")
        user_id = result_db[0]
        token = result_db[1]

        payload = event.get_payload_json()

        week = payload["cmd"].split("_")[0]
        weekday = payload["cmd"].split("_")[1]

        r = await SchoolApi.user_diary_get(user_id, departmentid=db[6], instituteid=82, year=year, week=week, token=token)

        if r["status"] == "error":
            await event.show_snackbar(f"Error: {r['error']['description']}")
            return
        try:
            await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id,                             delete_for_all=True)
        except:
            pass
        weekday_list = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}

        weekday_convert = weekday_list[weekday]
        date = datetime.datetime.strptime(f"{year}-W{int(week)-1}" + f'-{weekday_convert}', "%Y-W%W-%w")
        print(date)
        month_names = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября", "Октября", "Ноября",
                       "Декабря"]

        text = f"{int(date.strftime('%d'))} {month_names[date.month - 1]} ({calendar.day_name[date.weekday()]})\n\n"
        number = 1

        for i in r['result']:
            if i["WeekDayTypeKeyword"] == weekday:
                text += f"""{number}. «{i['Discipline']}»"""

                if i['Homework'] != "":
                    text += f"\n　{i['PastHomework']}"

                marks = "　Оценки: "
                if len(i["Marks"]) > 0:
                    for mark in i["Marks"]:
                        marks += mark["Mark"]
                    text += f"\n{marks}"

                if len(i["TeacherFiles"]) > 0:
                    text += f"\n　　Файлы учителя: "
                    for files in i["TeacherFiles"]:
                        text += f"\n　https://elschool.ru/files/downloadhomeworkteacher?Id={files['Id']} - {files['TeacherFileName']}{files['TeacherFileExtension']}"

                if len(i["LearnerFiles"]) > 0:
                    text += f"\n　　Ваши файлы: "
                    for files in i["LearnerFiles"]:
                        text += f"\n　https://elschool.ru/files/downloadhomeworkteacher?Id={files['Id']} - {files['LearnerFileName']}{files['LearnerFileExtension']}"

                text += f"\n　{i['StartTime'].replace(':00.0000000', '')} - {i['EndTime'].replace(':00.0000000', '')}\n\n"
                number += 1

        keyboard = (
            Keyboard(inline=True)
                .add(Callback("Назад", payload={"cmd": "menu_dnevnik"}),color=KeyboardButtonColor.SECONDARY)
                .get_json()
        )
        if text == f"{date.strftime('%d')} {date.strftime('%B')} ({calendar.day_name[date.weekday()]})":
            await event.send_message("Пустой день", keyboard=keyboard, dont_parse_links=True)
            return

        await event.send_message(text, keyboard=keyboard, dont_parse_links=True)
    else:
        await event.show_snackbar(f"Error: {result['error']['description']}")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "menu_last_marks"})
async def cmd_start(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass

    result_db = await DB.select_all_value_by_user_id(event.user_id)
    if result_db is None:
        await event.show_snackbar(f"Вы не авторизированы в боте....")
        return

    result = await SchoolApi.user_markvalue_get(userid=result_db[2], token=result_db[5])

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "menu_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )
    if result["status"] == "ok":
        text = "Ваши последние оценки:\n\n"
        number = 1

        if len(result["result"]) < 10:
            await event.send_message(f"Недостаточно оценок для статистики, необходимо 10, у вас {len(result['result'])}", keyboard=keyboard)
        elif len(result["result"]) >= 10:
            teachers_dict = await SchoolApi.user_diary_get(userid=result_db[2], departmentid=result_db[6],
                                                           instituteid=82, year=2022, week=5, token=result_db[5])
            if teachers_dict["status"] == "error":
                await event.send_message(f"Не получилось получить список учителей. \n\nОшибка: <<{teachers_dict['error']['description']}>>", keyboard=keyboard)
                await event.show_snackbar(f"Ошибка!")
                return

            lessons_dict = await SchoolApi.department_lesson_get(departmentid=result_db[6], token=result_db[5])
            name_lessons_dict = await SchoolApi.department_discipline_get(userid=result_db[2], token=result_db[5])
            name_teachers_dict = await SchoolApi.department_teacher_get(departmentid=result_db[6], token=result_db[5])

            if lessons_dict["status"] == "error":
                await event.send_message(f"Не получилось получить список предметов. \n\nОшибка: <<{lessons_dict['error']['description']}>>", keyboard=keyboard)
                await event.show_snackbar(f"Ошибка!")
                return

            if name_lessons_dict["status"] == "error":
                await event.send_message(f"Не получилось получить названия предметов. \n\nОшибка: <<{name_lessons_dict['error']['description']}>>", keyboard=keyboard)
                await event.show_snackbar(f"Ошибка!")
                return

            if name_teachers_dict["status"] == "error":
                await event.send_message(f"Не получилось получить список учителей. \n\nОшибка: <<{name_teachers_dict['error']['description']}>>", keyboard=keyboard)
                await event.show_snackbar(f"Ошибка!")
                return

            for i in reversed(result["result"][-10:]):
                lessons_info = next(iter(item for item in lessons_dict['result'] if item['Id'] == i["LessonId"]), None)

                name_lessons_info = next(iter(item for item in name_lessons_dict['result'] if item['Id'] == lessons_info["DisciplineId"]), None)

                if name_lessons_info is not None:
                    teacher_info = next(iter(item for item in name_teachers_dict['result'] if item['Id'] == lessons_info["TeacherId"]), None)

                    text += f"{number}. {name_lessons_info['ShortTitle'][0:9]}."
                else:
                    text += f"{number}. возможно математика"

                text += f"\n　Оценка: {i['MarkTypeValueId']}"
                text += f"\n　Время: {datetime.datetime.fromisoformat(i['CreatedDate'].split('.')[0]).strftime('%H:%M:%S %d.%m.%Y')}"

                if i['Comment'] != "":
                    text += f"\n　Комметарий: '{i['Comment']}'"

                if lessons_info is not None:
                    text += f"\n　Дата урока: {datetime.datetime.fromisoformat(lessons_info['DateTime'].split('.')[0]).strftime('%d.%m.%Y')}"

                if i["Active"] == "True":
                    text += f"\n　Активен: ✅"
                elif i["Active"] == "True":
                    text += f"\n　Активен: ❌"

                text += "\n\n"
                number += 1
            await event.send_message(text, keyboard=keyboard)
    else:
        await event.show_snackbar(f"Error: {result['error']['description']}")
