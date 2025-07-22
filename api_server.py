import logging
import traceback
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field

# 请求模型定义
class PortMapRequest(BaseModel):
    ip_addr: str
    wan_port: str
    lan_port: str
    comment: str
    interface: str = Field("wan1")
    protocol: str = Field("tcp+udp")

class QosRequest(BaseModel):
    ip_addr: str
    upload: int
    download: int
    comment: str
    interface: str = "wan1"
    protocol: str = "tcp+udp"

class StreamRequest(BaseModel):
    src_addr: str
    interface: str = "vwan_cmcc"
    comment: str
    protocol: str = "tcp+udp"
    mode: str = "3"  # 默认智能分流模式


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            self.logger.info(f"[{client_ip}] {method} {path} -> {response.status_code}")
            return response
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"[{client_ip}] {method} {path} 异常: {e}\n{tb}")
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


def create_api_app(port_mgr, qos_mgr, stream_mgr, logger_name, api_token):
    logger = logging.getLogger(logger_name)
    app = FastAPI(
        title="iKuai 管理 API",
        description="提供端口映射、IP 限速、IP 分流配置接口"
    )

    # 注册日志中间件
    app.add_middleware(LoggingMiddleware, logger=logger)

    # 认证依赖函数，必须用 Depends
    async def verify_token(x_api_token: str = Header(None), request: Request = None):
        client_ip = request.client.host if request else "unknown"
        if x_api_token != api_token:
            logger.warning(f"[认证失败] 来自 {client_ip} 的请求使用了错误的 API Token")
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Token")

    # 端口映射接口
    @app.post("/port-mapping", dependencies=[Depends(verify_token)])
    def add_port_mapping(req: PortMapRequest):
        try:
            port_mgr.config_port(
                ip_addr=req.ip_addr,
                wan_port=req.wan_port,
                lan_port=req.lan_port,
                comment=req.comment,
                interface=req.interface,
                protocol=req.protocol
            )
            return {"status": "ok", "msg": f"新增端口映射 [{req.comment}] 成功"}
        except Exception as e:
            logger.exception("[port-mapping] 新增失败")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/port-mapping/{comment}", dependencies=[Depends(verify_token)])
    def delete_port_mapping(comment: str):
        try:
            port_mgr.delete_by_comment(comment)
            return {"status": "ok", "msg": f"删除端口映射 [{comment}] 成功"}
        except Exception as e:
            logger.exception("[port-mapping] 删除失败")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/port-mapping", dependencies=[Depends(verify_token)])
    def list_port_mappings():
        try:
            data = port_mgr.get_all()
            return {"status": "ok", "data": data}
        except Exception as e:
            logger.exception("[port-mapping] 查询全部失败")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/port-mapping/{comment}", dependencies=[Depends(verify_token)])
    def get_port_mapping(comment: str):
        try:
            result = port_mgr.get_by_comment(comment)
            return {"status": "ok", "data": result or []}
        except Exception as e:
            logger.exception("[port-mapping] 查询失败")
            raise HTTPException(status_code=500, detail=str(e))

    # IP 限速接口
    @app.post("/qos-limit", dependencies=[Depends(verify_token)])
    def add_qos_limit(req: QosRequest):
        try:
            qos_mgr.config_limit(
                ip_addr=req.ip_addr,
                upload=req.upload,
                download=req.download,
                interface=req.interface,
                comment=req.comment,
                protocol=req.protocol
            )
            return {"status": "ok", "msg": f"新增 IP 限速 [{req.comment}] 成功"}
        except Exception as e:
            logger.exception("[qos-limit] 新增失败")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/qos-limit/{comment}", dependencies=[Depends(verify_token)])
    def delete_qos_limit(comment: str):
        try:
            qos_mgr.delete_by_comment(comment)
            return {"status": "ok", "msg": f"删除 IP 限速 [{comment}] 成功"}
        except Exception as e:
            logger.exception("[qos-limit] 删除失败")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/qos-limit", dependencies=[Depends(verify_token)])
    def list_qos_limits():
        try:
            data = qos_mgr.get_all()
            return {"status": "ok", "data": data}
        except Exception as e:
            logger.exception("[qos-limit] 查询全部失败")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/qos-limit/{comment}", dependencies=[Depends(verify_token)])
    def get_qos_limit(comment: str):
        try:
            result = qos_mgr.get_by_comment(comment)
            return {"status": "ok", "data": result or []}
        except Exception as e:
            logger.exception("[qos-limit] 查询失败")
            raise HTTPException(status_code=500, detail=str(e))

    # IP 分流接口
    @app.post("/stream-ipport", dependencies=[Depends(verify_token)])
    def add_stream_rule(req: StreamRequest):
        try:
            stream_mgr.config_stream(
                src_addr=req.src_addr,
                interface=req.interface,
                comment=req.comment,
                protocol=req.protocol,
                mode=req.mode
            )
            return {"status": "ok", "msg": f"新增分流规则 [{req.comment}] 成功"}
        except Exception as e:
            logger.exception("[stream-ipport] 新增失败")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/stream-ipport/{comment}", dependencies=[Depends(verify_token)])
    def delete_stream_rule(comment: str):
        try:
            stream_mgr.delete_by_comment(comment)
            return {"status": "ok", "msg": f"删除分流规则 [{comment}] 成功"}
        except Exception as e:
            logger.exception("[stream-ipport] 删除失败")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/stream-ipport", dependencies=[Depends(verify_token)])
    def list_stream_rules():
        try:
            data = stream_mgr.get_all()
            return {"status": "ok", "data": data}
        except Exception as e:
            logger.exception("[stream-ipport] 查询全部失败")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/stream-ipport/{comment}", dependencies=[Depends(verify_token)])
    def get_stream_rule(comment: str):
        try:
            result = stream_mgr.get_by_comment(comment)
            return {"status": "ok", "data": result or []}
        except Exception as e:
            logger.exception("[stream-ipport] 查询失败")
            raise HTTPException(status_code=500, detail=str(e))

    return app
