import asyncio
import json
import uuid
from pathlib import Path

from bot_engine import Router, Text, Callback, MessageContext, CallbackContext
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
from infra.s3_storage import S3StorageService, make_report_object_key
import settings

router = Router()


@router.message(Text("привет", "начать", "старт", "меню", "здравствуйте", "начать тест"))
async def on_welcome(ctx: MessageContext):
    await ctx.extra["reply"](
        text="👋 Здравствуйте! Отправьте '🚀 Начать тест', чтобы запустить оценку управленческих навыков.",
        buttons=[[{"label": "🚀 Начать тест", "payload": {"act": "start"}}]],
    )


@router.message(Text("🚀 начать тест"))
@router.callback(Callback(act="start"))
async def on_start_survey(ctx: MessageContext | CallbackContext):
    redis = ctx.extra["redis"]
    reply = ctx.extra["reply"]
    user_id = ctx.user_id

    old_session = await get_user_session(redis, user_id)
    if old_session:
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

    # Сохраняем ID сообщений старого блока перед тем, как переключить экран и стереть их
    old_message_ids = list(session.active_message_ids)
    # TODO: Если ваш протокол поддерживает системные события (например, 'delete_messages'), 
    # можно передать старые ID на фронтенд для их очистки.

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
    s3_service: S3StorageService = ctx.extra["s3_service"]
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

    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        answers_json_path = tmp_path / "answers.json"
        answers_json_path.write_text(
            json.dumps(final_results, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )

        try:
            result = await asyncio.to_thread(
                generate_management_index_report,
                answers_path=answers_json_path,
                methodology_path=Path("src/result_file_renderer/template.xlsx"),
                template_pptx_path=Path("src/result_file_renderer/template.pptx"),
                output_dir=tmp_path,
                base_name="report",
                study_url="https://yandex.ru",
                export_pdf=True,
                sheet_name=None,
            )

            if not (result and result.pdf_path and Path(result.pdf_path).exists()):
                raise FileNotFoundError("PDF-файл не сгенерирован.")

            pdf_bytes = Path(result.pdf_path).read_bytes()
            object_key = make_report_object_key(user_id)
            await s3_service.upload_file(
                bucket=settings.S3_BUCKET_REPORTS,
                object_key=object_key,
                file_bytes=pdf_bytes,
                content_type="application/pdf",
            )

            await reply(
                text=(
                    f"🎉 Тестирование завершено!\n\n"
                    f"📊 Общая средняя оценка: {result.overall_average:.2f}\n\n"
                    f"Развернутый отчёт с топ-5 сильных сторон и рекомендациями прикреплён ниже."
                ),
                buttons=[],
                attachment_object_key=object_key,
                attachment_file_name="report.pdf",
                attachment_content_type="application/pdf",
            )

        except Exception as e:
            print(f"❌ Ошибка генерации PDF для пользователя {user_id}: {e}")
            await reply(
                text="⚠️ Произошла ошибка при формировании отчёта. Попробуйте позже.",
                buttons=[],
            )
        finally:
            await delete_user_session(redis, user_id)


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
