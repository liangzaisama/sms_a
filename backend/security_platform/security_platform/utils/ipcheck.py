class BaseIPCheck:

    def get_request_ip(self, request):
        """获取请求ip地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # 所以这里是真实的ip
            return x_forwarded_for.split(',')[0]

        # 这里获得代理ip
        return request.META.get('REMOTE_ADDR')

    def validate(self, request, view):
        return True


# class BlackIPCheck(BaseIPCheck):
#     """黑名单ip访问校验"""
#
#     def validate(self, request, view):
#         return True


class UserAuthIPCheck(BaseIPCheck):
    """用户授权ip访问校验"""

    def is_auth_ip(self, auth_ips, request_ip):
        split_request_ip = request_ip.split('.')
        split_request_ip.pop()
        str_ip_segment = ''.join(split_request_ip)

        for auth_ip in auth_ips:
            split_auth_ip = auth_ip.split('.')

            if int(split_auth_ip[-1]) == 0:
                # ip段 校验前三位是否一样
                split_auth_ip.pop()
                if ''.join(split_request_ip) == str_ip_segment:
                    return True
            else:
                # ip地址 校验是否完全一致
                if request_ip == auth_ip:
                    return True

        return False

    def validate(self, request, view):
        user = request.user
        request_ip = self.get_request_ip(request)

        if not user.is_authenticated or request_ip == '127.0.0.1':
            # 匿名用户, 不限制
            return True

        auth_ips = user.useripwhitelist_set.all().values_list('ip_address', flat=True)
        if not auth_ips or '0.0.0.0' in auth_ips:
            # 未设置授权ip, 放行
            return True

        return self.is_auth_ip(auth_ips, request_ip)
