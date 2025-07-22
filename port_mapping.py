# port_mapping.py
from base_manager import BaseManager


class PortMappingManager(BaseManager):
    def __init__(self, session, call_url):
        super().__init__(session, call_url)
        self.func_name = "dnat"

    def get_all(self):
        return self._fetch_all_records()

    def get_by_comment(self, comment):
        rules = self.get_all()
        return [r for r in rules if r.get("comment") == comment]

    def config_port(self, ip_addr, wan_port, lan_port, comment, interface="wan1", protocol="tcp+udp"):
        new_config = {
            "ip_addr": ip_addr,
            "wan_port": wan_port,
            "lan_port": lan_port,
            "comment": comment,
            "interface": interface,
            "protocol": protocol
        }
        existing_rules = self.get_all()
        self._create_or_update_rule(comment, new_config, existing_rules)

    def delete_by_comment(self, comment):
        self._delete_record_by_comment(comment)
