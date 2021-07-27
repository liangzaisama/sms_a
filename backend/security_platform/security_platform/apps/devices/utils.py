# from json import JSONDecodeError
import base64

import requests
from simplejson import JSONDecodeError

from security_platform import config_parser, logger
from security_platform.utils.exceptions import RequestVMSError


def request_vms(api_url, method, content_type='json'):
    """请求视频监控

    1 返回null/true/false 还是异常的判断标准，是异常行为还是正常行为，如果是异常行为就要抛出异常，否则可以抛出null等其他值
    2 不能直接抛出JSONDecodeError等调用异常，应该进行重新对异常进行封装，避免暴露细节，调用上层不关心底层异常细节
    3 如果抛出的异常跟业务有相关性，可以直接抛出异常
    4 是否进行参数校验：理论上讲，参数传递的正确性应该有程序员来保证，无需做判断，但是谁也无法保证参数的正确性，加校验是为了提高代码
      的健壮性，如果代码完成在自己的掌控范围内，可以不加校验

    Args:
        api_url: 请求地址字符串，头前不加斜线
        method: 请求方法字符串
        content_type: 响应数据类型, json:json数据，image:图片

    Returns:
        data: 视频监控客户端响应的数据
    """
    assert content_type in ['json', 'image'], 'content_type错误'

    try:
        # 拿登陆token
        token_response = requests.post(
            f"{config_parser.get('API_HOST', 'ZVAMS')}/userlogin",
            data={'username': 'admin', 'password': 'admin'}
        )
        token = token_response.json()['accessToken']

        # 使用token调接口
        response = getattr(requests, method)(
            f"{config_parser.get('API_HOST', 'VMS')}/{api_url if not api_url.startswith('/') else api_url[1:]}",
            headers={'Authorization': token}
        )

        if response.status_code != 200:
            raise RequestVMSError(errmsg=f'请求视频监控系统失败:{response.status_code}')

        if content_type == 'json':
            response_data = response.json()
            code = response_data['code']
            if int(code) != 0:
                # 请求失败，返回错误
                logger.error('视频监控系统响应异常:%s', response_data)
                raise RequestVMSError(errmsg='请求视频监控系统失败')

            data = response.json()['data']
        else:
            data = f'data:image/png;base64,{base64.b64encode(response.content).decode()}'
    except (JSONDecodeError, KeyError, requests.RequestException):
        # 将异常转为自己的异常
        logger.error('请求视频监控系统失败', exc_info=True)
        raise RequestVMSError(errmsg='请求视频监控系统失败')

    if data is None:
        raise RequestVMSError(errmsg='请求视频监控系统失败，无数据')

    return data
