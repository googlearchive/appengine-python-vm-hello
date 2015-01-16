# Copyright 2014 Google Inc. All Rights Reserved.

"""Docker registry to push/pull docker images to/from Google Cloud Storage.

Registry runs in a Docker container.
"""

from collections import namedtuple

import json
import time

from googlecloudsdk.appengine.lib import appengine_code_importer
from googlecloudsdk.appengine.lib.images import config
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import constants as const_lib
from googlecloudsdk.core.util import docker as docker_lib

with appengine_code_importer.Importer() as importer:
  containers = importer.Import('tools.docker.containers')


_DOCKER_REGISTRY_URL_TMPL = 'http://%s/v1/_ping'

_GOOGLE_NAMESPACE_PREFIX = 'google/'


class Error(Exception):
  """Base exception for registry module."""


def _Retry(func, *args, **kwargs):
  """Retries the function if an exception occurs.

  Args:
    func: The function to call and retry.
    *args: Args to pass to the function.
    **kwargs: Kwargs to pass to the function.

  Returns:
    Whatever the function returns.
  """
  retries = 60
  while True:
    try:
      return func(*args, **kwargs)
    except Exception as e:  # pylint: disable=broad-except
      retries -= 1
      if retries > 0:
        log.info('Exception {e} thrown in {func}. Retrying.'.format(
            e=e, func=func.__name__))
        time.sleep(1)
      else:
        raise e


RegistryOptions = namedtuple(
    'RegistryOptions', [
        'port',
        'credentials',
        'bucket',
        'project_id',
        'storage_path',
        'boto_path'
    ]
)


class _Registry(object):
  """Google Registry Interface."""

  @property
  def docker_client(self):
    raise NotImplementedError(
        'Subtypes must provide an implementation for docker_client')

  def Start(self):
    """Prepare this registry for use."""
    raise NotImplementedError(
        'Subtypes must provide an implementation for Start')

  def Stop(self):
    """Finalize this registry."""
    raise NotImplementedError(
        'Subtypes must provide an implementation for Stop')

  def GetRepoImageTag(self, image_tag):
    """Translates the tag into an addressable entity with this registry."""
    raise NotImplementedError(
        'Subtypes must provide an implementation for GetRepoImageTag')


def _Sanitize(string):
  """Make the string a suitable docker namespace.

  Docker doesn't yet support hyphens in the namespace,
  so we accept the substitution '_' which is illegal
  in project ids.

  Args:
    string: a string to sanitize for use as a docker namespace.

  Returns:
    the input, properly sanitized for use as a docker namespace.
  """
  return string.replace('-', '_')


def _StripDomain(project_id):
  """This strips the domain from an appid, if qualified with one."""
  split_id = project_id.split(':')
  if len(split_id) == 1:
    return split_id[0]
  return split_id[1]


class _GoogleContainerRegistry(_Registry):
  """Google Container Engine Registry."""

  def __init__(self, options, addr):
    self.addr = addr
    self._options = options
    self._docker_client = None

  @property
  def docker_client(self):
    return self._docker_client

  def Start(self):
    docker_lib.UpdateDockerCredentials(self.addr)
    # Disallow access to the docker client prior to calling Start, so that we
    # don't inadvertently use cached credentials instead of the fresh ones above
    self._docker_client = containers.NewDockerClient(
        version=config.DOCKER_PY_VERSION,
        timeout=config.DOCKER_D_REQUEST_TIMEOUT)
    log.debug('Configured access to {server}.'.format(server=self.addr))
    return

  def Stop(self):
    pass

  def GetRepoImageTag(self, image_tag):
    if self._options.project_id:
      display = _StripDomain(self._options.project_id)
      return '%s/_m_%s/%s' % (self.addr, _Sanitize(display), image_tag)
    else:
      # NOTE: we only expect to see containers-{qa, prod} on this
      # path, so this is a safe substitution.
      # NOTE: we also strip the 'google/' prefix from the image name
      # in this case.
      prefix_len = len(_GOOGLE_NAMESPACE_PREFIX)
      return '%s/_b_%s/%s' % (self.addr,
                              _Sanitize(self._options.bucket),
                              image_tag[prefix_len:])


class _LocalRegistry(_Registry):
  """Local Docker Registry path using google/docker-registry."""

  def __init__(self, options):
    self._options = options
    self._registry = None

  @property
  def docker_client(self):
    # Not valid until Start has been called.
    return self._docker_client

  def Start(self):
    cred_containers = []
    if self._options.credentials and self._options.credentials.name:
      cred_containers.append(self._options.credentials.name)

    # An empty STORAGE_PATH breaks the registry. See b/18722295.
    environment = {'BOTO_PATH': self._options.boto_path,
                   'GCS_BUCKET': self._options.bucket}
    storage_path = self._options.storage_path.strip()
    if storage_path:
      environment['STORAGE_PATH'] = storage_path

    container_opts = containers.ContainerOptions(
        containers.ImageOptions(
            # Uses pre-built registry image.
            dockerfile_dir=None,
            tag=config.DOCKER_REGISTRY_TAG,
            nocache=False),
        port=self._options.port,
        environment=environment,
        volumes_from=cred_containers)
    log.debug('Starting registry container with opts: %s', container_opts)

    self._docker_client = containers.NewDockerClient(
        version=config.DOCKER_PY_VERSION,
        timeout=config.DOCKER_D_REQUEST_TIMEOUT)

    self._registry = containers.Container(self._docker_client, container_opts)
    self._registry.Start()

  def Stop(self):
    self._registry.Stop()

  def GetRepoImageTag(self, image_tag):
    return 'localhost:%s/%s' % (self._registry.port, image_tag)


