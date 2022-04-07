from vkbottle.bot import Blueprint
from vkbottle import GroupEventType, Keyboard, Callback, KeyboardButtonColor, BaseMiddleware, UserTypes, UserEventType
from vkbottle.bot import Bot, Message, MessageEvent, rules
from vkbottle import BaseStateGroup
from database import DB
import datetime, pytz
from elschool import SchoolApi
from vkbottle import CtxStorage

bp = Blueprint("office")
SchoolApi = SchoolApi()
ctx = CtxStorage()


class ElschoolStates(BaseStateGroup):
    LOGIN_STATE = 0
    PASSWORD_STATE = 1
    CHECK_STATE = 2


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "lk_reload"})
async def cmd_menu_reload(event: MessageEvent):
    await cmd_menu_lk_main(event)
    await event.show_snackbar("Информация обновлена.")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "menu_lk"})
async def cmd_menu_lk_main(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass
    try:
        await bp.state_dispenser.delete(event.user_id)
    except Exception as e:
        print(f"STATE ERROR: {e}")

    result = await DB.select_by_user_id(event.user_id)

    time_register = datetime.datetime.fromtimestamp(int(result[4]), tz=pytz.timezone('Europe/Moscow')).strftime(
        '%Y-%m-%d %H:%M:%S')
    role = await DB.select_role_by_user_id(event.user_id)

    user_values = await DB.get_token_by_user_id(event.user_id)

    try:
        r = await SchoolApi.user_bill_get(user_values[0], user_values[1])
        print(f"END: {r}")
        # return str(r)
        buffet = r['result'][0]['Balance'] + " rub."
        dinigroom = r['result'][1]['Balance'] + " rub."
    except:
        buffet, dinigroom = "Неавторизовано", "Неавторизовано"

    text = f"""
Добро пожаловать в личный кабинет!

ID: {result[0]} ({event.user_id})
Баланс:
　　┌ Буфет - {buffet}
　　└ Столовая - {dinigroom}
Роль: {role[0]}
Регистрация: {time_register}.

    """
    if buffet == "Неавторизовано":
        keyboard = (
            Keyboard(inline=True)
                .add(Callback("Назад", payload={"cmd": "start"}))
                .add(Callback("🔄", payload={"cmd": "lk_reload"}))
                .add(Callback("Добавить аккаунт", payload={"cmd": "add_account"}))
                .row()
                .add(Callback("Настройки", payload={"cmd": "lk_settings"}))
                .get_json()
        )
    else:
        keyboard = (
            Keyboard(inline=True)
                .add(Callback("Назад", payload={"cmd": "start"}))
                .add(Callback("🔄", payload={"cmd": "lk_reload"}))
                .add(Callback("Удалить аккаунт", payload={"cmd": "delete_account"}))
                .row()
                .add(Callback("Настройки", payload={"cmd": "lk_settings"}))
                .get_json()
        )
    await event.send_message(text, keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "lk_settings"})
async def lk_settings(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass

    await DB.create_if_not_create_settings(event.user_id)

    result = await DB.select_all_settings_by_userid(event.user_id)

    lists = ["mailing", "display_top"]
    lists_number = 0

    keyboard = (
        Keyboard(inline=True)
    )

    for i in result:
        if lists_number == 0:
            if i == 0:
                text = "Включить рассылку оценок"
                payload = f"{lists[lists_number]}.on"
                color = KeyboardButtonColor.POSITIVE
            else:
                text = "Выключить рассылку оценок"
                payload = f"{lists[lists_number]}.off"
                color = KeyboardButtonColor.NEGATIVE

        elif lists_number == 1:
            if i == 0:
                text = "Включить отображение в топе"
                payload = f"{lists[lists_number]}.on"
                color = KeyboardButtonColor.POSITIVE
            else:
                text = "Выключить отображение в топе"
                payload = f"{lists[lists_number]}.off"
                color = KeyboardButtonColor.NEGATIVE
        else:
            text = "Неизвестная кнопка"
            payload = ""
            color = KeyboardButtonColor.PRIMARY
        lists_number += 1

        keyboard.add(Callback(text, payload={"cmd": "change_settings", "settings": payload}), color=color)
        keyboard.row()
    keyboard.add(Callback("Назад", payload={"cmd": "menu_lk"}))
    keyboard = keyboard.get_json()

    await event.send_message("Настройки", keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload_contains={"cmd": "change_settings"})
async def cmd_menu_lk(event: MessageEvent):
    data = event.get_payload_json()

    try:
        name = data["settings"].split(".")[0]
        boolean = data["settings"].split(".")[1]
        if boolean == "on":
            boolean = 1
        elif boolean == "off":
            boolean = 0

        await DB.update_settings_by_userid(event.user_id, name, boolean)
        await lk_settings(event)
    except Exception as e:
        print(f"CHANGE SETTINGS ERROR: {e}")
        await event.show_snackbar(f"Произошла ошибка. Ошибка: {e}")
        return


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "delete_account"})
async def cmd_menu_lk(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "menu_lk"}))
            .add(Callback("Удалить", payload={"cmd": "delete_account_confirm"}))
            .get_json()
    )
    await event.send_message(
        """🤨 Вы уверены, что хотите удалить данные от аккаунта?\n\nДля отмены нажмите на кнопку <<Назад>>""",
        keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "delete_account_confirm"})
