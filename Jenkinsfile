pipeline {
    agent any

    environment {
        // DockerHub repo names
        BACKEND_IMAGE  = "mrvandana1/rag-backend"
        FRONTEND_IMAGE = "mrvandana1/rag-frontend"

        // Jenkins credentials ID for DockerHub login
        DOCKER_CREDS = "mrvandana1"

        // Ansible inventory file
        ANSIBLE_INVENTORY = "ansible/inventory-k8"
    }

    stages {

        stage("Checkout") {
            steps {
                checkout scm
            }
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

                    echo "Changed files:\n${changedFiles ?: 'No changed files detected'}"

                    env.BACKEND_CHANGED  = changedFiles.contains("backend/")
                    env.FRONTEND_CHANGED = changedFiles.contains("frontend/")

                    echo "---- CHANGE SUMMARY ----"
                    echo env.BACKEND_CHANGED  == "true" ? "[✔] Backend changed"  : "[ ] Backend unchanged"
                    echo env.FRONTEND_CHANGED == "true" ? "[✔] Frontend changed" : "[ ] Frontend unchanged"
                    echo "------------------------"
                }
            }
        }

        stage("Prepare Tag") {
            when { expression { env.BACKEND_CHANGED || env.FRONTEND_CHANGED } }
            steps {
                script {
                    env.IMAGE_TAG = sh(script: "git rev-parse --short=8 HEAD", returnStdout: true).trim()
                }
                echo "Using Tag: ${env.IMAGE_TAG}"
            }
        }

        stage("Build Docker Images") {
            when { expression { env.BACKEND_CHANGED || env.FRONTEND_CHANGED } }
            steps {
                script {
                    if (env.BACKEND_CHANGED == "true") {
                        sh """
                            docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} -t ${BACKEND_IMAGE}:latest backend/
                        """
                    }
                    if (env.FRONTEND_CHANGED == "true") {
                        sh """
                            docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} -t ${FRONTEND_IMAGE}:latest frontend/
                        """
                    }
                }
            }
        }

        stage("Push Images to DockerHub") {
            when { expression { env.BACKEND_CHANGED || env.FRONTEND_CHANGED } }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDS, usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        sh """echo "$PASS" | docker login -u "$USER" --password-stdin"""

                        if (env.BACKEND_CHANGED == "true") {
                            sh """
                                docker push ${BACKEND_IMAGE}:${IMAGE_TAG}
                                docker push ${BACKEND_IMAGE}:latest
                            """
                        }

                        if (env.FRONTEND_CHANGED == "true") {
                            sh """
                                docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
                                docker push ${FRONTEND_IMAGE}:latest
                            """
                        }
                    }
                }
            }
        }

        stage("Deploy to K8s") {
            when { expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" } }
            steps {
                sh "ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/playbook-k8.yml"
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
