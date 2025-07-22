from config_provider import get_config, get_logger_name
from logger import setup_logger
from auth import IKUAIAuth
from port_mapping import PortMappingManager
from qos_limit import QosManager
from stream_ipport import StreamIpPortManager
from api_server import create_api_app
import uvicorn


def main():
    config = get_config()
    logger_name = get_logger_name()
    logger = setup_logger(config.get_log_config())
    device_cfg = config.get_device_config()

    try:
        auth = IKUAIAuth(
            ip=device_cfg["ip"],
            username=device_cfg["username"],
            password=device_cfg["password"],
            port=device_cfg.get("port", 80),
            login_retry=device_cfg.get("login_retry"),
            auto_login=True
        )
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return

    # 初始化管理器
    port_mgr = PortMappingManager(auth.session, auth.call_url)
    qos_mgr = QosManager(auth.session, auth.call_url)
    stream_mgr = StreamIpPortManager(auth.session, auth.call_url)

    api_server_cfg = config.get_api_server_config()

    if api_server_cfg.get("enabled", False):
        app = create_api_app(port_mgr, qos_mgr, stream_mgr, logger_name,api_token=api_server_cfg.get("api_token"))
        logger.info(f"启动 API 服务器，端口 {api_server_cfg.get('port', 8080)}")
        uvicorn.run(app, host="0.0.0.0", port=api_server_cfg.get("port", 8080))
    else:
        logger.info("api_server 配置为未启用，跳过启动。")


if __name__ == "__main__":
    main()
