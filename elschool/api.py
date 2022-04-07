import aiohttp
import asyncio
from database import DB

class SchoolApi:
    async def check_account(self, login, password):
        result = await self.get_token(login, password)
        print(result)
        return result


    async def post_requests(self, method, payload):
        pass

    @staticmethod
    async def decode_text(text):
        return str(text).decode("utf-8")

    async def get_token(self, login, password):
        return await self.get_requests("login.Token.get", f"login={login}&password={password}&twofa=")

    async def department_contingent_get(self, token, departmentid=160364):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("department.contingent.get", f"token={token}&departmentid={departmentid}")

    async def user_bill_get(self, userid, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("user.bill.get", f"token={token}&userid={userid}")

    async def user_department_get(self, userid, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("user.department.get",f"userId={userid}&token={token}")

    async def user_diary_get(self, userid, departmentid, instituteid, year, week, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("user.diary.get", f"userId={userid}&token={token}&departmentId={departmentid}&instituteId={instituteid}&year={year}&week={week}")

    async def check_account_token(self, userid, token):
        return await self.get_requests("user.department.get", f"userId={userid}&token={token}")

    async def department_lesson_get(self, departmentid, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("department.lesson.get", f"departmentId={departmentid}&token={token}")

    async def user_markvalue_get(self, userid, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("user.markvalue.get", f"userId={userid}&token={token}")

    async def user_markresult_get(self, userid, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n
        return await self.get_requests("user.markresult.get", f"userId={userid}&token={token}")

    async def department_schedule_get(self, departmentid, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("department.schedule.get", f"departmentId={departmentid}&token={token}")

    async def user_dairy_get(self, userid, departmentid, instituteId, year, week, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("user.dairy.get", f"departmentId={departmentid}&userid={userid}&instituteId={instituteId}&year={year}&week={week}&token={token}")

    async def login_users_get(self, token):
        """        n = await self.remake_token(token)
                if n is dict: return n
                else: token = n"""

        return await self.get_requests("login.users.get", f"token={token}")

    async def department_teacher_get(self, departmentid, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("department.teacher.get", f"departmentId={departmentid}&token={token}")

    async def department_period_get(self, userid, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n
        return await self.get_requests("department.period.get", f"userId={userid}&token={token}")

    async def remake_token(self, token):
        result = await DB.select_by_token(token)

        # token = ""
        if result is not None:
            token = result[5]
            if result[2] == "" and result[5] == "":
                return True
            r = await self.check_account_token(result[2], result[5])

            if r['status'] == "error":
                new_r = await self.get_token(result[3], result[4])

                if new_r['status'] == "error":
                    if int(new_r['error']['code']) == 2281337:
                        print("Пропустил токен")
                        # await DB.update_last_mark_id(result[1], 0)
                        return {"status": "error", "error": {"code": "2424428", "description": "Боту не удается отправить запрос на сервер, попробуйте позже..."}}

                    print("Удалил токен")
                    await DB.update_values_elschool(result[1], "", "", "", "", "")
                    await DB.update_last_mark_id(result[1], 0)
                    return {"status": "error", "error": {"code": "8", "description": "Неверный логин или пароль, авторизация в боте сброшена, залогинтесь заного..."}}
                token = new_r['result']['Token']
                await DB.update_token_by_id(new_r['result']['Token'], result[0])

        return token


    async def chart_absencesbyperiod_get(self, userid, startdate, enddate, token):
        """
        :param userid: user_id
        :param startdate: 2022-01-17
        :param enddate: 20222-05-31
        :param token: token
        :return:
        """
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("chart.absencesbyperiod.get", f"userId={userid}&startDate={startdate}&endDate={enddate}&token={token}")

    async def chart_avgmarkbyperioddepartment_get(self, userid, startdate, enddate, token):
        """
        :param userid: user_id
        :param startdate: 2022-01-17
        :param enddate: 2022-05-31
        :param token: token
        :return:
        """
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("chart.avgmarkbyperioddepartment.get", f"userId={userid}&startDate={startdate}&endDate={enddate}&token={token}")

    async def execute_tabel(self, departmentid, userid, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        result_dep = await self.get_requests("user.department.get", f"userId={userid}&token={token}")

        result_period = await self.get_requests("department.period.get", f"userId={userid}&token={token}")
        result = await self.get_requests("department.discipline.get", f"userId={userid}&token={token}")
        lessons = await self.get_requests("department.lesson.get", f"departmentId={departmentid}&token={token}")
        marks = await self.get_requests("user.markvalue.get", f"userId={userid}&token={token}")
        user_info = await self.get_requests("login.users.get", f"token={token}")
        return result_dep, result_period, result, lessons, marks, user_info


    async def chart_avgmarksbyperiod_get(self, userid, startdate, enddate, token, stepdays=5):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("chart.avgmarksbyperiod.get",f"userId={userid}&startDate={startdate}&endDate={enddate}&stepDays={stepdays}&token={token}")

    async def department_discipline_get(self, userid, token):
        n = await self.remake_token(token)
        if n is dict: return n
        else: token = n

        return await self.get_requests("department.discipline.get", f"userId={userid}&token={token}")

    async def get_requests(self, method, data):
        await DB.add_statistics_requests()
        headers = {
            'sec-ch-ua': '"Opera GX";v="81", " Not;A Brand";v="99", "Chromium";v="95"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.61',
        }
        async with aiohttp.ClientSession() as session:
            # print(f"https://api.elschool.ru/api/{method}?{data}")


            # http://F2SGflzwuU:WGdhYv9U0f@92.63.198.85:24099 10mps 2022-04-16 20:08:24
            # http://YbTYn61J5itR:moder.kanalov@185.66.13.152:18520 10mps 2022-04-15
            # http://k1N2L1:hJBXGxl437@213.226.101.187:3000 до июля


            try:
                async with session.get(f"https://api.elschool.ru/api/{method}?{data}", headers=headers, proxy="http://YbTYn61J5itR:moder.kanalov@185.66.13.152:18520") as res:
                    return await res.json(content_type="text/plain; charset=utf-8")
            except Exception as e:
                print(f"Requests error: {e}")
                return {"status": "error", "error": {"code": 2281337, "description": "Не удается отправить запрос на сервер. Повторите попытку позднее. "}}
                
