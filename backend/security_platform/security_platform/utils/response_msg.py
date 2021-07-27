"""
根据错误码及错误类型进行错误描述映射
"""
from security_platform.utils.response_code import RET, ErrorType


ERROR_MAP = {

    # 内部
    RET.BADREQUESTERR: {
        ErrorType.DEFAULT: '错误的请求'
    },
    RET.PARSEERR: {
        ErrorType.DEFAULT: '请求数据解析错误'
    },
    RET.AUTHENTICAERR: {
        ErrorType.DEFAULT: '无效签名',
        ErrorType.EXPIRE: '签名已过期',
        ErrorType.REQUIRED: '签名未提供',
    },
    RET.METHODERR: {
        ErrorType.DEFAULT: '请求的HTTP METHOD不支持，请检查是否选择了正确的方式',
    },
    RET.NOTACCEPTABLE: {
        ErrorType.DEFAULT: '无效的版本号',
    },
    RET.MEDIATYPEERR: {
        ErrorType.DEFAULT: '不支持的媒体类型'
    },
    RET.THROTTLEDERR: {
        ErrorType.DEFAULT: '用户请求频次超过上限'
    },
    RET.PERMISSIONERR: {
        ErrorType.DEFAULT: '对不起, 您没有访问权限',   # 没有接口权限
        ErrorType.LEVEL: '对不起, 您的用户级别不足',     # 操作等级时无权限
        ErrorType.DEPARTMENT: '对不起, 您没有该部门权限',  # 操作部门时无权限
        ErrorType.DEVICE: '对不起，您没有该设备权限',    # 操作设备无权限
        ErrorType.USER: '对不起，您没有用户权限',      # 操作用户无权限
    },
    RET.ROUTEERR: {
        ErrorType.DEFAULT: '请求路径错误'
    },
    RET.SERVERERR: {
        ErrorType.DEFAULT: '服务器内部错误',
        ErrorType.UNKNOWN: '未知错误',
    },
    RET.PARAMERR: {
        ErrorType.DEFAULT: '参数{param_name}错误',
        ErrorType.REQUIRED: '缺少参数{param_name}',
        ErrorType.BLANK: '参数{param_name}不能为空',
        ErrorType.NULL: '{param_name}不能为null',
        ErrorType.INVALID: '{param_name}格式错误',
        ErrorType.INVALID_CHOICE: '{param_name}输入错误',
        ErrorType.NOT_A_LIST: '{param_name}格式错误,请传入列表',
        ErrorType.EVENT: '存在错误的事件ID或事件状态有误',
        ErrorType.PLAN: '存在错误的预案ID',
        ErrorType.DOES_NOT_EXIST: '{model_name}不存在',
        ErrorType.INCORRECT_TYPE: '{param_name}格式错误',
        ErrorType.EMPTY: '{param_name}不能为空',
        ErrorType.ID_LIST: '参数{param_name}中存在错误的{field_name}',
        ErrorType.DEVICE_STATE: '设备状态{param_name}错误，请重新选择设备',
        ErrorType.EVENT_STATE: '事件状态{param_name}错误，请重新选择事件',
    },
    RET.MYSQLERR: {
        ErrorType.DEFAULT: '存储数据库异常'
    },
    RET.REDISERR: {
        ErrorType.DEFAULT: '缓存数据库异常'
    },
    RET.DISAlOWHOSTERR: {
        ErrorType.DEFAULT: '不支持访问的域名'
    },

    # 外部
    RET.EXPARAMERR: {
        ErrorType.DEFAULT: '输入的{param_name}错误',
        ErrorType.UNIQUE: '{param_name}已存在, 请重新输入',
        ErrorType.REQUIRED: '请输入{param_name}',
        ErrorType.INVALID: '输入的{param_name}格式错误',
        ErrorType.BLANK: '输入的{param_name}为空',
        ErrorType.INVALID_EMAIL: '输入的邮箱格式有误，请重新输入',
        ErrorType.INVALID_IMAGE: '请上传有效图片，上传文件不是图片或者图片已经损坏',
        ErrorType.MAX_LENGTH: '请输入{min_length}-{max_length}个字符内的{param_name}',
        ErrorType.MIN_LENGTH: '请输入{min_length}-{max_length}个字符内的{param_name}',
        ErrorType.MAX_VALUE: '请输入{min_value}-{max_value}范围内的{param_name}',
        ErrorType.MIN_VALUE: '请输入{min_value}-{max_value}范围内的{param_name}',
        ErrorType.ID_LIST_ADD: '{param_name}已有{field_name}，请勿重复添加',
        ErrorType.ID_LIST_DEL: '{param_name}不属于选择{field_name}，请重新选择',
        ErrorType.MAX_COUNT: '{param_name}数量达到上限',
    },
    RET.LOGINERR: {
        ErrorType.DEFAULT: '用户名或密码错误',
        ErrorType.DECRYPT: '密码解密失败',
    },
    RET.UNAEMERR: {
        ErrorType.DEFAULT: '请输入正确用户名, 只能包含字母，数字和@/./+/-/_ 字符。',
        ErrorType.UNIQUE: '用户名已存在，请重新输入',
    },
    RET.ACTIVEERR: {
        ErrorType.DEFAULT: '用户已停用'
    },
    RET.THIRDERR: {
        ErrorType.DEFAULT: '第三方错误'
    },
    RET.PWDERR: {
        ErrorType.DEFAULT: '输入的密码有误',
        ErrorType.INVALID_OLD_PWD: '输入的原始密码有误',
        ErrorType.DIFFERENT_PWD: '密码确认与密码不一致',
    },
    RET.BATCHCOUNTERROR: {
        ErrorType.DEFAULT: '批量{function}最大数量不能超过{max_count}'
    },
    RET.IPMAXCOUNTERR: {
        ErrorType.DEFAULT: '用户访问授权IP最大数量为{max_count}个'
    },
    RET.IPNOTALLOWED: {
        ErrorType.DEFAULT: '未授权访问的IP'
    },

}
