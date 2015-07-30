Copyright (C) 2014 Google Inc.

# Sample 'hello world' application for use with the App Engine Python Managed VMs.

[![Build Status](https://travis-ci.org/GoogleCloudPlatform/appengine-python-vm-hello.svg?branch=master)](https://travis-ci.org/GoogleCloudPlatform/appengine-python-vm-hello)

A simple Python VM Runtime 'hello world' example, which accesses the 'Users' service, and shows how to get information about the current instance.

You can run this application only on the [App Engine Managed VMs][1]. Currently, Managed VMs are in Beta, and as such may be subject to backward-incompatible changes.

## Project Setup

Before you begin working, be sure you've installed the Google Cloud SDK and a local Docker environment as described in [Getting Started](https://cloud.google.com/appengine/docs/managed-vms/getting-started).

## Deploying

First, set your project ID using the `config` command:

	$ gcloud config set project <project_id>

### Deploy Locally

You can [deploy locally](https://cloud.google.com/appengine/docs/managed-vms/sdk#run-local) using the `app run` command:

    $ gcloud preview app run app.yaml

> `app.yaml` is your project's [runtime configuration file](https://cloud.google.com/appengine/docs/python/config/appconfig?hl=en).

The output of this command will present you the URL your app is now running on. Navigate to this URL in your browser and you'll be greeted with the "Hello!" dialog and a few more options.

### Deploy to Production

Next, [deploy to production](https://cloud.google.com/appengine/docs/managed-vms/sdk#deploy) using the `app deploy` command:

	$ gcloud preview app deploy yaml

Congratulations! You've successfully deployed the Hello World app! Go to the URL specified in the output of your command and enjoy your hard work.

## Licensing

* See LICENSE

[1]: https://cloud.google.com/appengine/docs/managed-vms/
