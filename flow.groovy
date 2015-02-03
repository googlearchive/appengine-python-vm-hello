
node('master'){
	//Vodoo string manipulation:
	//replaces environmental variables defined in pod_template.json with their binding
	//probably better to write a workflow tool for this
	sh 'perl -p -e \'s/\\$\\{([^}]+)\\}/defined $ENV{$1} ? $ENV{$1} : $&/eg; s/\\$\\{([^}]+)\\}//eg\' $WORKSPACE/pod_template.json | $JENKINS_HOME/kubectl create -f -'
}

node(env.BUILD_TAG) {
	sh "gcloud config set project civil-authority-768"
	sh "gcloud auth login"
	sh "gcloud preview app deploy ."
}
