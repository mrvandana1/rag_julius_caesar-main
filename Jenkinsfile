pipeline {
    //commebt to trigger build
    agent any

    environment {
        DOCKERHUB_USER = 'saketh479'
        DOCKERHUB_PASS = 'Saketh22#@'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/saketh1122/rag_julius_caesar.git'
            }
        }

        stage('Install Dependencies & Test') {
            steps {
                sh 'pip install -r backend/requirements.txt'
                sh 'pytest || true'
            }
        }

        stage('Build Docker Images') {
            steps {
                sh 'docker build -t ${DOCKERHUB_USER}/jc-backend:latest backend/'
                sh 'docker build -t ${DOCKERHUB_USER}/jc-frontend:latest frontend/'
            }
        }

        stage('Login to Docker Hub') {
            steps {
                sh "echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin"
            }
        }

        stage('Push Images') {
            steps {
                sh 'docker push ${DOCKERHUB_USER}/jc-backend:latest'
                sh 'docker push ${DOCKERHUB_USER}/jc-frontend:latest'
            }
        }
    }
}
