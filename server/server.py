import tornado.ioloop
import tornado.web
import tornado.websocket
import os, uuid


from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)
__UPLOADS__ = "uploads/"
# we gonna store clients in dictionary..
clients = dict()


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../client/index.html")


class Upload(tornado.web.RequestHandler):
    def post(self):
        fileinfo = self.request.file
        print("fileinfo is", fileinfo)
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        cname = str(uuid.uuid4()) + extn
        fh = open(__UPLOADS__ + cname, 'wb')
        fh.write(fileinfo['body'])
        # self.redirect("/")      # Sends the url back to the main page for websockets sake

        # self.render("../client/index.html")
        # self.finish(cname + " is uploaded!! Check %s folder" %__UPLOADS__)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        self.id = self.get_argument("Id")
        self.stream.set_nodelay(True)
        clients[self.id] = {"id": self.id, "object": self}

    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        print("Client %s received a message : %s" % (self.id, message))
        self.write_message("Connected")

    def on_close(self):
        if self.id in clients:
            del clients[self.id]

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}
# This part is the key to success. We have to redirect the websocket calls to a different URL ex//: /websocket
app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/websocket', WebSocketHandler),
    (r'/uploads', Upload),
    (r"/(apple-touch-icon\.png)", tornado.web.StaticFileHandler, dict(path=settings['static_path']))
], **settings)

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()