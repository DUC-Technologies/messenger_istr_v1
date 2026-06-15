
import json
from typing import Optional


def parse_vk_reply_markup(reply_markup_str: Optional[str]) -> list[list[dict]]:
    """
    Парсит reply_markup из форматов VK в формат мессенджера list[list[dict]].
    """
    if not reply_markup_str:
        return []
    
    try:
        data = json.loads(reply_markup_str)
    except Exception:
        return []

    # Формат 2: Официальный объект VK Keyboard {"inline": ..., "buttons": [[...]]}
    if isinstance(data, dict) and "buttons" in data:
        internal_matrix = []
        for row in data["buttons"]:
            internal_row = []
            for btn in row:
                action = btn.get("action", {})
                label = action.get("label", "Кнопка")
                
                # Payload в VK может быть как строкой JSON, так и чистым объектом
                raw_payload = action.get("payload", {})
                if isinstance(raw_payload, str):
                    try:
                        payload = json.loads(raw_payload)
                    except Exception:
                        payload = {"raw": raw_payload}
                else:
                    payload = raw_payload or {}

                internal_row.append({
                    "label": label,
                    "payload": payload,
                    "selected": False
                })
            internal_matrix.append(internal_row)
        return internal_matrix

    # Формат 1: Прямая матрица [[{"label": "...", "payload": ...}]]
    elif isinstance(data, list):
        internal_matrix = []
        for row in data:
            if not isinstance(row, list):
                continue
            internal_row = []
            for btn in row:
                if not isinstance(btn, dict):
                    continue
                
                label = btn.get("label", "Кнопка")
                raw_payload = btn.get("payload", {})
                if isinstance(raw_payload, str):
                    try:
                        payload = json.loads(raw_payload)
                    except Exception:
                        payload = {"raw": raw_payload}
                else:
                    payload = raw_payload or {}

                internal_row.append({
                    "label": label,
                    "payload": payload,
                    "selected": btn.get("selected", False)
                })
            internal_matrix.append(internal_row)
        return internal_matrix

    return []
