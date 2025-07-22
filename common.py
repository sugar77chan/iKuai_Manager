# common.py
import json
import logging
from config_provider import get_logger_name

logger = logging.getLogger(get_logger_name())


def fetch_all_records(session, call_url, func_name, limit=100):
    all_records = []
    offset = 0

    while True:
        payload = {
            "func_name": func_name,
            "action": "show",
            "param": {
                "TYPE": "data,total",
                "limit": f"{offset},{limit}",
                "ORDER": "",
                "ORDER_BY": ""
            }
        }
        resp = session.post(call_url, data=json.dumps(payload))
        resp.raise_for_status()

        data = resp.json().get("Data", {}).get("data", [])
        if not data:
            break

        all_records.extend(data)
        offset += limit

    return all_records


def delete_record_by_comment(session, call_url, func_name, comment, fetch_func=None):
    if not fetch_func:
        raise ValueError("fetch_func 是必须的，用于获取全部规则")

    all_records = fetch_func(session, call_url)

    for rule in all_records:
        if rule.get("comment") == comment:
            rule_id = rule["id"]
            del_payload = {
                "func_name": func_name,
                "action": "del",
                "param": {"id": rule_id}
            }
            session.post(call_url, data=json.dumps(del_payload)).raise_for_status()
            logger.info(f"[-] 已删除 {func_name} 规则: {comment}")
            return True

    logger.warning(f"[-] 未找到注释为 {comment} 的 {func_name} 规则")
    return False


def create_or_update_rule_by_comment(
        session,
        call_url,
        func_name,
        comment,
        new_config,
        existing_rules,
        id_key="id"):
    matched = next((r for r in existing_rules if r.get("comment") == comment), None)

    if matched:
        is_same = all(
            str(matched.get(k, "")).strip() == str(v).strip()
            for k, v in new_config.items()
            if k in matched
        )
        if is_same:
            logger.info(f"[=] {func_name} 配置未变，无需修改: [{comment}]")
            return

        new_config[id_key] = matched[id_key]
        payload = {"func_name": func_name, "action": "edit", "param": new_config}
        session.post(call_url, data=json.dumps(payload)).raise_for_status()
        logger.info(f"[~] 已更新 {func_name} 配置: [{comment}]")
    else:
        payload = {"func_name": func_name, "action": "add", "param": new_config}
        session.post(call_url, data=json.dumps(payload)).raise_for_status()
        logger.info(f"[+] 新建 {func_name} 配置: [{comment}]")
