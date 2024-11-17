from typing import Any, List, Dict, Tuple

from app.core.event import eventmanager, Event
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType, NotificationType

from serverchan_sdk import sc_send


class ServerChan3Msg(_PluginBase):
    # 插件名称
    plugin_name = "Server酱3消息通知"
    # 插件描述
    plugin_desc = "支持使用Server酱3发送消息通知。"
    # 插件图标
    plugin_icon = "https://github.com/u754709124/MoviePilot-Plugins/blob/main/icons/ServerChan3.png"
    # 插件版本
    plugin_version = "0.7"
    # 插件作者
    plugin_author = "Chdon"
    # 作者主页
    author_url = "https://github.com/u754709124"
    # 插件配置项ID前缀
    plugin_config_prefix = "serverchan3msg_"
    # 加载顺序
    plugin_order = 20
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _sendKey = None
    _tag = None
    _msgtypes = []

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled")
            self._msgtypes = config.get("msgtypes") or []
            self._sendKey = config.get("sendkey")
            self._tag = config.get("tag")

    def get_state(self) -> bool:
        return self._enabled and (True if self._sendKey else False)

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        # 编历 NotificationType 枚举，生成消息类型选项
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
                                            'model': 'sendkey',
                                            'label': 'Send Key',
                                            'placeholder': '',
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
                                            'model': 'tag',
                                            'label': '消息标签',
                                            'placeholder': 'MOVIE PILOT',
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
                ]
            }
        ], {
            "enabled": False,
            'msgtypes': [],
            'sendkey': '',
            'tag': 'MOVIE PILOT'
        }

    def get_page(self) -> List[dict]:
        pass

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
        # 渠道
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

        try:
            if not self._sendKey:
                return False, "参数未配置"
            send_text = text
            if image is not None:
                send_text += '\r\n![image](%s)' % image
            res = sc_send(self._sendKey, title, send_text, {"tags": self._tag})
            ret_json = res.json()
            errCode = ret_json.get('code')
            errorMsg = ret_json.get('message')
            if res:
                if errCode == 0:
                    logger.info(f"ServerChan3消息发送成功")
                else:
                    logger.warn(f"ServerChan3消息发送失败, 错误信息：{errorMsg}")
            else:
                logger.warn(f"ServerChan3消息发送失败！")
        except Exception as msg_e:
            logger.error(f"ServerChan3消息发送失败，错误信息：{str(msg_e)}")

    def stop_service(self):
        """
        退出插件
        """
        pass
