#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, os.path, sys
import imp
import ConfigParser
import logging
import logging.handlers
import traceback

import tornado.httpserver
import tornado.ioloop
import tornado.web
import daemon.runner

import db

CONF_DIR = "./service.conf"

def load_module(module_path, settings):
    handlers = []
    modules = [(x[:-3], os.path.join(module_path, x)) for x in os.listdir(module_path) if x.endswith('.py')]
    for name, path in modules:
        m = imp.load_source(name, path)
        for x in dir(m):
            try:
                if issubclass(getattr(m, x), tornado.web.RequestHandler):
                    handlers.append((m.url, getattr(m, x), settings))
            except TypeError, e:
                pass
    return handlers

def get_config(config, section, option, default = None):
    try:
        return config.get(section, option)
    except:
        return default

class Service:
    def __init__(self, conf_file='service.conf'):
        self.config = ConfigParser.ConfigParser()
        self.config.read(conf_file)

        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = get_config(self.config, 'main', 'pidfile', None)
        self.pidfile_timeout = 3
        self.module_path = get_config(self.config, 'main', 'module_path', os.path.join(os.getcwd(), 'modules'))

        log_level = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING,
                     'error': logging.ERROR, 'critical': logging.CRITICAL}
	self.setting = {'port': get_config(self.config, 'main', 'port'),
		        'logfile': get_config(self.config, 'log', 'logfile'),
                        'log_level': log_level.get(get_config(self.config, 'log', 'level'), logging.DEBUG),
                        'db_type': get_config(self.config, 'db', 'type'),
                        'db_host': get_config(self.config, 'db', 'host'),
                        'db_user': get_config(self.config, 'db', 'user'),
                        'db_pass': get_config(self.config, 'db', 'pass'),
                        'dbname': get_config(self.config, 'db', 'dbname')}
        self.db = db.DB(self.setting)

    def run(self):
        handler = logging.handlers.TimedRotatingFileHandler(self.setting['logfile'], 'midnight', backupCount=90)
        handler.setLevel(self.setting['log_level'])
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        handler.suffix = '%Y%m%d'
        logging.getLogger().addHandler(handler)
        logging.Logger.root.setLevel(self.setting['log_level'])

        try:
            app = tornado.web.Application(handlers = load_module(self.module_path, dict(db=self.db, config=self.setting)))
            serv = tornado.httpserver.HTTPServer(app)
            serv.listen(int(self.setting['port']))
            tornado.ioloop.IOLoop.instance().start()
        except Exception, e:            
            logging.error('start service exception:')
            logging.error(e)
            logging.error(traceback.format_exc())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s [start|stop] [config_file]" % sys.argv[0]
        sys.exit()

    conf_file = sys.argv[2] if len(sys.argv) > 2 else CONF_DIR
    if not os.path.isfile(conf_file):
        print "Cannot find configure file '%s'" % conf_file
        sys.exit()

    reload(sys)
    sys.setdefaultencoding('utf8')

    runner = daemon.runner.DaemonRunner(Service(CONF_DIR))
    runner.do_action()
