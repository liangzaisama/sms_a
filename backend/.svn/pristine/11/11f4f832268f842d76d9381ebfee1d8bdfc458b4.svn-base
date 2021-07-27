"""
mysql数据库相关操作
"""
from pymysql import connect


class DatabaseManager:
    """mysql数据库相关操作"""

    def __init__(self, host, port, root_pwd):
        self.host = host
        self.port = port
        self.root_pwd = root_pwd
        self._conn = connect(host=host, port=port, user='root', password=root_pwd, charset='utf8')
        self._cursor = self._conn.cursor()

    def create_db_and_user(self, db_name, username, password):
        """创建数据库及用户"""
        try:
            self._cursor.execute('create database {0} default charset=utf8'.format(db_name))
            print('创建数据库成功')
            self._cursor.execute("create user {0} identified by '{1}';".format(username, password))
            print('创建用户成功')
            self._cursor.execute("grant all on {0}.* to '{1}'@'%'; ".format(db_name, username))
            print('给用户添加权限成功')
            self._cursor.execute("flush privileges;")
            print('刷新权限成功')
        finally:
            self._cursor.close()
            self._conn.close()
