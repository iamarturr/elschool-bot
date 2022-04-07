import aiosqlite
import datetime, pytz

class DB:
    @staticmethod
    async def select_by_user_id(user_id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT * FROM users WHERE user_id = '{user_id}'")
        users = await cursor.fetchone()
        await cursor.close()
        await sql.close()

        return users

    @staticmethod
    async def select_role_by_user_id(user_id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT roles.role FROM users, roles WHERE user_id = '{user_id}' AND roles.id = users.role")
        users = await cursor.fetchone()
        await cursor.close()
        await sql.close()

        return users

    @staticmethod
    async def add_new_user(user_id, role=0, banned=0):
        unix = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')).timestamp()

        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?)", (None, user_id, role, banned, int(unix)))
        await sql.commit()
        await cursor.close()

        cursor = await sql.execute(f"INSERT INTO elschool VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (None, user_id, "", "", "", "", "", int(unix), int(unix)))
        await sql.commit()
        await cursor.close()

        cursor = await sql.execute(f"INSERT INTO settings VALUES(?, ?, ?, ?)", (None, user_id, True, True))
        await sql.commit()
        await cursor.close()
        await sql.close()
        return True

    @staticmethod
    async def update_values_elschool(user_id, login, password, token, client_id, school_id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"UPDATE elschool SET login = '{login}', password = '{password}', token = '{token}', client_id = '{client_id}', school_id = '{school_id}' WHERE user_id = '{user_id}'")

        await sql.commit()
        await cursor.close()
        await sql.close()
        return True

    @staticmethod
    async def get_token_by_user_id(user_id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT client_id, token FROM elschool WHERE user_id = '{user_id}'")
        result = await cursor.fetchone()

        await cursor.close()
        await sql.close()
        return result

    @staticmethod
    async def select_all_value_by_user_id(user_id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT * FROM elschool WHERE user_id = '{user_id}'")
        result = await cursor.fetchone()

        await cursor.close()
        await sql.close()
        return result

    @staticmethod
    async def select_all_users():
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT users.*, elschool.* FROM users, elschool WHERE elschool.user_id = users.user_id")
        result = await cursor.fetchall()

        await cursor.close()
        await sql.close()
        return result

    @staticmethod
    async def create_if_not_create_notification(user_id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT * FROM notification WHERE user_id = '{user_id}'")
        result = await cursor.fetchone()
        await cursor.close()

        if result is None:
            cursor = await sql.execute(f"INSERT INTO notification VALUES(?, ?, ?)", (None, user_id, 0))
            await sql.commit()
            await cursor.close()

        await sql.close()
        return True

    @staticmethod
    async def create_if_not_create_settings(user_id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT * FROM settings WHERE user_id = '{user_id}'")
        result = await cursor.fetchone()
        await cursor.close()

        if result is None:
            cursor = await sql.execute(f"INSERT INTO settings VALUES(?, ?, ?, ?)", (None, user_id, True, True))
            await sql.commit()
            await cursor.close()

        await sql.close()
        return True

    @staticmethod
    async def select_last_mark_id(user_id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT last_mark_id FROM notification WHERE user_id = '{user_id}'")
        result = await cursor.fetchone()

        await cursor.close()
        await sql.close()
        return result

    @staticmethod
    async def update_last_mark_id(user_id, mark_id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"UPDATE notification SET last_mark_id = '{int(mark_id)}' WHERE user_id = '{user_id}'")

        await sql.commit()
        await cursor.close()
        await sql.close()
        return True

    @staticmethod
    async def select_statistics_requests():
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT count FROM statistics WHERE id = 1")
        result = await cursor.fetchone()

        await cursor.close()
        await sql.close()
        return result

    @staticmethod
    async def select_by_token(token):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT * FROM elschool WHERE token = '{token}'")
        result = await cursor.fetchone()
        await cursor.close()
        await sql.close()

        return result

    @staticmethod
    async def add_statistics_requests():
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT count FROM statistics WHERE id = 1")
        result = await cursor.fetchone()
        await cursor.close()

        cursor = await sql.execute(f"UPDATE statistics SET count = '{result[0]+1}' WHERE id = 1")
        await sql.commit()
        await cursor.close()
        await sql.close()

        return True


    @staticmethod
    async def update_token_by_id(token, id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"UPDATE elschool SET token = '{token}' WHERE id = '{id}'")

        await sql.commit()
        await cursor.close()
        await sql.close()
        return True

    @staticmethod
    async def select_all_settings_by_userid(user_id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT mailing, display_top FROM settings WHERE user_id = '{user_id}'")

        result = await cursor.fetchone()
        await cursor.close()
        await sql.close()
        return result

    @staticmethod
    async def update_settings_by_userid(user_id, name, boolean):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"UPDATE settings SET {name} = '{boolean}' WHERE user_id = '{user_id}'")

        await sql.commit()
        await cursor.close()
        await sql.close()
        return True


    @staticmethod
    async def delete_all_db():
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"DELETE FROM settings")

        await sql.commit()
        await cursor.close()

        cursor = await sql.execute(f"DELETE FROM users")

        await sql.commit()
        await cursor.close()

        cursor = await sql.execute(f"DELETE FROM elschool")

        await sql.commit()
        await cursor.close()

        cursor = await sql.execute(f"DELETE FROM notification")

        await sql.commit()
        await cursor.close()

        cursor = await sql.execute(f"DELETE FROM roles")

        await sql.commit()
        await cursor.close()

        cursor = await sql.execute(f"DELETE FROM elschool_top")

        await sql.commit()
        await cursor.close()

        await sql.close()
        return True

    @staticmethod
    async def create_new_mark(lists_marks):
        # user_id, name, mark, mark_2, school_id
        sql = await aiosqlite.connect("database.db")

        for lists in lists_marks:
            cursor = await sql.execute(f"SELECT * FROM elschool_top WHERE user_id = '{lists[0]}'")
            result = await cursor.fetchone()
            await cursor.close()

            if result is None:
                updated = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')).timestamp()
                cursor = await sql.execute(f"INSERT INTO elschool_top VALUES(?, ?, ?, ?, ?, ?, ?)", (None, lists[0], lists[1], lists[2], 0, lists[4], int(updated)))

        await sql.commit()

        await sql.close()
        return True

    @staticmethod
    async def select_first_top():
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT * FROM elschool_top")

        result = await cursor.fetchone()
        await cursor.close()
        await sql.close()
        return result

    @staticmethod
    async def delete_elschool_top():
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"DELETE FROM elschool_top")

        await sql.commit()
        await cursor.close()
        await sql.close()
        return True


    @staticmethod
    async def select_elschool_top():
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT * FROM elschool_top")

        result = await cursor.fetchall()
        await cursor.close()
        await sql.close()
        return result


    @staticmethod
    async def select_elschool_top_by_userid(user_id):
        sql = await aiosqlite.connect("database.db")

        cursor = await sql.execute(f"SELECT * FROM elschool_top WHERE user_id = '{user_id}'")

        result = await cursor.fetchone()
        await cursor.close()
        await sql.close()
        return result