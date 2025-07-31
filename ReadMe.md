## iKuai 管理 API
### 项目简介
iKuai 管理 API 是一个基于 FastAPI 的服务，提供 iKuai 路由器的端口映射、IP 限速和 IP 分流的管理接口。
支持同步调用 iKuai API，提供 RESTful 风格的增删查功能，适合集成到自动化运维或管理系统中。
目前在iKuai 3.7.20社区版中测试通过，API访问基于token，对于所有访问均记录日志。

### 主要功能
**端口映射（DNAT）管理**

**IP 限速管理**

**IP 分流规则管理**


### 环境要求
Python 3.9 及以上
iKuai 3.7.20
依赖包见 requirements.txt

### 安装与运行
克隆代码库,运行main.py文件

```shell
git clone https://github.com/sugar7chan/iKuai_Manager.git
cd ikuai_manager

```

### 安装依赖
```shell
pip install -r requirements.txt
```

### 编辑配置文件 config.yaml，示例结构：
```shell
device:
  ip: 192.168.157.254
  username: admin
  password: your_password
  login_retry: 3
  port: 80

log:
  name: ikuai
  log_file: ikuai.log
  level: INFO
  max_bytes: 10485760
  backup_count: 3

api_server:
  enabled: true
  port: 8080
  api_token: "your_secure_token_here"
```

### 启动主程序
```shell
python main.py
```

### API 使用说明
**认证**
所有接口均需要在请求头中携带认证 Token：
```markdown
Authorization: Bearer your_secure_token_here
端口映射
新增端口映射：POST /port-mapping

删除端口映射：DELETE /port-mapping/{comment}

查询所有端口映射：GET /port-mapping

查询指定注释的端口映射：GET /port-mapping/{comment}
```


**请求示例（新增端口映射）：**

```json
{
  "ip_addr": "192.168.1.100",
  "wan_port": "8080",
  "lan_port": "80",
  "comment": "example-port-mapping",
  "interface": "wan1",
  "protocol": "tcp+udp"
}
```
IP 限速与 IP 分流
接口格式和用法与端口映射类似。

**日志**
日志文件默认位置在配置文件指定路径，支持滚动日志。日志中包含操作记录和访问日志，方便排查和审计。

### 贡献
欢迎提交 Issues 和 Pull Requests。

### 许可证
MIT License