from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    sub_level: str | None = None
    prev_sub_level: str | None = None
    season: int | None = None
    gp: str | None = None
    weekend_session: str | None = None
    analytical_function: str | None = None


async def main_start_kb(level: int):
    buttons = [
        ('Historical Stats', 'hist_stat'),
        ('Season Stats', 'seas_stat'),
        ('About', 'about')
    ]
    keyboard = InlineKeyboardBuilder()
    for button_text, button_level in buttons:
        keyboard.add(
            InlineKeyboardButton(
                text=button_text,
                callback_data=MenuCallBack(
                    level=level+1,
                    sub_level=button_level
                ).pack()
            )
        )
    return keyboard.adjust(1).as_markup()


async def back_to_main_button(level, previous_sub_level):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text='Back',
            callback_data=MenuCallBack(
                level=level-1,
                sub_level=previous_sub_level,
                prev_sub_level=None
            ).pack()
        )
    )
    
    return keyboard.adjust(1).as_markup()


async def get_seasonal_menu_kb(level, sub_level, previous_sub_level):
    buttons = [
        ("Season Overview", 'seas_overview'),
        ("Grand Prix Stats", 'gp_stat')
    ]
    keyboard = InlineKeyboardBuilder()
    for button_text, button_level in buttons:
        keyboard.add(
            InlineKeyboardButton(
                text=button_text,
                callback_data=MenuCallBack(
                    level=level+1,
                    sub_level=button_level,
                    prev_sub_level=sub_level
                ).pack()
            )
        )
    
    keyboard.add(
        InlineKeyboardButton(
            text='Back',
            callback_data=MenuCallBack(
                level=level-1,
                sub_level=previous_sub_level,
                prev_sub_level=None
            ).pack()
        )
    )

    return keyboard.adjust(1).as_markup()


async def get_f1_seasons_kb(seasons, level, prev_sub_level, size=2):
    keyboard = InlineKeyboardBuilder()
    for season in seasons:
        keyboard.add(
            InlineKeyboardButton(
                text=str(season),
                callback_data=MenuCallBack(
                    level=level+1,
                    season=season
                ).pack()
            )
        )
    
    keyboard.add(
        InlineKeyboardButton(
            text='Back',
            callback_data=MenuCallBack(
                level=level-1,
                sub_level=prev_sub_level
            ).pack()
        )
    )

    return keyboard.adjust(size).as_markup()


async def get_f1_gps_kb(gps, season, level, size=2):
    keyboard = InlineKeyboardBuilder()
    for gp in gps:
        keyboard.add(
            InlineKeyboardButton(
                text=str(gp),
                callback_data=MenuCallBack(
                    level=level+1,
                    season=season,
                    gp=gp
                ).pack()
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text = "Back",
            callback_data=MenuCallBack(
                level=level-1,
                # hardcode values, possible changes with levels (deep levels) or fsm
                sub_level='gp_stat', 
                prev_sub_level='seas_stat',
                season=season
            ).pack()
        )
    )
    return keyboard.adjust(size).as_markup() 


async def get_f1_sessions_kb(weekend_sessions, gp, season, level, size=2):
    keyboard = InlineKeyboardBuilder()
    for weekend_session in weekend_sessions:
        keyboard.add(
            InlineKeyboardButton(
                text=str(weekend_session),
                callback_data=MenuCallBack(
                    level=level+1,
                    season=season,
                    gp=gp,
                    weekend_session=weekend_session
                ).pack()
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text = "Back",
            callback_data=MenuCallBack(
                level=level-1,
                season=season,
                gp=gp
            ).pack()
        )
    )
    return keyboard.adjust(size).as_markup()   


async def get_f1_analytical_functions_kb(weekend_session, gp, season, level, size=2):
    if weekend_session == 'Race':
        buttons = [
            ('Results', 'res'),
            ('Weather Report', 'weather'),
            ('Tyre Strategy', 'tyre_strat'),
            ('Drivers pace', 'drivers_pace')]
    
    keyboard = InlineKeyboardBuilder()
    for button_text, button_level in buttons:
        keyboard.add(
            InlineKeyboardButton(
                text=str(button_text),
                callback_data=MenuCallBack(
                    level=level+1,
                    season=season,
                    gp=gp,
                    weekend_session=weekend_session,
                    analytical_function=button_level
                ).pack()
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text = "Back",
            callback_data=MenuCallBack(
                level=level-1,
                season=season,
                gp=gp,
                weekend_session=weekend_session
                ).pack()
        )
    )
    return keyboard.adjust(size).as_markup()    
