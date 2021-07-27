class MasterSlaveRouter:
    """数据库读取分离路由分发

    职责链模式：
    如果存在多个Router时
    如果返回None, 则依次调用其他路由获取操作的数据库
    如果返回数据库别名，则使用，停止调用其他路由

    可能存在的bug
    由于写入传播到复制副本需要时间，导致查询不一致
    也没有考虑事务与数据库利用策略的交互
    """
    def db_for_read(self, model, **hints):
        """读操作走从库"""
        # print('读操作走从库')
        return "slave"

    def db_for_write(self, model, **hints):
        """写操作走主库"""
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """允许关联关系"""
        return True
