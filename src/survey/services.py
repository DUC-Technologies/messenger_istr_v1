import uuid
from typing import Any, Optional

from survey.models import SurveyScreen, Question, UserSession
from survey.presenter import SurveyPresenter, ScreenPayload


def parse_survey_data(raw_data: list[dict[str, Any]]) -> list[SurveyScreen]:
    screens = []
    for group in raw_data:
        block_name = group.get("block_name", "Без названия")
        questions = [Question(**q) for q in group.get("block", [])]
        screens.append(SurveyScreen(block_name=block_name, questions=questions))
    return screens


def build_screen_payloads(session: UserSession) -> list[ScreenPayload]:
    screen = session.current_screen
    start_global_idx = sum(len(s.questions) for s in session.screens[:session.current_screen_idx]) + 1

    payloads = []
    for idx, q in enumerate(screen.questions):
        if q.id not in session.q_to_msg_map:
            msg_id = uuid.uuid4()
            session.q_to_msg_map[q.id] = str(msg_id)
            session.active_message_ids.append(str(msg_id))
        
        current_msg_id = uuid.UUID(session.q_to_msg_map[q.id])

        payloads.append(SurveyPresenter.render_question(
            q=q,
            block_name=screen.block_name,
            chosen_idx=session.results.get(q.id),
            is_first=(idx == 0),
            is_last=(idx == len(screen.questions) - 1),
            current_idx=session.current_screen_idx,
            total_screens=session.total_screens,
            global_idx=start_global_idx + idx,
            message_id=current_msg_id,  # Передаем стабильный ID
        ))
    return payloads

async def get_user_session(redis_client, user_id: uuid.UUID) -> Optional[UserSession]:
    data = await redis_client.get(f"session:{user_id}")
    if not data:
        return None
    return UserSession.from_json(data.decode() if isinstance(data, bytes) else data)


async def save_user_session(redis_client, user_id: uuid.UUID, session: UserSession) -> None:
    await redis_client.set(f"session:{user_id}", session.to_json(), ex=86400)


async def delete_user_session(redis_client, user_id: uuid.UUID) -> None:
    await redis_client.delete(f"session:{user_id}")
    