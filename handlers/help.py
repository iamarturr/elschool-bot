from vkbottle.bot import Blueprint
from vkbottle import GroupEventType, Keyboard, Callback, KeyboardButtonColor, BaseMiddleware, UserTypes, UserEventType
from vkbottle.bot import Bot, Message, MessageEvent, rules
import config
bp = Blueprint("services")


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, payload={"cmd": "menu_help"})
async def cmd_menu_reload(event: MessageEvent):
    try:
        await bp.api.messages.delete(cmids=event.conversation_message_id, peer_id=event.peer_id, delete_for_all=True)
    except: pass

    keyboard = (
        Keyboard(inline=True)
            .add(Callback("Назад", payload={"cmd": "start"}))
            .get_json()
    )

    await event.send_message(f"⁉ По вопросам к {config.admin_link}", keyboard=keyboard)
    await event.show_snackbar("фига он крутой....")