
node('master'){
	//Vodoo string manipulation:
	//replaces environmental variables defined in pod_template.json with their binding
	sh 'perl -p -e \'s/\\$\\{([^}]+)\\}/defined $ENV{$1} ? $ENV{$1} : $&/eg; s/\\$\\{([^}]+)\\}//eg\' pod_template.json | kubectl create -f -'
}

node(env.BUILD_TAG) {
	sh "gcloud config set project civil-authority-768"
	sh "gcloud auth login"
	sh "gcloud preview app deploy ."
}
