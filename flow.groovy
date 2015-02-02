
node('master'){
	def slurper = new groovy.json.JsonSlurper()
	def template_file = new File('pod_template.json)
	def pod = slurper.parse(template_file)
	pod.setId(env.BUILD_TAG)	
	kube_create_pod: pod
}

node(env.BUILD_TAG) {
	sh "gcloud config set project civil-authority-768"
	sh "gcloud auth login"
	sh "gcloud preview app deploy ."
}
