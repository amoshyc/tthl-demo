import tornado.ioloop
import tornado.web

import backend


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class DataHandler(tornado.web.RequestHandler):
    def post(self):
        url = self.get_argument('url')
        pred = backend.Video().highlight(url)

        data = {
            'pred': pred,
        }
        self.write(data)
        

if __name__ == '__main__':
    route = [
        (r'/', IndexHandler),
        (r'/data', DataHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, { 'path': './static' }),
        (r'/result/(.*)', tornado.web.StaticFileHandler, { 'path': './result' }),
    ] # yapf: disable

    app = tornado.web.Application(route)
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()