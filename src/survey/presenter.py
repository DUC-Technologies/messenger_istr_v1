from dataclasses import dataclass
from typing import Optional
import uuid
from survey.models import Question


@dataclass(frozen=True)
class Button:
    label: str
    payload: dict
    selected: bool = False


@dataclass(frozen=True)
class ScreenPayload:
    text: str
    buttons: list[list[Button]]
    message_id: uuid.UUID


class SurveyPresenter:

    @staticmethod
    def render_question(
        q: Question,
        block_name: str,
        chosen_idx: Optional[int],
        is_first: bool,
        is_last: bool,
        current_idx: int,
        total_screens: int,
        global_idx: int,
        message_id: uuid.UUID,  # ДОБАВЛЕНО: принимаем ID из сервиса
    ) -> ScreenPayload:
        lines = []
        if is_first:
            lines.append(f"📋 Блок: {block_name} (Часть {current_idx + 1} из {total_screens})")
            lines.append("──────────────────────────")
        lines.append(f"{global_idx}. {q.question}")

        option_rows = [
            [Button(
                label=opt,
                payload={"act": "select", "q_id": q.id, "opt_idx": opt_idx},
                selected=(chosen_idx == opt_idx),
            )]
            for opt_idx, opt in enumerate(q.options)
        ]

        nav_buttons: list[Button] = []
        if is_last:
            if current_idx > 0:
                nav_buttons.append(Button(label="⬅️ Назад", payload={"act": "prev"}))
            if current_idx == total_screens - 1:
                nav_buttons.append(Button(label="📥 Завершить", payload={"act": "submit"}))
            else:
                nav_buttons.append(Button(label="Далее ➡️", payload={"act": "next"}))

        rows = option_rows + ([nav_buttons] if nav_buttons else [])
        return ScreenPayload(text="\n".join(lines), buttons=rows, message_id=message_id)
