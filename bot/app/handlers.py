from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message
import app.keyboards as kb
from sqlalchemy.ext.asyncio import AsyncSession
from app.inline_menu_processing import get_menu_content


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    message_text, content = await get_menu_content(session, level=0)
    await message.answer(message_text, reply_markup=content)


@router.callback_query(kb.MenuCallBack.filter())
async def gp(callback: types.CallbackQuery, callback_data: kb.MenuCallBack, session: AsyncSession):
    if callback_data.level <= 5:
        message_text, content = await get_menu_content(
            session,
            callback_data.level,
            callback_data.sub_level,
            callback_data.prev_sub_level,
            callback_data.season,
            callback_data.gp,
            callback_data.weekend_session,
            callback_data.analytical_function
            )
        await callback.answer()
        await callback.message.edit_text(text=message_text, reply_markup=content)
    else:
        photo_file, caption = await get_menu_content(
            session,
            callback_data.level,
            callback_data.sub_level,
            callback_data.prev_sub_level,
            callback_data.season,
            callback_data.gp,
            callback_data.weekend_session,
            callback_data.analytical_function
            )
        
        await callback.answer()
        await callback.message.reply_photo(photo=photo_file, caption=caption)