import asyncio
import json
import shutil
from pathlib import Path

from bot_engine import Router, Text, Command, Callback, MessageContext, CallbackContext
from messenger.services.message_service import MessageService
from survey.models import UserSession
from survey.services import (
    parse_survey_data,
    build_screen_payloads,
    get_user_session,
    save_user_session,
    delete_user_session,
)
from .config import INPUT_SURVEY_DATA, SCORE_MAP
from result_file_renderer.pdf import generate_management_index_report

router = Router()

WELCOME_TEXTS = {"привет", "начать", "старт", "меню", "здравствуйте", "начать тест", "старт"}


@router.message(Text("привет", "начать", "старт", "меню", "здравствуйте", "начать тест"))
async def on_welcome(ctx: MessageContext):
    await ctx.extra["reply"](
        text="👋 Здравствуйте! Отправьте '🚀 Начать тест', чтобы запустить оценку управленческих навыков.",
        buttons=[[{"label": "🚀 Начать тест", "payload": {"act": "start"}}]],
    )


@router.message(Text("🚀 Начать тест"))
@router.callback(Callback(act="start"))
async def on_start_survey(ctx: MessageContext | CallbackContext):
    redis = ctx.extra["redis"]
    reply = ctx.extra["reply"]
    user_id = ctx.user_id

    old_session = await get_user_session(redis, user_id)
    if old_session:
        # Чистим старую сессию — новый старт
        await delete_user_session(redis, user_id)

    screens = parse_survey_data(INPUT_SURVEY_DATA)
    session = UserSession(screens=screens)

    intro_text = (
        "Перед вами список из 40 управленческих навыков. Пожалуйста, оцените свой уровень "
        "владения каждым из них по шкале: Плохо / Скорее плохо / Скорее хорошо / Отлично."
    )
    await reply(text=intro_text, buttons=[])

    payloads = build_screen_payloads(session)
    await reply(text=None, buttons=None, screen_payloads=payloads)

    await save_user_session(redis, user_id, session)


@router.callback(Callback(act="select"))
async def on_select(ctx: CallbackContext):
    redis = ctx.extra["redis"]
    user_id = ctx.user_id
    q_id = ctx.payload["q_id"]
    opt_idx = ctx.payload["opt_idx"]

    session = await get_user_session(redis, user_id)
    if not session:
        await ctx.extra["reply"](text="⚠️ Сессия истекла. Начните тест заново.", buttons=[])
        return

    screen = session.current_screen
    if not any(q.id == q_id for q in screen.questions):
        await ctx.extra["reply"](text="⚠️ Сессия обновлена. Используйте актуальные кнопки!", buttons=[])
        return

    session.results[q_id] = opt_idx
    await save_user_session(redis, user_id, session)

    # Возвращаем обновлённые payload'ы текущего блока — фронтенд перерисовывает кнопки
    payloads = build_screen_payloads(session)
    await ctx.extra["reply"](text=None, buttons=None, screen_payloads=payloads)


@router.callback(Callback(act="next"))
async def on_next(ctx: CallbackContext):
    redis = ctx.extra["redis"]
    reply = ctx.extra["reply"]
    user_id = ctx.user_id

    session = await get_user_session(redis, user_id)
    if not session:
        return

    if not session.is_current_screen_complete():
        missing = _missing_question_numbers(session)
        await reply(text=f"⚠️ Заполните все ответы! Остались вопросы №: {missing}", buttons=[])
        return

    session.move_next()
    payloads = build_screen_payloads(session)
    await reply(text=None, buttons=None, screen_payloads=payloads)
    await save_user_session(redis, user_id, session)


@router.callback(Callback(act="prev"))
async def on_prev(ctx: CallbackContext):
    redis = ctx.extra["redis"]
    reply = ctx.extra["reply"]
    user_id = ctx.user_id

    session = await get_user_session(redis, user_id)
    if not session:
        return

    session.move_prev()
    payloads = build_screen_payloads(session)
    await reply(text=None, buttons=None, screen_payloads=payloads)
    await save_user_session(redis, user_id, session)


@router.callback(Callback(act="submit"))
async def on_submit(ctx: CallbackContext):
    redis = ctx.extra["redis"]
    reply = ctx.extra["reply"]
    user_id = ctx.user_id

    session = await get_user_session(redis, user_id)
    if not session:
        return

    if not session.is_current_screen_complete():
        missing = _missing_question_numbers(session)
        await reply(text=f"⚠️ Перед завершением ответьте на вопросы №: {missing}", buttons=[])
        return

    await reply(
        text="⏳ Ваши ответы приняты! Формируем PDF-отчёт, подождите 5–10 секунд...",
        buttons=[],
    )

    final_results = _build_final_results(session)

    user_dir = Path("result_file_renderer/results") / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    answers_json_path = user_dir / "answers.json"

    with open(answers_json_path, "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=4)

    try:
        result = await asyncio.to_thread(
            generate_management_index_report,
            answers_path=answers_json_path,
            methodology_path=Path("result_file_renderer/template.xlsx"),
            template_pptx_path=Path("result_file_renderer/template.pptx"),
            output_dir=user_dir,
            base_name="report",
            study_url="https://yandex.ru",
            export_pdf=True,
            sheet_name=None,
        )

        if not (result and result.pdf_path and Path(result.pdf_path).exists()):
            raise FileNotFoundError("PDF-файл не сгенерирован.")

        await reply(
            text=(
                f"🎉 Тестирование завершено!\n\n"
                f"📊 Общая средняя оценка: {result.overall_average:.2f}\n\n"
                f"Развернутый отчёт с топ-5 сильных сторон и рекомендациями прикреплён ниже."
            ),
            buttons=[],
            attachment=str(result.pdf_path),
        )

    except Exception as e:
        print(f"❌ Ошибка генерации PDF для пользователя {user_id}: {e}")
        await reply(
            text="⚠️ Произошла ошибка при формировании отчёта. Попробуйте позже.",
            buttons=[],
        )
    finally:
        if user_dir.exists():
            shutil.rmtree(user_dir)
        await delete_user_session(redis, user_id)


@router.message()
async def on_any_message(ctx: MessageContext):
    message_service: MessageService = ctx.extra["message_service"]
    await message_service.send_message_to_bot(
        author_id=ctx.user_id,
        text=ctx.text,
    )

# --- helpers ---

def _missing_question_numbers(session: UserSession) -> str:
    screen = session.current_screen
    start = sum(len(s.questions) for s in session.screens[:session.current_screen_idx]) + 1
    return ", ".join(
        str(start + idx)
        for idx, q in enumerate(screen.questions)
        if q.id not in session.results
    )


def _build_final_results(session: UserSession) -> dict:
    results = {}
    for scr in session.screens:
        for q in scr.questions:
            chosen_idx = session.results.get(q.id)
            ans_text = q.options[chosen_idx] if chosen_idx is not None else "Нет ответа"
            results[q.id] = {
                "question_text": q.question,
                "user_answer": str(SCORE_MAP.get(ans_text, 0)),
            }
    return results
