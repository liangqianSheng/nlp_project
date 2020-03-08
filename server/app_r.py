import web

urls = (
    '/index', 'index',
    '/(.*)', 'index'
)

app = web.application(urls, globals())

class index:
    def GET(self):
        print('get')
        web.header("Access-Control-Allow-Origin", "*")
        # query = web.input()
        print('query',query)
        # get_summarization_by_sen_emb()
        
        # return query
        return "Hello, world!"

    def POST(self):
        print('post')
        web.header("Access-Control-Allow-Origin", "*")
        web.header('Access-Control-Allow-Credentials', ' true');
        web.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
        # web.header('Access-Control-Allow-Headers',
        #            'WWW-Authenticate,Authorization,Set-Cookie,X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version,name');
        web.header('Access-Control-Allow-Headers',
                   'Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization');

        data = web.input()
        return data


if __name__ == "__main__":
    app.run()