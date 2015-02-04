
node('master'){
	kube_create("pods", "jenkinsmaster1")
//[
//		"id": env.BUILD_TAG,
//		"kind": "Pod",
//		"apiVersion": "v1beta1",
//		"desiredState": [
//			"manifest": [
//				"version": "v1beta1",
//				"containers": [[
//					"name": "jenkinsslave",
//					"image": "elibixby/jenkins_slave",
//					"volumeMounts": [
//						"name": "docksock",
//						"mountpath": "/var/run"
//					]
//				]],
//				"volumes": [[
//					"name": "docksock",
//					"source": [
//						"hostDir": [
//							"path": "/var/run"
//						]
//					]
//				]]
//			]
//		]
//	]))
}

node(env.BUILD_TAG) {
	sh "gcloud config set project civil-authority-768"
	sh "gcloud auth login"
	sh "gcloud preview app deploy ."
}
