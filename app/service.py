from __future__ import annotations

import logging
from typing import Any

from app.config import Settings
from app.lark import LarkClient, at_mentions, group_value, people_value
from app.mapping import MappedSubmission, map_submission
from app.store import EventStore
from app.typeform import parse_webhook


logger = logging.getLogger(__name__)


class SubmissionService:
    def __init__(self, settings: Settings, lark: LarkClient, store: EventStore) -> None:
        self.settings = settings
        self.lark = lark
        self.store = store

    def process_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        parsed = parse_webhook(payload, self.settings.typeform_form_id)
        mapped = map_submission(parsed)
        self.store.receive(mapped.token, payload, [record.route for record in mapped.routes])
        state = self.store.submission(mapped.token) or {}
        if state.get("status") == "complete" or (
            state.get("status") == "written" and not self.settings.notifications_enabled
        ):
            return {"status": "duplicate", "response_token": mapped.token}

        master_id = str(state.get("master_record_id") or "")
        if not master_id:
            master_fields = dict(mapped.master_fields)
            master_owner_ids = list(
                dict.fromkeys(
                    self.settings.owner_open_ids.get(owner, "")
                    for route in mapped.routes
                    for owner in route.owners
                    if self.settings.owner_open_ids.get(owner)
                )
            )
            if master_owner_ids:
                master_fields["负责人路由"] = people_value(master_owner_ids)
            master_id = self.lark.create_record(self.settings.lark_master_table_id, master_fields)
            self.store.set_master(mapped.token, master_id)

        failures: dict[str, str] = {}
        for route in mapped.routes:
            try:
                self._process_route(mapped, master_id, route)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Route failed: token=%s route=%s", mapped.token, route.route)
                self.store.set_route_error(mapped.token, route.route, str(exc))
                failures[route.route] = str(exc)

        complete = self.store.mark_complete_if_ready(mapped.token) if self.settings.notifications_enabled else False
        written = complete or self.store.mark_written_if_ready(mapped.token)
        self.lark.update_record(
            self.settings.lark_master_table_id,
            master_id,
            {
                "分流状态": "已分流" if written and not failures else "分流失败",
                "通知状态": (
                    "已通知"
                    if complete
                    else (
                        "待通知"
                        if not self.settings.notifications_enabled and not failures
                        else ("部分通知成功" if len(failures) < len(mapped.routes) else "通知失败")
                    )
                ),
            },
        )
        if failures:
            raise RuntimeError(f"Partial processing failure: {failures}")
        return {
            "status": "complete" if complete else "written",
            "response_token": mapped.token,
            "master_record_id": master_id,
        }

    def _process_route(self, mapped: MappedSubmission, master_id: str, route: Any) -> None:
        route_state = self.store.route(mapped.token, route.route) or {}
        if route_state.get("status") == "notified":
            return

        table_id = self.settings.table_ids[route.route]
        record_id = str(route_state.get("record_id") or "")
        owner_ids = [self.settings.owner_open_ids[name] for name in route.owners]
        if not record_id:
            fields = dict(route.fields)
            fields["关联总申请"] = [master_id]
            reviewer_value = people_value(owner_ids)
            if reviewer_value:
                fields["审核负责人"] = reviewer_value
            notification_group = group_value(self.settings.notification_chat_id)
            if notification_group:
                fields["通知群"] = notification_group
            record_id = self.lark.create_record(table_id, fields)
            self.store.set_route_record(mapped.token, route.route, record_id)

        if not self.settings.notifications_enabled:
            return

        message_id = str(route_state.get("message_id") or "")
        if not message_id:
            mentions = at_mentions(route.owners, self.settings.owner_open_ids)
            url = f"https://asgnwd2jk3jn.sg.larksuite.com/base/{self.settings.lark_base_token}?table={table_id}&record={record_id}"
            text = self._notification_text(mapped, route, mentions, url)
            message_id = self.lark.send_group_text(self.settings.notification_chat_id, text)
            self.store.set_route_message(mapped.token, route.route, message_id)
        self.lark.update_record(table_id, record_id, {"通知状态": "已通知", "飞书通知消息 ID": message_id})
        self.store.set_route_notified(mapped.token, route.route, message_id)

    @staticmethod
    def _route_title(route: str) -> str:
        return {"ecosystem": "生态扶持奖励", "gas": "Gas 返佣", "event": "活动合作", "incubation": "孵化加速"}[route]

    @classmethod
    def _notification_text(cls, mapped: MappedSubmission, route: Any, mentions: str, url: str) -> str:
        title = cls._route_title(route.route)
        owners = "、".join(route.owners)
        mention_line = f"{mentions}\n" if mentions else ""
        return (
            f"{mention_line}【新申请待审核｜{title}】\n\n"
            f"项目名称：{mapped.project_name}\n"
            f"申请类型：{title}\n"
            f"审核负责人：{owners}\n"
            "当前状态：待审核\n\n"
            f"审核入口：{url}\n\n"
            "请审核负责人核对申请资料，并在对应分流表中及时更新审核状态。"
        )
