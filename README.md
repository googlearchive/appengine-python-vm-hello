Copyright (C) 2014 Google Inc.

# Sample 'hello world' application for use with the App Engine Python VM Runtime.

A simple Python VM Runtime 'hello world' example, which accesses the 'Users' service, and shows how to get information about the current instance.

## Project Setup, Installation, and Configuration

You can run this application only on the [App Engine VM
Runtime][1]. Currently, the VM Runtime is part of the Early Access Program, and
only the participants are able to run this application.

## Deploying

1. Make sure that you are invited to the VM Runtime Trusted Tester
   Program, and [download the SDK](http://commondatastorage.googleapis.com/gae-vm-runtime-tt/vmruntime_sdks.html).
2. Update the `application` value of the `app.yaml` file from
   `your-app-id` to the app-id which is whitelisted for the VM Runtime
   Trusted Tester Program.
3. Run the `appcfg.py` script from the VM Runtime SDK as follows:

        $ $SDK_DIR/appcfg.py -R -s preview.appengine.google.com update <directory>

4. Visit `http://your-app-id.appspot.com/`.

## Licensing

* See LICENSE

[1]: https://docs.google.com/document/d/1VH1oVarfKILAF_TfvETtPPE3TFzIuWqsa22PtkRkgJ4
