import tornado.ioloop
import tornado.web

import backend


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class DataHandler(tornado.web.RequestHandler):
    def post(self):
        url = self.get_argument('url')
        video = backend.Video()
        pred = video.highlight(url)
        data = {
            'pred': pred,
        }
        self.write(data)
        del video

class ResultFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control',
                        'no-store, no-cache, must-revalidate, max-age=0')

if __name__ == '__main__':
    route = [
        (r'/', IndexHandler),
        (r'/data', DataHandler),
        (r'/result/(.*)', ResultFileHandler, { 'path': './result' }),
        (r'/static/(.*)', tornado.web.StaticFileHandler, { 'path': './static' }),
    ] # yapf: disable

    app = tornado.web.Application(route)
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()