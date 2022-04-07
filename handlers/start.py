from vkbottle.bot import Blueprint
from vkbottle import GroupEventType, Keyboard, Callback, KeyboardButtonColor, BaseMiddleware, UserTypes, UserEventType
from vkbottle.bot import Bot, Message, MessageEvent, rules

bp = Blueprint("start")

@bp.on.message(payload={"command": "start"})
@bp.on.message(text=["/start", "Старт", "Начать", "start", "начать", "старт", "/старт", "!start", "/начать"])
async def sending_start(message: Message):
    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Профиль", payload={"cmd": "menu_lk"}), color=KeyboardButtonColor.POSITIVE)
            .row()
            .add(Callback("Помощь", payload={"cmd": "menu_help"}), color=KeyboardButtonColor.NEGATIVE)
            .row()
            .add(Callback("Статистика", payload={"cmd": "menu_stats"}), color=KeyboardButtonColor.SECONDARY)
            .row()
            .add(Callback("Электронный дневник", payload={"cmd": "menu_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )
    user = await message.get_user()

    await message.answer(f"Привет, {user.first_name}!\n\n", keyboard=keyboard)

@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "start"})
async def cmd_start(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except: pass

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Профиль", payload={"cmd": "menu_lk"}), color=KeyboardButtonColor.POSITIVE)
            .row()
            .add(Callback("Помощь", payload={"cmd": "menu_help"}), color=KeyboardButtonColor.NEGATIVE)
            .row()
            .add(Callback("Статистика", payload={"cmd": "menu_stats"}), color=KeyboardButtonColor.SECONDARY)
            .row()
            .add(Callback("Электронный дневник", payload={"cmd": "menu_dnevnik"}), color=KeyboardButtonColor.SECONDARY)
            .get_json()
    )
    user = await bp.api.users.get(event.user_id)

    await event.send_message(f"Привет, {user[0].first_name}!\n\n", keyboard=keyboard)