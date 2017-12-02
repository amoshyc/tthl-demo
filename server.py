import tornado.ioloop
import tornado.web

import backend


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class DataHandler(tornado.web.RequestHandler):
    def post(self):
        url = self.get_argument('url')
        backend.process(url)
        self.write('ok')


if __name__ == '__main__':
    route = [
        (r'/', IndexHandler),
        (r'/data', DataHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, { 'path': './static' }),
    ] # yapf: disable

    app = tornado.web.Application(route, debug=True)

    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()