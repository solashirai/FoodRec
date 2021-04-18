pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                slackSend (channel: "#heals-foodkg-ci", color: '#FFFF00', message: "STARTED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
                sh '''
                rm -rf env
                /usr/local/bin/python3.8 -m venv env
                source env/bin/activate
                pip install -r requirements.txt
                python -m pip install -e .
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                export PYTHONPATH=$PWD
                source env/bin/activate
                python -m pytest tests/
                '''
            }
        }
    }
    post {
        success {
          slackSend (channel: "#heals-foodkg-ci", color: '#00FF00', message: "SUCCESSFUL: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
        }

        failure {
          slackSend (channel: "#heals-foodkg-ci", color: '#FF0000', message: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
        }
    }
}