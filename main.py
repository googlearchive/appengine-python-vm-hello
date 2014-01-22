"""A simple 'hello world' sample, which includes examples of start/stop
handlers, accesses the 'users' service, and shows how to get information about
the current instance.
"""

import logging
import os

import jinja2
import webapp2

from google.appengine.api import app_identity
from google.appengine.api import modules
from google.appengine.api import runtime
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


def shutdown_hook():
  """A hook function for de-registering myself."""
  instance_id = modules.get_current_instance_id()
  logging.info('shutdown_hook called for %s.', instance_id)


def get_url_for_instance(instance_id):
  """Return a full url of the current instance.
  Args:
      A string to represent an VM instance.
  Returns:
      URL string for the guestbook form on the instance.
  """
  hostname = app_identity.get_default_version_hostname()
  return 'https://{}-dot-{}-dot-{}'.format(
      instance_id, modules.get_current_version_name(), hostname)


def get_signin_navigation(original_url):
  """Return a pair of a link text and a link for logging in/out.
  Args:
      An original URL.
  Returns:
      Two-value tuple; a url and a link text.
  """
  if users.get_current_user():
      url = users.create_logout_url(original_url)
      url_linktext = 'Logout'
  else:
      url = users.create_login_url(original_url)
      url_linktext = 'Login'
  return url, url_linktext


class Hello(webapp2.RequestHandler):
  """Display a greeting, using user info if logged in, and display information
  about the instance.
  """

  def get(self):
    """Display a 'Hello' message"""
    instance_id = modules.get_current_instance_id()
    message = 'Hello'
    if users.get_current_user():
      nick = users.get_current_user().nickname()
      message += ', %s' % nick
    template = JINJA_ENVIRONMENT.get_template('index.html')
    url, url_linktext = get_signin_navigation(self.request.uri)
    self.response.out.write(template.render(instance_id=get_url_for_instance(instance_id),
                                            url=url,
                                            url_linktext=url_linktext,
                                            message=message))


class Start(webapp2.RequestHandler):
  """A handler for /_ah/start."""

  def get(self):
    """A handler for /_ah/start"""
    runtime.set_shutdown_hook(shutdown_hook)


class Stop(webapp2.RequestHandler):
  """A handler for /_ah/stop."""

  def get(self):
    """Just call shutdown_hook now, for a temporary workaround.

    With the initial version of the VM Runtime, a call to
    /_ah/stop hits this handler, without invoking the shutdown
    hook we registered in the start handler. We're working on the
    fix to make it a consistent behavior, the same as the traditional
    App Engine backends. After the fix is out, this stop handler
    won't be necessary any more.
    """
    shutdown_hook()


APPLICATION = webapp2.WSGIApplication([
    ('/', Hello),
    ('/_ah/start', Start),
    ('/_ah/stop', Stop),
], debug=True)
