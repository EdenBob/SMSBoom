# encoding=utf8
from pathlib import Path
from loguru import logger
import sys
from pydantic import BaseModel, validator
from typing import Optional, Union
import httpx
from datetime import datetime
import json

# logger config
logger.remove()
logger.add(
    sink=sys.stdout,
    format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> - <level>{level}</level> - <level>{message}</level>",
    colorize=True,
    backtrace=True
)

json_path = Path(Path(__file__).parent.parent, "api.json")
if not json_path.exists():
    logger.error("Json file not exists in default directory!")
    sys.exit(1)

default_header = {
    "User-Agent": "Mozilla/5.0 (Linux; U; Android 10; zh-cn; Mi 10 Build/QKQ1.191117.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/79.0.3945.147 Mobile Safari/537.36 XiaoMi/MiuiBrowser/13.5.40"
}


class API(BaseModel):
    desc: str = "Default"
    url: str
    method: str = "GET"
    header: Optional[Union[str, dict]] = default_header
    data: Optional[Union[str, dict]]


    def replace_data(self, content: Union[str, dict], phone) -> str:
        if not phone:
            return content
        # 统一转换成 str 再替换.
        content = str(content).replace("[phone]", phone).replace(
            "[timestamp]", self.timestamp_new()).replace("'",'"')
        # 尝试 json 化
        try:
            return json.loads(content)
        except:
            return content

    def timestamp_new(self) -> str:
        """返回整数字符串时间戳"""
        return str(int(datetime.now().timestamp()))

    def handle_API(self, phone=None):
        """
        :param API: one API basemodel
        :return: API basemodel
        """
        # if isinstance(self.data, str):
        #     if self.data:
        #         self.data = json.loads(self.data)
        if isinstance(self.header, str):
            if self.header:
                self.header = json.loads(self.header)
        self.data = self.replace_data(self.data, phone)
        self.url = self.replace_data(self.url, phone)
        return self


def test_resq(api: API, phone) -> httpx.Response:
    """测试 API 返回响应
    :param api: API model
    :param phone: 手机号
    :return: httpx 请求对象.
    """
    api = api.handle_API(phone)
    with httpx.Client(headers=default_header, timeout=8) as client:
        if not isinstance(api.data, dict):
            print("data")
            resp = client.request(method=api.method, headers=api.header,
                           url=api.url, data=api.data)
        else:
            print('json')
            resp = client.request(
                method=api.method, headers=api.header, url=api.url, json=api.data)
    return resp


if __name__ == '__main__':
    pass
