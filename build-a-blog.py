import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPosts(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class HomePage(Handler):
    def render_front(self):
        blogs = db.GqlQuery("SELECT * FROM BlogPosts ORDER BY created DESC LIMIT 5")
        self.render("home.html", blogs=blogs)
    def get(self):
        self.render_front()
    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = BlogPosts(title = title, body = body)
            b.put()
            self.redirect('/')
        else:
            error = "Please enter both a title and a body"
            self.render_front(title, body, error)

class NewPost(Handler):
    def render_front(self, title="", body="", error=""):
        self.render("newpost.html", title=title, body=body, error=error)
    def get(self):
        self.render_front()
    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post = BlogPosts(title = title, body = body)
            post.put()
            post_id = post.key().id()
            post_id = str(post_id)
            self.redirect('/blog/' + post_id)
        else:
            error = "Please enter both a title and a body"
            self.render_front(title, body, error)

class AllBlogs(Handler):
    def get(self):
        allblogs = db.GqlQuery("SELECT * FROM BlogPosts ORDER BY created DESC")
        post_id = []
        n = 0
        for blog in allblogs:
            post_id.append(blog.key().id())
            post_id[n] = str(post_id[n])
            n+=1
        self.render("allblogs.html", post_id=post_id, allblogs=allblogs, blog=blog)


class ViewPostHandler(Handler):
    def get(self, id):
        id_num = int(id)
        if BlogPosts.get_by_id(id_num):
            blog = BlogPosts.get_by_id(id_num)
            self.render("single-blog.html", blog=blog)
        else:
            self.response.write("not found")



app = webapp2.WSGIApplication([('/', HomePage),
                               ('/newpost', NewPost),
                               ('/all-blogs', AllBlogs),
                  webapp2.Route('/blog/<id:\d+>', ViewPostHandler)],
                              debug=True)
