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

class bloglist(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class HomePage(Handler):
    def render_front(self, title="", body="", error=""):
        self.render("blog.html", title=title, body=body, error=error)
    def get(self):
        self.render_front()
    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = bloglist(title = title, body = body)
            b.put()

        self.redirect('/')

app = webapp2.WSGIApplication([('/', HomePage)], debug=True)
