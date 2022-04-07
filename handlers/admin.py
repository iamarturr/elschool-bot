from vkbottle.bot import Blueprint
from vkbottle import GroupEventType, Keyboard, Callback, KeyboardButtonColor, BaseMiddleware, UserTypes, UserEventType
from vkbottle.bot import Bot, Message, MessageEvent, rules
from database import DB
from vkbottle.dispatch.rules import ABCRule
from vkbottle import BaseStateGroup
from vkbottle import CtxStorage
import asyncio
from vkbottle.tools import DocMessagesUploader
import os


class MyRule(ABCRule[Message]):
    def __init__(self):
        pass

    async def check(self, event: Message) -> bool:
        result = await DB.select_role_by_user_id(event.peer_id)

        if result[0].lower() == "администратор":
            return True
        else:
            return False


class MailingState(BaseStateGroup):
    TEXT_STATE = 0


bp = Blueprint("admin")
bp.labeler.custom_rules["my_rule"] = MyRule
ctx = CtxStorage()


@bp.on.message(MyRule(), text=["/admin"])
async def sending_start(message: Message):
    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Рассылка", payload={"cmd": "admin_mailing"}), color=KeyboardButtonColor.POSITIVE)
            .row()
            .add(Callback("Пользователи", payload={"cmd": "admin_users"}), color=KeyboardButtonColor.NEGATIVE)
            .get_json()
    )
    user = await message.get_user()

    await message.answer(f"Привет, {user.first_name}!\n\n", keyboard=keyboard)


@bp.on.message(MyRule(), text=["/db"])
async def sending_start(message: Message):
    doc = await DocMessagesUploader(bp.api).upload(
        "database.db", 'database.db', peer_id=message.peer_id
    )
    await message.answer("123123", attachment=doc)


@bp.on.message(MyRule(), text=["/deletedb"])
async def sending_start(message: Message):
    try:
        await DB.delete_all_db()
        await message.answer(f"успешно")
    except Exception as e:
        await message.answer(f"ERROR: {e}")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, MyRule(), payload={"cmd": "admin_start"})
async def cmd_start(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except: pass

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Рассылка", payload={"cmd": "admin_mailing"}), color=KeyboardButtonColor.POSITIVE)
            .row()
            .add(Callback("Пользователи", payload={"cmd": "admin_users"}), color=KeyboardButtonColor.NEGATIVE)
            .get_json()
    )
    user = await bp.api.users.get(event.user_id)

    await event.send_message(f"Привет, {user[0].first_name}!\n\n", keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, MyRule(), payload={"cmd": "admin_mailing"})
async def cmd_start(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except: pass

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "admin_start"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )

    await bp.state_dispenser.set(event.user_id, MailingState.TEXT_STATE)
    message_id = await event.send_message(f"Введи текст для рассылки:", keyboard=keyboard)
    ctx.set("message_id", message_id.message_id)


@bp.on.message(MyRule(), state=MailingState.TEXT_STATE)
async def awkward_handler(message: Message):
    try:
        await bp.api.messages.delete(ctx.get("message_id"), delete_for_all=True)
    except: pass

    ctx.set("text", message.text)
    text = ctx.get("text")

    print(len(message.attachments))
    if len(message.attachments) == 1:
        r = message.attachments[0]
        if ".WALL: 'wall'" in str(r):
            print(f'wall{r.wall.from_id}_{r.wall.id}')
            ctx.set("wall", f'wall{r.wall.from_id}_{r.wall.id}')

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "admin_start"}), color=KeyboardButtonColor.SECONDARY)
            .add(Callback("Отправить", payload={"cmd": "admin_mailing_send"}), color=KeyboardButtonColor.POSITIVE)
            .get_json()
    )

    await message.answer(f"""😃 Отлично!\n\nТекст: {text}\n\nДля отмены рассылки нажмите <<Отмена>>""", attachment=ctx.get("wall"), keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, MyRule(), payload={"cmd": "admin_mailing_send"})
async def cmd_start(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except: pass


    text = ctx.get("text")
    result_true = 0
    result_false = 0

    result = await DB.select_all_users()
    for i in result:
        try:
            await bp.api.messages.send(i[1], random_id=0, message=text, attachment=ctx.get("wall"))
            result_true += 1
        except Exception as e:
            print(e)
            result_false += 1
        await asyncio.sleep(0.4)

    ctx.storage.clear()

    await bp.state_dispenser.delete(event.user_id)
    await event.send_message(f"Рассылка произведена!\n\nТекст: \n{text}\nУспешно: {result_true}\nНеуспешно: {result_false}")
