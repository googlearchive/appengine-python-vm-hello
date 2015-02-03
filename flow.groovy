
node('master'){
<<<<<<< HEAD
	//Vodoo string manipulation:
	//replaces environmental variables defined in pod_template.json with their binding
	//probably better to write a workflow tool for this
	sh 'perl -p -e \'s/\\$\\{([^}]+)\\}/defined $ENV{$1} ? $ENV{$1} : $&/eg; s/\\$\\{([^}]+)\\}//eg\' $WORKSPACE/pod_template.json | $JENKINS_HOME/kubectl create -f -'
=======
	kube_create: "pods", [
		"id": env.BUILD_TAG,
		"kind": "Pod",
		"apiVersion": "v1beta1",
		"desiredState": [
			"manifest": [
				"version": "v1beta1",
				"containers": [[
					"name": "jenkinsslave",
					"image": "elibixby/jenkins_slave",
					"volumeMounts": [
						"name": "docksock",
						"mountpath": "/var/run"
					]
				]],
				"volumes": [[
					"name": "docksock",
					"source": [
						"hostDir": [
							"path": "/var/run"
						]
					]
				]]
			]
		]
	]
>>>>>>> parent of 63aae58... syntax fix
}

node(env.BUILD_TAG) {
	sh "gcloud config set project civil-authority-768"
	sh "gcloud auth login"
	sh "gcloud preview app deploy ."
}
