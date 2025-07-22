# base_manager.py
import json
import logging
from config_provider import get_logger_name

logger = logging.getLogger(get_logger_name())


class BaseManager:
    def __init__(self, session, call_url):
        self.session = session
        self.call_url = call_url
        self.func_name = None

    def _fetch_all_records(self, limit=100):
        all_records = []
        offset = 0
        while True:
            payload = {
                "func_name": self.func_name,
                "action": "show",
                "param": {
                    "TYPE": "data,total",
                    "limit": f"{offset},{limit}",
                    "ORDER": "",
                    "ORDER_BY": ""
                }
            }
            resp = self.session.post(self.call_url, data=json.dumps(payload))
            resp.raise_for_status()
            data = resp.json().get("Data", {}).get("data", [])
            if not data:
                break
            all_records.extend(data)
            offset += limit
        return all_records

    def _delete_record_by_comment(self, comment):
        all_records = self._fetch_all_records()
        for rule in all_records:
            if rule.get("comment") == comment:
                rule_id = rule.get("id")
                del_payload = {
                    "func_name": self.func_name,
                    "action": "del",
                    "param": {"id": rule_id}
                }
                self.session.post(self.call_url, data=json.dumps(del_payload)).raise_for_status()
                logger.info(f"已删除 {self.func_name} 规则: {comment}")
                return True
        logger.warning(f"未找到注释为 {comment} 的 {self.func_name} 规则")
        return False

    def _create_or_update_rule(self, comment, new_config, existing_rules, id_key="id"):
        matched = next((r for r in existing_rules if r.get("comment") == comment), None)
        if matched:
            is_same = all(
                str(matched.get(k, "")).strip() == str(v).strip()
                for k, v in new_config.items()
                if k in matched
            )
            if is_same:
                logger.info(f"{self.func_name} 配置未变，无需修改: [{comment}]")
                return
            new_config[id_key] = matched[id_key]
            payload = {"func_name": self.func_name, "action": "edit", "param": new_config}
            self.session.post(self.call_url, data=json.dumps(payload)).raise_for_status()
            logger.info(f"已更新 {self.func_name} 配置: [{comment}]")
        else:
            payload = {"func_name": self.func_name, "action": "add", "param": new_config}
            self.session.post(self.call_url, data=json.dumps(payload)).raise_for_status()
            logger.info(f"新建 {self.func_name} 配置: [{comment}]")
