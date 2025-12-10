

pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "saketh479"
        BACKEND_IMAGE  = "${DOCKERHUB_USER}/rag-backend"
        FRONTEND_IMAGE = "${DOCKERHUB_USER}/rag-frontend"
    }

    triggers {
        githubPush()
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/saketh1122/rag_julius_caesar.git'
            }
        }

        stage('Build Backend Image') {
            steps {
                sh '''
                docker pull alpine:latest
                docker tag alpine:latest ${BACKEND_IMAGE}:latest
                '''
            }
        }


        stage('Build Frontend Image') {
            steps {
                sh '''
                docker pull alpine:latest
                docker tag alpine:latest ${FRONTEND_IMAGE}:latest
                '''
            }
        }


        stage('Push Images to DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                    docker push ${BACKEND_IMAGE}:latest
                    docker push ${FRONTEND_IMAGE}:latest
                    '''
                }
            }
        }

        // stage('Deploy using Ansible') {
        //     steps {
        //         sh '''
        //         cd ansible
        //         ansible-playbook -i inventory.ini deploy_k8s.yml
        //         '''
        //     }
        // }
    }
}