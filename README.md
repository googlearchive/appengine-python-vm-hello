# Python VM Runtime 'hello world' example

A simple Python VM Runtime 'hello world' example, which accesses the 'Users' service, and shows how to get information about the current instance.

## Project Setup, Installation, and Configuration

You can run this application only on the [App Engine VM
Runtime][1]. Currently, the VM Runtime is part of the Early Access Program, and
only the participants are able to run this application.

## Deploying

1. Make sure that you are invited to the VM Runtime Trusted Tester
   Program, and download the custom SDK.
2. Update the `application` value of the `app.yaml` file from
   `your-app-id` to the app-id which is whitelisted for the VM Runtime
   Trusted Tester Program.
3. Run the following command:
   $ $CUSTOM_SDK_DIR/appcfg.py -R update <directory>

## Licensing

* See LICENSE

[1]: https://docs.google.com/document/d/1VH1oVarfKILAF_TfvETtPPE3TFzIuWqsa22PtkRkgJ4
