import cgi
import os
import urllib
import logging

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

from django.utils import simplejson as json

# Set the debug level
_DEBUG = True

class Greeting(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  latex = db.BooleanProperty(default=False)
  date = db.DateTimeProperty(auto_now_add=True)

class BaseRequestHandler(webapp.RequestHandler):
  """Base request handler extends webapp.Request handler

     It defines the generate method, which renders a Django template
     in response to a web request
  """

  def generate(self, template_name, template_values={}):
    """Generate takes renders and HTML template along with values
       passed to that template

       Args:
         template_name: A string that represents the name of the HTML template
         template_values: A dictionary that associates objects with a string
           assigned to that object to call in the HTML template.  The defualt
           is an empty dictionary.
    """
    # We check if there is a current user and generate a login or logout URL
    user = users.get_current_user()

    if user:
      log_in_out_url = users.create_logout_url('/')
    else:
      log_in_out_url = users.create_login_url(self.request.path)

    # We'll display the user name if available and the URL on all pages
    values = {'user': user, 'log_in_out_url': log_in_out_url}
    values.update(template_values)

    # Construct the path to the template
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 'templates', template_name)

    # Respond to the request by rendering the template
    self.response.out.write(template.render(path, values, debug=_DEBUG))
    
class MainRequestHandler(BaseRequestHandler):
  def get(self):
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      }

    self.generate('index.html', template_values);

class ChatsRequestHandler(BaseRequestHandler):
  def renderChats(self):
    greetings_query = Greeting.all().order('date')
    greetings = greetings_query.fetch(1000)

    template_values = {
      'greetings': greetings,
    }

    to_serialise = [{'author': ({'nickname': g.author.nickname(),
                                'email': g.author.email()} if g.author else None),
                     'latex': g.latex,
                     'content': g.content,
                     'date': g.date.ctime()} for g in greetings]

#    self.response.headers.add_header("Content-Type", 'application/json')
    return self.response.out.write(json.dumps(to_serialise))
      
  def getChats(self, useCache=True):
    if useCache is False:
      greetings = self.renderChats()
      if not memcache.set("chats", greetings, 10):
        logging.error("Memcache set failed:")
      return greetings
      
    greetings = memcache.get("chats")
    if greetings is not None:
      return greetings
    else:
      greetings = self.renderChats()
      if not memcache.set("chats", greetings, 10):
        logging.error("Memcache set failed:")
      return greetings
    
  def get(self):
    self.getChats()

  def post(self):
    greeting = Greeting()

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.latex = bool(self.request.get('latex'))
    greeting.put()
    
    self.getChats(False) #invalidate the cache

                                       
application = webapp.WSGIApplication(
                                     [('/', MainRequestHandler),
                                      ('/getchats', ChatsRequestHandler)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
