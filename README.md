Copyright (C) 2014 Google Inc.

# Sample 'hello world' application for use with the App Engine Python Managed VMs.

[![Build Status](https://travis-ci.org/GoogleCloudPlatform/hello-sample-appengine-vm-python.svg?branch=master)](https://travis-ci.org/GoogleCloudPlatform/hello-sample-appengine-vm-python)

A simple Python VM Runtime 'hello world' example, which accesses the 'Users' service, and shows how to get information about the current instance.

You can run this application only on the [App Engine Managed VMs][1]. Currently, Managed VMs are in Beta, and as such may be subject to backward-incompatible changes.

## Project Setup

Create a billing enabled project and install the Google Cloud SDK as described [here](https://cloud.google.com/appengine/docs/python/managed-vms/#install-sdk) (this includes [installing Docker](https://cloud.google.com/appengine/docs/python/managed-vms/#install-docker))

### Installing boot2docker on Linux

First install VirtualBox if you do not already have it:

```
$ sudo apt-get install virtualbox
```

Next download the [latest boot2docker release](https://github.com/boot2docker/boot2docker-cli/releases) and then start the daemon:

```
$ <path_to_download>/boot2docker-<version>-linux-<processor> init
$ <path_to_download>/boot2docker-<version>-linux-<processor> up

```

Then continue with the Docker installation as described above

## Deploying

After successfully setting up your project, you can either [run locally](https://cloud.google.com/appengine/docs/python/managed-vms/sdk#run-local), or [deploy to production](https://cloud.google.com/appengine/docs/python/managed-vms/sdk#deploy)

## Licensing

* See LICENSE

[1]: https://cloud.google.com/appengine/docs/managed-vms/
