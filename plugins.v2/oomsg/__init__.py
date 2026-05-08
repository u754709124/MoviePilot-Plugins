from typing import Any, List, Dict, Tuple, Optional

from app.core.event import eventmanager, Event
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType, NotificationType
from app.utils.http import RequestUtils


class OoMsg(_PluginBase):
    # 插件名称
    plugin_name = "噢噢消息通知"
    # 插件描述
    plugin_desc = "支持使用噢噢消息小程序发送消息通知。"
    # 插件图标
    plugin_icon = "Wechat_A.png"
    # 插件版本
    plugin_version = "1.0"
    # 插件作者
    plugin_author = "chdon"
    # 作者主页
    author_url = "https://github.com/chdon"
    # 插件配置项ID前缀
    plugin_config_prefix = "oomsg_"
    # 加载顺序
    plugin_order = 28
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _onlyonce = False
    _server = None
    _apikey = None
    _deviceid = None
    _group = None
    _msgtypes = []

    # 默认服务器地址
    DEFAULT_SERVER = "https://api.chdon.com/wxpush/api/push"

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled")
            self._onlyonce = config.get("onlyonce")
            self._msgtypes = config.get("msgtypes") or []
            self._server = config.get("server") or self.DEFAULT_SERVER
            self._apikey = config.get("apikey")
            self._deviceid = config.get("deviceid")
            self._group = config.get("group") or "MoviePilot"

        if self._onlyonce:
            self._onlyonce = False
            # 关闭一次性开关并保存
            self.update_config({
                "enabled": self._enabled,
                "onlyonce": False,
                "msgtypes": self._msgtypes,
                "server": self._server,
                "apikey": self._apikey,
                "deviceid": self._deviceid,
                "group": self._group,
            })
            self._send("噢噢消息测试通知", "噢噢消息通知插件已启用")

    def get_state(self) -> bool:
        return bool(
            self._enabled
            and self._server
            and self._apikey
            and self._deviceid
        )

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        # 遍历 NotificationType 枚举，生成消息类型选项
        MsgTypeOptions = []
        for item in NotificationType:
            MsgTypeOptions.append({
                "title": item.value,
                "value": item.name
            })
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'onlyonce',
                                            'label': '测试插件（立即运行）',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'server',
                                            'label': '服务器地址',
                                            'placeholder': self.DEFAULT_SERVER,
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'apikey',
                                            'label': 'API Key',
                                            'placeholder': '推送接口鉴权密钥',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'deviceid',
                                            'label': '设备ID',
                                            'placeholder': '16位字母数字，由小程序设置页查看',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'group',
                                            'label': '消息分组',
                                            'placeholder': 'MoviePilot',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'multiple': True,
                                            'chips': True,
                                            'model': 'msgtypes',
                                            'label': '消息类型',
                                            'items': MsgTypeOptions
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '噢噢消息：通过 deviceId 与 API Key 向小程序推送 Markdown 格式通知。'
                                                    '设备ID与API Key可在“噢噢消息”小程序设置页查看。'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "onlyonce": False,
            'msgtypes': [],
            'server': self.DEFAULT_SERVER,
            'apikey': '',
            'deviceid': '',
            'group': 'MoviePilot',
        }

    def get_page(self) -> List[dict]:
        pass

    @staticmethod
    def _truncate(text: str, max_len: int) -> str:
        """
        按最大长度截断，超出的部分以省略号结尾。
        """
        if not text:
            return text
        if len(text) <= max_len:
            return text
        # 留 1 个字符给省略号
        return text[: max(1, max_len - 1)] + "…"

    def _send(self, title: str, text: str) -> Optional[Tuple[bool, str]]:
        """
        发送消息
        :param title: 标题
        :param text: 内容（Markdown）
        """
        try:
            if not self._server or not self._apikey or not self._deviceid:
                return False, "参数未配置"

            # 噢噢消息字段长度约束
            safe_title = self._truncate(title or "通知", 50)
            safe_group = self._truncate(self._group or "MoviePilot", 20)
            safe_content = self._truncate(text or " ", 5000)

            req_body = {
                "deviceId": self._deviceid,
                "group": safe_group,
                "title": safe_title,
                "content": safe_content,
            }

            headers = {
                "Content-Type": "application/json",
                "X-API-KEY": self._apikey,
            }

            res = RequestUtils(headers=headers).post_res(self._server, json=req_body)
            if res and res.status_code == 200:
                try:
                    ret_json = res.json()
                except Exception:
                    ret_json = {}
                code = ret_json.get("code")
                if code == 0:
                    logger.info("噢噢消息发送成功")
                    return True, "ok"
                else:
                    message = ret_json.get("message") or "未知错误"
                    logger.warn(f"噢噢消息发送失败：code={code}, message={message}")
                    return False, message
            elif res is not None:
                logger.warn(
                    f"噢噢消息发送失败，错误码：{res.status_code}，错误原因：{res.reason}"
                )
                return False, f"HTTP {res.status_code}"
            else:
                logger.warn("噢噢消息发送失败：未获取到返回信息")
                return False, "无响应"
        except Exception as msg_e:
            logger.error(f"噢噢消息发送失败：{str(msg_e)}")
            return False, str(msg_e)

    @eventmanager.register(EventType.NoticeMessage)
    def send(self, event: Event):
        """
        消息发送事件
        """
        if not self.get_state():
            return

        if not event.event_data:
            return

        msg_body = event.event_data
        # 渠道：仅处理无指定渠道的系统通知
        channel = msg_body.get("channel")
        if channel:
            return
        # 类型
        msg_type: NotificationType = msg_body.get("type")
        # 标题
        title = msg_body.get("title")
        # 文本
        text = msg_body.get("text")
        # 图片
        image = msg_body.get("image")

        if not title and not text:
            logger.warn("标题和内容不能同时为空")
            return

        if (msg_type and self._msgtypes
                and msg_type.name not in self._msgtypes):
            logger.info(f"消息类型 {msg_type.value} 未开启消息发送")
            return

        # 拼装 Markdown 正文：保留原文本，若有图片则附加
        content_parts = []
        if text:
            content_parts.append(str(text))
        if image:
            content_parts.append(f"![image]({image})")
        content = "\n\n".join(content_parts) if content_parts else " "

        return self._send(title or "通知", content)

    def stop_service(self):
        """
        退出插件
        """
        pass