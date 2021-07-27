"""
错误码定义
0(错误级别)_1（系统标示）_00（内部模块标示）_000（错误码标示）

错误级别
1: 内部错误，不需要展示给用户
2: 外部错误，需要展示给用户

系统标示
4:标示安保管理平台

内部模块标示
00 公共模块
01 用户模块
"""


class RET:
    """错误码

    首位1：内部错误，内部调试用
    首位2：外部错误，需提示用户
    """
    BADREQUESTERR       = '1400000'
    PARSEERR            = '1400001'
    AUTHENTICAERR       = '1400002'
    METHODERR           = '1400004'
    NOTACCEPTABLE       = '1400005'
    MEDIATYPEERR        = '1400006'
    THROTTLEDERR        = '1400007'
    ROUTEERR            = '1400009'
    SERVERERR           = '1400010'
    PARAMERR            = '1400011'
    MYSQLERR            = '1400012'
    REDISERR            = '1400013'
    DISAlOWHOSTERR      = '1400014'

    PERMISSIONERR       = '2400008'
    EXPARAMERR          = '2400011'
    BATCHCOUNTERROR     = '2400012'
    IPNOTALLOWED        = '2400013'
    LOGINERR            = '2401000'
    ACTIVEERR           = '2401001'
    THIRDERR            = '2401002'
    PWDERR              = '2401003'
    IPMAXCOUNTERR       = '2401004'
    UNAEMERR            = '2401005'


class ErrorType:
    """错误类型"""

    DEFAULT = 'default'
    REQUIRED = 'required'
    EXPIRE = 'expire'
    UNKNOWN = 'unknown'
    BLANK = 'blank'
    NULL = 'null'
    NOT_A_LIST = 'not_a_list'
    EVENT = 'event'
    PLAN = 'plan'
    DOES_NOT_EXIST = 'does_not_exist'
    INCORRECT_TYPE = 'incorrect_type'
    DECRYPT = 'decrypt'
    INVALID = 'invalid'
    INVALID_CHOICE = 'invalid_choice'
    INVALID_EMAIL = 'invalid_email'
    INVALID_IMAGE = 'invalid_image'
    INVALID_FORMAT = 'invalid_format'
    MAX_COUNT = 'max_count'
    MAX_LENGTH = 'max_length'
    MIN_LENGTH = 'min_length'
    MAX_VALUE = 'max_value'
    MIN_VALUE = 'min_value'
    INVALID_OLD_PWD = 'invalid_old_pwd'
    DIFFERENT_PWD = 'different_pwd'
    UNIQUE = 'unique'
    ID_LIST = 'id_list'
    LEVEL = 'level'
    DEPARTMENT = 'department'
    USER = 'user'
    DEVICE = 'device'
    ID_LIST_ADD = 'id_list_add'
    ID_LIST_DEL = 'id_list_del'
    EMPTY = 'empty'
    DEVICE_STATE = 'device_state'
    EVENT_STATE = 'event_state'
