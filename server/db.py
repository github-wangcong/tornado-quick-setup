#-*- encoding: utf-8 -*-
import logging

class DB:
    def __init__(self, setting):
        if not (isinstance(setting, dict) and setting.has_key('db_type')):
            raise Exception("Config exception: Config item [db_type] required")
        self.type = setting.get('db_type')

        if self.type == 'mysql':
            import MySQLdb
            from DBUtils.PooledDB import PooledDB
            self.conns = PooledDB(creator=MySQLdb, host=setting['db_host'], user=setting['db_user'],
                                  passwd=setting['db_pass'], db=setting['dbname'], reset = False, charset='utf8')
            return

        raise Exception("DB exception: Unsupported DB type [%s]" % self.type)

    def cur_exec(self, cmd, args = None):
        if self.type == 'mysql':
            conn = self.conns.connection()
            cur = conn.cursor()
            if args and isinstance(args, tuple):
                cur.execute(cmd, args)
            else:
                cur.execute(cmd)
            return cur

    def db_get(self, cmd, args = None):
        cur = self.cur_exec(cmd, args)
        data = cur.fetchall()
        cur.close()
        return list(data)

    def db_exec(self, cmd, args = None):
        cur = self.cur_exec(cmd, args)
        self.cur_exec('commit')
