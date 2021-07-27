"""
分布式环境下生产配置文件
"""
import os
import sys
import datetime

from rest_framework.settings import APISettings

from security_platform import config_parser

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(BASE_DIR, 'extra_apps'))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n@tjbku(a=$prygv)bh)t71!$vx)0#$x0jkvh3uu8wpw6cvq8w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = eval(config_parser.get('VARIABLE', 'ALLOWED_HOSTS'))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'crispy_forms',
    # 'corsheaders',
    'django_db_reconnect',
    'django_crontab',
    # 'django_filters',
    'reversion',
    'xadmin',
    'configurations',
    'situations',
    'devices',
    'events',
    'operations',
    'users',

    # websocket app
    'chat',
    'channels',
]

MIDDLEWARE = [
    # 'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'security_platform.utils.middleware.AddOperationFieldMiddleware',
    'security_platform.utils.middleware.ApiLoggingMiddleware'
]

# CORS
# CORS_ORIGIN_ALLOW_ALL = True
#
# CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie

ROOT_URLCONF = 'security_platform.urls'

AUTH_USER_MODEL = 'users.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'security_platform.wsgi.application'

# websocket配置
ASGI_APPLICATION = 'security_platform.routing.application'

CHANNEL_LAYERS = {
    'default': {
        "BACKEND": "channels_rabbitmq.core.RabbitmqChannelLayer",
        'CONFIG': {
            "host": f"amqp://{config_parser.get('MQTT', 'MQTT_USER')}:{config_parser.get('MQTT', 'MQTT_PWD')}@{config_parser.get('MQTT', 'MQTT_SERVER_IP')}:{config_parser.get('MQTT', 'AMQP_PORT')}/",
            "group_expiry": 86400000
        },
    },
}

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': config_parser.get('MYSQL', 'MYSQL_HOST'),
        'PORT': config_parser.get('MYSQL', 'MYSQL_PORT'),
        'USER': config_parser.get('MYSQL', 'MYSQL_USER'),
        'PASSWORD': config_parser.get('MYSQL', 'MYSQL_PASSWORD'),
        'NAME': config_parser.get('MYSQL', 'MYSQL_NAME'),
        'CONN_MAX_AGE': 900,
        'OPTIONS': {
            # "init_command": "SET group_concat_max_len = 4294967295;",
        },
    },
}

SENTINELS = eval(config_parser.get('REDIS', 'SENTINELS'))

DJANGO_REDIS_CONNECTION_FACTORY = 'django_redis.pool.SentinelConnectionFactory'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://mymaster/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.SentinelClient",
            'SENTINELS': SENTINELS,
            'SENTINEL_KWARGS': {
            },
            "CONNECTION_POOL_CLASS": "redis.sentinel.SentinelConnectionPool",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://mymaster/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.SentinelClient",
            'SENTINELS': SENTINELS,
            'SENTINEL_KWARGS': {
            },
            "CONNECTION_POOL_CLASS": "redis.sentinel.SentinelConnectionPool",
        }
    },
    "cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://mymaster/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.SentinelClient",
            'SENTINELS': SENTINELS,
            'SENTINEL_KWARGS': {
            },
            "CONNECTION_POOL_CLASS": "redis.sentinel.SentinelConnectionPool",
        }
    },
    "lock": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": [
            "redis://mymaster/3",
            "redis://mymaster/4"
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.SentinelClient",
            'SENTINELS': SENTINELS,
            'SENTINEL_KWARGS': {
            },
            "CONNECTION_POOL_CLASS": "redis.sentinel.SentinelConnectionPool",
        }
    },
    "queue": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": [
            "redis://mymaster/5",
            "redis://mymaster/6"
            "redis://mymaster/7"
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.SentinelClient",
            'SENTINELS': SENTINELS,
            'SENTINEL_KWARGS': {
            },
            "CONNECTION_POOL_CLASS": "redis.sentinel.SentinelConnectionPool",
        }
    },
}

