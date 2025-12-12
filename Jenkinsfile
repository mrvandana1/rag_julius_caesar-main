pipeline {
    agent any

    environment {
        BACKEND_IMAGE  = "mrvandana1/rag-backend"
        FRONTEND_IMAGE = "mrvandana1/rag-frontend"
        DOCKER_CREDS   = "mrvandana1"
        ANSIBLE_INVENTORY = "ansible/inventory-k8"
    }

    stages {
        stage("Checkout") {
            steps { checkout scm }
        }

        stage("Detect Changes") {
            steps {
                script {
                    def changedFiles = sh(
                        script: """
                            git diff --name-only HEAD~1 HEAD 2>/dev/null || \
                            git diff --name-only origin/main HEAD 2>/dev/null || true
                        """,
                        returnStdout: true
                    ).trim()

                    echo "Changed files:\n${changedFiles}"

                    env.BACKEND_CHANGED  = changedFiles.contains("backend/")
                    env.FRONTEND_CHANGED = changedFiles.contains("frontend/")
                }
            }
        }

        stage("Prepare Tag") {
            when { expression { env.BACKEND_CHANGED || env.FRONTEND_CHANGED } }
            steps {
                script {
                    env.IMAGE_TAG = sh(script: "git rev-parse --short=8 HEAD", returnStdout: true).trim()
                }
                echo "TAG = ${env.IMAGE_TAG}"
            }
        }

        stage("Build Images Inside Minikube") {
            when { expression { env.BACKEND_CHANGED || env.FRONTEND_CHANGED } }
            steps {
                script {
                    sh "eval \$(minikube docker-env)"

                    if (env.BACKEND_CHANGED == "true") {
                        sh """
                            docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} backend/
                        """
                    }

                    if (env.FRONTEND_CHANGED == "true") {
                        sh """
                            docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} frontend/
                        """
                    }
                }
            }
        }

        stage("Push to DockerHub") {
            when { expression { env.BACKEND_CHANGED || env.FRONTEND_CHANGED } }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDS, usernameVariable: 'USER', passwordVariable: 'PASS')]) {

                        sh """echo "$PASS" | docker login -u "$USER" --password-stdin"""

                        if (env.BACKEND_CHANGED == "true") {
                            sh "docker push ${BACKEND_IMAGE}:${IMAGE_TAG}"
                        }
                        if (env.FRONTEND_CHANGED == "true") {
                            sh "docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                        }
                    }
                }
            }
        }

        stage("Deploy to Kubernetes") {
            steps {
                sh "ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/playbook-k8.yml --extra-vars \"image_tag=${IMAGE_TAG}\""
            }
        }
    }


    post {
        success {
            mail to: 'vandanamohanaraj@gmail.com',
                 subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "Pipeline successful.\nTag: ${env.IMAGE_TAG}\nLogs: ${env.BUILD_URL}"
        }
        failure {
            mail to: 'vandanamohanaraj@gmail.com',
                 subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "Pipeline failed.\nCheck logs: ${env.BUILD_URL}"
        }
    }
}