def ProgressHandler(action, func_with_output_lines):
  """Handles the streaming output of the docker client.

  Args:
    action: str, action verb for logging purposes, for example "push" or "pull".
    func_with_output_lines: a function streaming output from the docker client.
  Raises:
    Error: if a problem occured during the operation with an explanation
           string if possible.
  """
  for line in func_with_output_lines():
    log_record = json.loads(line.strip())
    if 'status' in log_record:
      feedback = log_record['status'].strip()
      if 'progress' in log_record:
        feedback += ': ' + log_record['progress'] + '\r'
      else:
        feedback += '\n'
      log.err.write(feedback)
    elif 'error' in log_record:
      error = log_record['error'].strip()
      log.error(error)
      raise Error('Unable to %s the image to/from the registry: "%s"' %
                  (action, error))
    elif 'errorDetail' in log_record:
      error_detail = log_record['errorDetail'] or 'Unknown Error'
      raise Error('Unable to push the image to the registry: "%s"'
                  % error_detail)


class Registry(object):
  """Docker Registry."""

  def __init__(self, options):
    """Initializer for Registry.

    Args:
      options: RegistryOptions.
    """
    # If the registry property is set, then use our hosted registry.
    if properties.VALUES.app.hosted_registry.GetBool():
      self._registry = _GoogleContainerRegistry(options,
                                                const_lib.DEFAULT_REGISTRY)
    else:
      self._registry = _LocalRegistry(options)

  def Start(self):
    """Starts Registry container."""
    self._registry.Start()

  def Stop(self):
    """Stops Registry container and removes it."""
    self._registry.Stop()

  def _GetRepoImageTag(self, image_tag):
    return self._registry.GetRepoImageTag(image_tag)

  @property
  def docker_client(self):
    return self._registry.docker_client

  def Push(self, image):
    """Calls "docker push" command.

    Args:
      image: containers.Image, An image to push into GCS bucket.
    """
    repo_image_tag = self._GetRepoImageTag(image.tag)
    self.docker_client.tag(image.id, repo_image_tag, force=True)

    log.err.write('Pushing image to Google Cloud Storage...\n')

    def InnerPush():
      return self.docker_client.push(repo_image_tag,
                                     stream=True,
                                     insecure_registry=True)

    _Retry(ProgressHandler, 'push', InnerPush)

  def _WaitForImageReady(self, image_name):
    """Waits until image with image_name can be found."""
    image = containers.PrebuiltImage(
        self.docker_client,
        containers.ImageOptions(dockerfile_dir=None, tag=image_name))
    # If image with the given name is not found containers.ImageError is raised.
    _Retry(image.Build)

  def Pull(self, image, version):
    """Calls "docker pull" command.

    Args:
      image: str, Tag of an image to pull from GCS bucket. Docker images are
          tagged as 'REPOSITORY_NAME:TAG'. This is repository part, also
          referred to as just image or image name.
      version: str, Version of an image to pull. Also referred to as tag.
    """
    log.info('Pulling image %s:%s from Google Cloud Storage...', image, version)
    repo_image_tag = self._GetRepoImageTag(image)
    def InnerPull():
      return self.docker_client.pull(repo_image_tag,
                                     stream=True,
                                     tag=version,
                                     insecure_registry=True)

    _Retry(ProgressHandler, 'pull', InnerPull)

    # Guarantee that download of the repo_image_tag has finished to safely
    # retag the image.
    self._WaitForImageReady(repo_image_tag)
    self.docker_client.tag(repo_image_tag, repository=image, tag=version)

    # Guarantee that retag is completed before removing the image
    # to safely untag the image with registry address in the name.
    self._WaitForImageReady(image)

    # Untag the images with registry address in the name. We need to
    # find all RepoTags for pulled images. Even if we pull only latest version,
    # all image tags pointing to the same image are pulled (so we'll have
    # "image:latest", "image:1915c" etc).
    # len(images) should be 1, but we might have some garbage from the previous
    # runs in case of improper cleanup, let's clean it here too instead of
    # raising an error.
    images = self.docker_client.images(repo_image_tag, all=True)
    for i in images:
      for repo_tag in i['RepoTags']:
        self.docker_client.remove_image(repo_tag)

  def __enter__(self):
    """Makes Registry usable with "with" statement."""
    self.Start()
    return self

  # pylint: disable=redefined-builtin
  def __exit__(self, type, value, traceback):
    """Makes Registry usable with "with" statement."""
    self.Stop()

  def __del__(self):
    self.Stop()