# session提供给xadmin站点使用
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(message)s'
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            # 'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'security_platform.utils.logging_json_filter.CommonTimedRotatingFileHandler',
            'when': 'midnight',
            'atTime': datetime.time(0, 0, 0),
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/security.log"),
            'backupCount': 10,
            'formatter': 'verbose'
        },
        'usr_file': {
            'level': 'INFO',
            'class': 'security_platform.utils.logging_json_filter.CommonTimedRotatingFileHandler',
            'when': 'midnight',
            'atTime': datetime.time(0, 0, 0),
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/user_action.log"),
            'backupCount': 10,
            'formatter': 'simple'
        },
        're_file': {
            'level': config_parser.get('MQTT', 'LOG_LEVEL'),
            'class': 'security_platform.utils.logging_json_filter.CommonTimedRotatingFileHandler',
            'when': 'midnight',
            'atTime': datetime.time(0, 0, 0),
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/receive.log"),
            'backupCount': 10,
            'formatter': 'verbose'
        },
        'cron': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/crontabs.log"),
            'maxBytes': 100 * 1024 * 1024,
            'backupCount': 1,
            'formatter': 'verbose'
        },
        'websocket': {
            'level': 'INFO',
            'class': 'security_platform.utils.logging_json_filter.CommonTimedRotatingFileHandler',
            'when': 'midnight',
            'atTime': datetime.time(0, 0, 0),
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/webscoket.log"),
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            # 'level': 'DEBUG',
            'propagate': True,
        },
        'receive': {
            'handlers': ['console', 're_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'cron': {
            'handlers': ['console', 'cron'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'api': {
            'handlers': ['usr_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'websocket': {
            'handlers': ['console', 'websocket'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

REST_FRAMEWORK = {
    # 版本控制
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'ALLOWED_VERSIONS': ['2.0'],
    # 'DEFAULT_VERSION': '2.0',

    # 异常处理
    'EXCEPTION_HANDLER': 'security_platform.utils.exception_handel_views.my_exception_handler',

    # JWT认证
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'security_platform.utils.authenticate.DefineJSONWebTokenAuthentication',
        # 'rest_framework.authent ication.SessionAuthentication',
    ),

    # 接口访问默认权限 认证通过，功能权限由前端判断，后端只判断数据权限
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        # 'permissions.utils.CustomDjangoModelPermissions',
    ),

    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),

    # 分页
    'DEFAULT_PAGINATION_CLASS': 'security_platform.utils.pagination.StandardResultsSetPagination',

    # 时间格式
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",

    # 'DEFAULT_THROTTLE_CLASSES': (
    #     'rest_framework.throttling.ScopedRateThrottle',
    # ),
    #
    # 'DEFAULT_THROTTLE_RATES': {
    #     'contacts': '3/m',
    # }
}

# 指明有效期
EXPIRE_DAYS = 7

# JWT的配置
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=EXPIRE_DAYS)
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',    # 最小长度校验
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # 检查密码是否不完全是数字
    },
]

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

APPEND_SLASH = False

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media').replace('\\', '/')

MEDIA_URL = '/media/'
# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

CUSTOM_API_SETTINGS = {
    'EXPORT_PATH': os.path.join(os.path.dirname(BASE_DIR), 'excel/export.xlsx'),
    'DEFAULT_DEPATMENT': ['信息公司', '安检站', 'AOC', '消救部', 'TOC'],
    'DEFAULT_SUPER_USER_NAME': '100000',
    'DEFAULT_USER_PASSWORD': 'ABgyjc10!#%&',
    'DEFAULT_IP_CHECK_CLASSES': (
        'security_platform.utils.ipcheck.UserAuthIPCheck',
    ),
}

IMPORT_STRINGS = (
    'DEFAULT_IP_CHECK_CLASSES'
)

API_SETTINGS = APISettings(defaults=CUSTOM_API_SETTINGS, import_strings=IMPORT_STRINGS)

DISALLOWED_USER_AGENTS = [
    # re.compile(r'.*PostmanRuntime.*')
]

# DATA_UPLOAD_MAX_NUMBER_FIELDS = None
DATA_UPLOAD_MAX_NUMBER_FIELDS = None
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760*2    # 设置为最大20M

CRONJOBS = [

    # 删除过期事件数据, 每天凌晨1点执行
    ('00 1 * * **', 'crons.delete_expire_data', '>/dev/null 2>&1'),
    # 报警事件自动关闭, 每分钟执行一次
    ('*/1 * * * *', 'crons.close_expire_event', '>/dev/null 2>&1'),

]

file_format = __file__.rpartition('.')[-1]

CRONTAB_DJANGO_MANAGE_PATH = os.path.join(os.path.dirname(BASE_DIR), 'manage.{0}'.format(file_format))

# 解决crontab中文问题
CRONTAB_COMMAND_PREFIX = 'LANG=en_US.UTF-8'
