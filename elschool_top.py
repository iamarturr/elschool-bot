from database import DB
from elschool import SchoolApi
import asyncio
import threading
import datetime, pytz

SchoolApi = SchoolApi()


async def starter_top():
    while True:
        await start_top()
        await asyncio.sleep(25)


async def start_top():
    users = await DB.select_all_users()
    after_new_year = datetime.datetime.strptime("2022-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
    time_unix = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')).timestamp()

    if (await DB.select_first_top()) is not None and (await DB.select_first_top())[-1] + 43200 > int(time_unix):
        pass
    else:
        await DB.delete_elschool_top()
        create_new_mark = []
        for i in users:
            allow_display_top = await DB.select_all_settings_by_userid(i[1])
            if allow_display_top is None:
                await DB.create_if_not_create_settings(i[1])
                allow_display_top = await DB.select_all_settings_by_userid(i[1])

            if i[8] != "" and i[9] != "":
                if allow_display_top[1] == 1:
                    result_db = await DB.select_all_value_by_user_id(i[1])

                    marks = await SchoolApi.user_markvalue_get(userid=result_db[2], token=result_db[5])
                    if marks["status"] == "error":
                        continue
                    lessons = await SchoolApi.department_lesson_get(departmentid=result_db[6], token=result_db[5])
                    if lessons["status"] == "error":
                        continue
                    result = await SchoolApi.department_discipline_get(userid=result_db[2], token=result_db[5])
                    if result["status"] == "error":
                        continue
                    sorted_result = sorted(result["result"], key=lambda d: d['ShortTitle'])

                    marks_result = 0
                    marks_result_len = 0
                    lessons_number = 0
                    values = []

                    for mark in sorted(marks["result"], key=lambda d: d['Id']):
                        lesson = next(iter(item for item in lessons['result'] if item['Id'] == mark["LessonId"]), None)
                        lesson_name = next(iter(item for item in sorted_result if item['Id'] == lesson["DisciplineId"]), None)

                        lesson_check = next(iter(item for item in values if item['name'] == lesson_name["ShortTitle"]), None)

                        if lesson_check is None:
                            lessons_number += 1
                            values.append({"name": lesson_name["ShortTitle"]})

                        if mark["Active"] == "False":
                            continue

                        if datetime.datetime.strptime(mark["CreatedDate"].split(".")[0], "%Y-%m-%dT%H:%M:%S").timestamp() > after_new_year.timestamp():
                            marks_result += int(mark["MarkTypeValueId"])
                            marks_result_len += 1

                    users_info = await SchoolApi.login_users_get(result_db[5])
                    if users_info["status"] == "ok":
                        name = f'{users_info["result"][-1]["Surname"]} {users_info["result"][-1]["Firstname"][0]}.'
                    else:
                        name = "error"

                    middle_marks = float(f"{marks_result/marks_result_len:.{2}f}")
                    # print(marks_result, marks_result_len, marks_result/marks_result_len, lessons_number)
                    create_new_mark.append([result_db[1], name, middle_marks, 0, result_db[6]])
                    # await DB.create_new_mark(result_db[1], name, middle_marks, 0, result_db[6])
                    # await asyncio.sleep(2)
        await DB.create_new_mark(create_new_mark)