async def cmd_menu_lk(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass

    await DB.update_values_elschool(event.user_id, "", "", "", "", "")

    await cmd_menu_lk_main(event)
    await event.show_snackbar("Аккаунт удален....")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "add_account"})
async def cmd_menu_lk(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except:
        pass

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "menu_lk"}))
            .add(Callback("Начать", payload={"cmd": "start_registration"}))
            .get_json()
    )
    await event.send_message(
        """😃 Для работы с электронным дневником необходимо зарегистрироваться.\n\nДля продолжения нажмите на кнопку <<Начать>>🗿""",
        keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "start_registration"})
async def cmd_menu_lk(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, delete_for_all=True, peer_id=event.peer_id)
    except:
        pass

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Отмена", payload={"cmd": "menu_lk"}))
            .get_json()
    )

    await bp.state_dispenser.set(event.user_id, ElschoolStates.LOGIN_STATE)
    message_id = await event.send_message("""😃 Введите свой логин.\n\nДля отмены регистрации нажмите <<Отмена>>""",
                                          keyboard=keyboard)

    ctx.set("message_id", message_id.message_id)


@bp.on.message(state=ElschoolStates.LOGIN_STATE)  # StateRule(SuperStates.AWKWARD_STATE)
async def awkward_handler(message: Message):
    try:
        await bp.api.messages.delete(ctx.get("message_id"), delete_for_all=True)
    except:
        pass

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Отмена", payload={"cmd": "menu_lk"}))
            .get_json()
    )
    ctx.set("login", message.text)

    await bp.state_dispenser.set(message.from_id, ElschoolStates.PASSWORD_STATE)
    message_id = await message.answer("""😃 Хорошо, теперь введите свой пароль.\n\nДля отмены регистрации нажмите <<Отмена>>""", keyboard=keyboard)
    ctx.set("message_id", message_id.message_id)


@bp.on.message(state=ElschoolStates.PASSWORD_STATE)  # StateRule(SuperStates.AWKWARD_STATE)
async def awkward_handler(message: Message):
    try:
        await bp.api.messages.delete(ctx.get("message_id"), delete_for_all=True)
    except:
        pass

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Отмена", payload={"cmd": "menu_lk"}))
            .add(Callback("Отправить", payload={"cmd": "check_account"}))
            .get_json()
    )
    ctx.set("password", message.text)
    login = ctx.get("login")
    password = ctx.get("password")

    message_id = await message.answer(f"""😃 Отлично!\n\nВаши данные:\nЛогин: {login} \nПароль: {password} \n\nДля отмены регистрации нажмите <<Отмена>>""", keyboard=keyboard)
    ctx.set("message_id", message_id.message_id)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "check_account"})
