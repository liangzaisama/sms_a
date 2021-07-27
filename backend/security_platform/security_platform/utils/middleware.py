"""自定义django中间件

AddOperationFieldMiddleware：增加业务字段，result等
ApiLoggingMiddleware：用户行为记录
"""
import json
import logging

from django.http import HttpResponse, FileResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
from rest_framework.response import Response

from security_platform import TextChoices
from security_platform.utils.mixins import _get_response_success_data


class AddOperationFieldMiddleware(MiddlewareMixin):
    """增加返回的业务字段

    rest_framework框架的mixin类返回时不存在固定业务字段，
    此中间件专门针对该mixin类的返回添加固有的正确业务字段
    """

    def add_operation_field(self, response):
        """添加业务字段"""
        response.data = _get_response_success_data(response.data)
        response._is_rendered = False
        response.render()

    def is_add(self, response):
        """判断是否需要添加"""
        if isinstance(response, Response):
            if response.data is None:
                response.data = {}

            if (status.HTTP_200_OK <= response.status_code <= status.HTTP_207_MULTI_STATUS and
                    'result' not in response.data):
                return True

        return False

    def process_response(self, request, response):
        """响应再次处理"""
        if self.is_add(response):
            self.add_operation_field(response)

        return response


class ApiLoggingMiddleware(MiddlewareMixin):
    """自定义中间件"""
    # 成功状态码
    SUCCESS_CODE = [200, 201, 204]
    # 成功响应类型
    SUCCESS_RESPONSE = [HttpResponse, FileResponse, Response]

    class UserLogUtils(TextChoices):
        USER = 'USER', '用户'
        AUTHORIZATIONS = 'authorizations', '登陆了'
        PASSWORD = 'password', '修改密码'
        SCENARIO = 'scenario', '自定义场景'
        CONFIG = 'config', '系统配置'

    class ActionName(TextChoices):
        POST = 'POST', '创建了'
        PUT = 'PUT', '修改了'
        PATCH = 'PATCH', '修改了'
        GET = 'GET', '查看了'
        DELETE = 'DELETE', '删除了'
        DOWNLOAD = 'DOWNLOAD', '下载了'
        BATCH_PUT = 'BATCH_PUT', '批量处理了'
        BATCH_POST = 'BATCH_POST', '批量创建了'

    def __init__(self, get_response):
        self.get_response = get_response
        self.apiLogger = logging.getLogger('api')
        self.action = None
        self.ip = None
        self.user_utils = None
        self.user = None
        self.plan = None
        self.model_name = None
        super().__init__(get_response)

    def __call__(self, request):
        """回调函数"""
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        response = response or self.get_response(request)
        if hasattr(self, 'check_response'):
            response = self.check_response(request, response)
            if hasattr(response, '_check'):
                return response
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

    def process_view(self, request, callback, callback_args, callback_kwargs):
        """相应之前处理"""
        request.re_body = getattr(request, 're_body', request.body)

        try:
            body = json.loads(request.re_body)
        except Exception:
            body = request.POST

        if callback_kwargs:
            pk = callback_kwargs['pk']
            try:
                # 获取要操作的model对象
                model = callback.cls.queryset.model
                # 获取要操作的数据对象
                instance = model.objects.get(id=pk)
            except Exception:
                # 获取执行函数之后的response
                response = callback(request, *callback_args, **callback_kwargs)
                response.renderer_context['body'] = body
                return response

            # 获取执行函数之后的response
            response = callback(request, *callback_args, **callback_kwargs)
            if type(response) in self.SUCCESS_RESPONSE:
                if type(response) is not Response:
                    self.model_name = callback.cls.queryset.model._meta.verbose_name
                    return response
            response.renderer_context['instance'] = instance
            response.renderer_context['body'] = body
            return response

        response = callback(request, *callback_args, **callback_kwargs)
        if type(response) in self.SUCCESS_RESPONSE:
            if request.path.find('xadmin') != -1:
                return response
            if type(response) is Response:
                response.renderer_context['body'] = body
            else:
                self.model_name = callback.cls.queryset.model._meta.verbose_name
        return response

    def user_login(self, body):
        """用户登陆日志记录"""
        user = body['username']
        self.action = self.UserLogUtils.AUTHORIZATIONS.label
        self.apiLogger.info("{} {} {} {}  ".format(self.user_utils,
                                                   user, self.action, self.ip))

    def user_set_password(self, request):
        """用户修改密码日志记录"""
        self.user = request.user
        self.apiLogger.info("{} {} {} {} {} ".format(self.user_utils, self.user, self.action,
                                                     self.UserLogUtils.PASSWORD.label, self.ip))

    def user_set_scenario(self, request):
        """用户修改场景值日志记录"""
        self.user = request.user
        self.apiLogger.info("{} {} {} {} {} ".format(self.user_utils, self.user, self.action,
                                                     self.UserLogUtils.SCENARIO.label, self.ip))

    def check_response(self, request, response):
        """返回参数校验"""

        if response.status_code not in self.SUCCESS_CODE or type(response) not in self.SUCCESS_RESPONSE:
            response._check = 'return'
            return response
        if request.path.find('xadmin') != -1:
            return response

        self.get_content(request, response)

        if type(response) is not Response:
            self.action = self.ActionName.DOWNLOAD.label
            return response
        view = response.renderer_context['view']
        try:
            view.serializer_class
        except Exception:
            # 通用接口直接返回不做用户操作记录
            response._check = 'return'
            return response
        if view.serializer_class is None and view.queryset is None:
            # 通用接口直接返回不做用户操作记录
            response._check = 'return'
            return response

        return response

    def cancel_object(self, cn_model_name, response):
        """记录删除数据日志"""
        instance = response.renderer_context['instance']

        self.apiLogger.info("{} {} {} {} {} {} ".format(self.user_utils, self.user, self.action,
                                                        cn_model_name, instance, self.ip))

    def put_object(self, cn_model_name, response):
        """记录编辑数据日志"""

        instance = response.renderer_context['instance']
        self.apiLogger.info("{} {} {} {} {} {} ".format(self.user_utils, self.user, self.action,
                                                        cn_model_name, instance, self.ip))

    def create_object(self, model, cn_model_name, response):
        """记录创建数据日志"""

        # 获取新增数据名字
        try:
            instance = model.objects.all().order_by('-id')[0]
        except Exception as e:
            self.apiLogger.warning(e)
            return response
        self.apiLogger.info(
            "{} {} {} {} {} {} ".format(self.user_utils, self.user, self.action, cn_model_name, instance, self.ip))

    def batch_create_object(self, model, cn_model_name, response, body):
        """记录批量创建数据日志"""

        self.action = self.ActionName.BATCH_POST.label
        try:
            instances = model.objects.all().order_by('-id')[0:len(body)]
        except Exception as e:
            self.apiLogger.warning(e)
            return response
        instances_names = [instance.__str__() for instance in instances]
        self.apiLogger.info("{} {} {} {} {} {} ".format(self.user_utils, self.user, self.action,
                                                        cn_model_name, instances_names, self.ip))

    def get_objects(self, cn_model_name):
        """记录获取数据列表日志"""
        self.apiLogger.info(
            "{} {} {} {} {} ".format(self.user_utils, self.user, self.action, cn_model_name, self.ip))

    def get_object(self, cn_model_name, response):
        """记录获取单条数据日志"""

        instance = response.renderer_context['instance']
        self.apiLogger.info("{} {} {} {} {} {} ".format(self.user_utils, self.user, self.action,
                                                        cn_model_name, instance, self.ip))

    def process_response(self, request, response):
        """相应之后处理"""
        if request.path.find('xadmin') != -1:
            return response
        if type(response) is not Response:
            self.download_response(request)
            return response

        body = response.renderer_context['body']
        endswith_path = request.path.split('/')[-1]

        # 特殊的url结尾，提前进行判断输出不同日志
        if endswith_path in self.UserLogUtils.values:
            return self.endswith_path_choice(response, endswith_path, body, request)

        view = response.renderer_context['view']
        pk = view.kwargs.get('pk')
        self.user = request.user

        try:
            # 获取操作表的中文名
            cn_model_name = view.serializer_class.Meta.model._meta.verbose_name
            # 获取要操作的model对象
            model = view.serializer_class.Meta.model
        except AttributeError:
            # 获取操作表的中文名
            cn_model_name = view.model_name
            model = view.queryset.model
        except Exception as e:
            self.apiLogger.warning(e)
            return response

        method = request.method
        response = self.request_method_choice(method, request, model, cn_model_name, response, body, pk)

        return response

    def download_response(self, request):
        """下载操作日志记录"""
        self.user = request.user
        self.apiLogger.info("{} {} {} {} {}  ".format(self.user_utils, self.user, self.action,
                                                      self.model_name, self.ip))

    def batch_response(self, cn_model_name):
        """批量操作日志记录"""
        self.action = self.ActionName.BATCH_PUT.label
        self.apiLogger.info(
            "{} {} {} {} {}  ".format(self.user_utils, self.user, self.action, cn_model_name, self.ip))

    def get_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
        else:
            ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
        self.ip = ip
        return ip

    def get_action(self, request, response):
        """获取动作"""
        action = request.method
        if action in self.ActionName.names:
            # 翻译请求动作为中文
            action = self.ActionName.dict_choices[action]
        else:
            response._check = 'return'
            return response
        self.action = action

    def get_content(self, request, response):
        """获取构造日志内容相关字段"""
        self.get_action(request, response)
        self.get_ip(request)
        self.user_utils = self.UserLogUtils.USER.label

    def endswith_path_choice(self, response, endswith_path, body, request):
        """特殊的url结尾，提前进行判断输出不同日志"""
        if endswith_path == self.UserLogUtils.AUTHORIZATIONS and request.method == self.ActionName.POST:
            self.user_login(body)

        if endswith_path == self.UserLogUtils.SCENARIO and request.method == self.ActionName.PUT:
            self.user_set_scenario(request)

        if endswith_path == self.UserLogUtils.PASSWORD and request.method == self.ActionName.PUT:
            self.user_set_password(request)

        return response

    def request_method_choice(self, method, request, model, cn_model_name, response, body, pk):
        """根据请求类型，进行判断输出不同日志"""
        if method == self.ActionName.POST:
            """创建或批量操作"""
            if request.path.endswith('batch'):
                self.batch_response(cn_model_name)
            elif isinstance(body, list):
                self.batch_create_object(model, cn_model_name, response, body)
            else:
                self.create_object(model, cn_model_name, response)

        if method == self.ActionName.DELETE:
            """删除操作"""
            self.cancel_object(cn_model_name, response)

        if method == self.ActionName.PUT or method == self.ActionName.PATCH:
            """修改操作"""
            self.put_object(cn_model_name, response)

        if method == self.ActionName.GET:
            """查看操作"""
            if pk:
                self.get_object(cn_model_name, response)
            else:
                self.get_objects(cn_model_name)

        return response
