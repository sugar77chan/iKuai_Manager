# stream_ipport.py
from base_manager import BaseManager


class StreamIpPortManager(BaseManager):
    def __init__(self, session, call_url):
        super().__init__(session, call_url)
        self.func_name = "stream_ipport"

    def get_all(self):
        return self._fetch_all_records()

    def get_by_comment(self, comment):
        rules = self.get_all()
        return [r for r in rules if r.get("comment") == comment]

    def config_stream(self, src_addr, interface="vwan_cmcc", protocol="tcp+udp", mode="3",comment=""):
        new_config = {
            "src_addr": src_addr,
            "interface": interface,
            "enabled": "yes",
            "mode": mode,
            "protocol": protocol,
            "time": "00:00-23:59",
            "type": 0,
            "week": "1234567",
            "comment": comment
        }
        existing_rules = self.get_all()
        self._create_or_update_rule(comment, new_config, existing_rules)

    def delete_by_comment(self, comment):
        self._delete_record_by_comment(comment)
