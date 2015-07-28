# -*- coding: utf-8 -*-
import tornado.web
import logging
url = '/show'

class CutHandler(tornado.web.RequestHandler):
    def initialize(self, db, config):
        self.db = db
        self.config = config

    def feedback(self, status, content):
        self.set_status(status)
        self.set_header('Content-Type', 'text/plain;charset=utf-8')
        self.write(content)

    def get(self):
	self.feedback(200, 'Hello World')