async def cmd_menu_lk(event: MessageEvent):
    try:
        await bp.api.messages.delete(ctx.get("message_id"), delete_for_all=True)
    except:
        pass

    login = ctx.get("login")
    password = ctx.get("password")
    await bp.state_dispenser.delete(event.user_id)

    result = await SchoolApi.check_account(login=login, password=password)

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Главное меню", payload={"cmd": "menu_lk"}))
            .get_json()
    )

    if result['status'] == "error":
        await event.send_message(f"Не получилось авторизоваться в Ваш аккаунт. \n\nОшибка: <<{result['error']['description']}>>", keyboard=keyboard)
        await event.show_snackbar(f"Ошибка!")
    elif result['status'] == "ok":
        if len(result['result']['Roles']) == 0:
            await event.send_message("На аккаунте нет роль ученика...", keyboard=keyboard)
            await event.show_snackbar(f"Ошибка!")
            return
        elif len(result['result']['Roles']) > 1:

            keyboard = (
                Keyboard(inline=True)
            )
            number = 1
            number_id = 0
            for i in result['result']['Roles']:
                if number == 3:
                    keyboard.row()
                    number = 1
                name = f'{i["EntityName"].split()[1]} {i["EntityName"].split()[0][0]}.'
                keyboard.add(Callback(label=name, payload={"cmd": "relogin_account", "id": number_id}))
                number += 1
                number_id += 1

            await event.send_message("На аккаунте имеется несколько ролей!\n\nВыберите пользователя, который будет авторизован в боте", keyboard=keyboard.get_json())
            await event.show_snackbar(f"Мне лень делать поддержку!")
            return

        token = result['result']['Token']

        users_info = await SchoolApi.login_users_get(token)

        if users_info["status"] == "error":
            await event.send_message(f"Не получилось получить id ученика. \n\nОшибка: <<{users_info['error']['description']}>>", keyboard=keyboard)
            await event.show_snackbar(f"Ошибка!")
            return

        client_id = users_info['result'][0]['Id']
        school_info = await SchoolApi.user_department_get(userid=client_id, token=token)

        if school_info["status"] == "error":
            await event.send_message(f"Не получилось получить id школы. \n\nОшибка: <<{school_info['error']['description']}>>", keyboard=keyboard)
            await event.show_snackbar(f"Ошибка!")
            return

        school_id = school_info['result'][-1]['Id']

        await DB.update_values_elschool(event.user_id, login, password, token, client_id, school_id)

        await event.send_message(f"Успешная авторизация, спасибо за участие в проекте! \n\nP.s. включена рассылка оценок и отображение в топе, выключить их можно в профиль -> личный кабинет -> настройки\n\nВ случае чего-либо Вы можете удалить аккаунт по кнопке удалить в ЛК.", keyboard=keyboard)
        await event.show_snackbar(f"Успешно!")
        ctx.storage.clear()
    else:
        print(f"Неизвестный статус: ", result)
        await event.send_message(f"Неизвестный статус авторизации. \n\nОшибка отправлена администрации.", keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload_contains={"cmd": "relogin_account"})
async def cmd_menu_lk(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, delete_for_all=True,
                                     peer_id=event.peer_id)
    except:
        pass

    client_number = event.get_payload_json()["id"]

    login = ctx.get("login")
    password = ctx.get("password")

    if login is None and password is None or str(client_number).isdigit() is False:
        await event.show_snackbar("Сессия завершилась")
        try:
            await bp.api.messages.delete(cmids=event.conversation_message_id, delete_for_all=True,
                                         peer_id=event.peer_id)
        except:
            pass
        return

    result = await SchoolApi.check_account(login=login, password=password)

    token = result['result']['Token']

    users_info = await SchoolApi.login_users_get(token)

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Главное меню", payload={"cmd": "menu_lk"}))
            .get_json()
    )

    if users_info["status"] == "error":
        await event.send_message(
            f"Не получилось получить id ученика. \n\nОшибка: <<{users_info['error']['description']}>>",
            keyboard=keyboard)
        await event.show_snackbar(f"Ошибка!")
        return

    client_id = users_info['result'][client_number]['Id']
    school_info = await SchoolApi.user_department_get(userid=client_id, token=token)

    if school_info["status"] == "error":
        await event.send_message(
            f"Не получилось получить id школы. \n\nОшибка: <<{school_info['error']['description']}>>",
            keyboard=keyboard)
        await event.show_snackbar(f"Ошибка!")
        return

    school_id = school_info['result'][-1]['Id']

    await DB.update_values_elschool(event.user_id, login, password, token, client_id, school_id)

    await event.send_message(
        f"Успешная авторизация, спасибо за участие в проекте! \n\nP.s. включена рассылка оценок и отображение в топе, выключить их можно в профиль -> личный кабинет -> настройки\n\nВ случае чего-либо Вы можете удалить аккаунт по кнопке удалить в ЛК.",
        keyboard=keyboard)
    await event.show_snackbar(f"Успешно!")
