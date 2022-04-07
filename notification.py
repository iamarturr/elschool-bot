from database import DB
from elschool import SchoolApi
import asyncio
import threading
import datetime

SchoolApi = SchoolApi()


async def starter(bot):
    while True:
        users = await DB.select_all_users()

        for i in users:
            allow_mailing = await DB.select_all_settings_by_userid(i[1])
            if allow_mailing is None:
                await DB.create_if_not_create_settings(i[1])
                allow_mailing = await DB.select_all_settings_by_userid(i[1])

            if i[8] != "" and i[9] != "":
                if allow_mailing[0] == 1:
                    await start_notification(i[1], bot)
                    await asyncio.sleep(10)
                else:
                    await DB.update_last_mark_id(i[1], 0)
        # print(f"Все потоки закончены, засыпаю")

        await asyncio.sleep(600)


async def start_notification(user_id, bot):
    await DB.create_if_not_create_notification(user_id)

    last_mark_id = await DB.select_last_mark_id(user_id)
    result_db = await DB.select_all_value_by_user_id(user_id)

    if last_mark_id[0] == 0:
        result = await SchoolApi.user_markvalue_get(userid=result_db[2], token=result_db[5])
        if result["status"] == "error":
            return 
        result_last = result["result"][-1]

        await DB.update_last_mark_id(user_id, int(result_last["Id"]))

    last_mark_id = await DB.select_last_mark_id(user_id)

    lessons_dict = await SchoolApi.department_lesson_get(departmentid=result_db[6], token=result_db[5])
    if lessons_dict["status"] == "error":
        return

    name_lessons_dict = await SchoolApi.department_discipline_get(userid=result_db[2], token=result_db[5])
    if name_lessons_dict["status"] == "error":
        return

    name_teachers_dict = await SchoolApi.department_teacher_get(departmentid=result_db[6], token=result_db[5])

    if name_teachers_dict["status"] == "error":
        return
    result = await SchoolApi.user_markvalue_get(userid=result_db[2], token=result_db[5])

    if result['status'] == "ok":
        for i in result["result"]:
            if int(i["Id"]) > last_mark_id[0]:
                text = f"Новая оценка! ({i['Id']})\nОценка: {i['MarkTypeValueId']}\nВремя: {datetime.datetime.fromisoformat(i['CreatedDate'].split('.')[0]).strftime('%H:%M:%S %d.%m.%Y')}\n"
                if i['Comment'] != "":
                    text += f"Комметарий: '{i['Comment']}'"

                lessons_info = next(iter(item for item in lessons_dict['result'] if item['Id'] == i["LessonId"]), None)
                name_lessons_info = next(iter(item for item in name_lessons_dict['result'] if item['Id'] == lessons_info["DisciplineId"]), None)

                if name_lessons_info is not None:
                    teacher_info = next(iter(item for item in name_teachers_dict['result'] if item['Id'] == lessons_info["TeacherId"]), None)

                    text += f"\n\nУчитель: {teacher_info['Surname']} {teacher_info['Firstname'][0]}.{teacher_info['Patronumic'][0]}."
                    text += f"\nПредмет: {name_lessons_info['ShortTitle'][0:9]}."
                else:
                    text += f"\nПредмет: возможно математика"


                if lessons_info is not None:
                    text += f"\nДата урока: {datetime.datetime.fromisoformat(lessons_info['DateTime'].split('.')[0]).strftime('%d.%m.%Y')}"

                if i["Active"] == "True":
                    try:
                        await bot.api.messages.send(peer_id=user_id, random_id=0, message=text)
                    except Exception as e:
                        print(f"Messages send: {e}")
                await DB.update_last_mark_id(user_id, int(i["Id"]))
    else:
        print(f"Ошибка {user_id}; {result}")
    # await asyncio.sleep(4242424)