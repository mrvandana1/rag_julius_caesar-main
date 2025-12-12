pipeline {
    agent any 

    environment {
        DOCKERHUB_CRED = 'mrvandana1'
        DOCKERHUB_USER = 'mrvandana1'

        BACKEND_IMAGE  = "${DOCKERHUB_USER}/rag-backend"
        FRONTEND_IMAGE = "${DOCKERHUB_USER}/rag-frontend"

        ANSIBLE_INVENTORY = 'ansible/inventory.ini'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '50'))
        timestamps()
    }

    stages {

        /* ---------------- CHECKOUT ---------------- */
        stage('Checkout') {
            steps {
                echo "...Checking out source code..."
                checkout scm
                echo "Checked out commit ${env.GIT_COMMIT}"
            }
        }

        /* ---------------- DETECT CHANGES ---------------- */
        stage('Detect Changed Services') {
            steps {
                script {

                    env.BACKEND_CHANGED  = "false"
                    env.FRONTEND_CHANGED = "false"

                    def changed = sh(script: "git diff --name-only HEAD~1 HEAD", returnStdout: true).trim()

                    echo "Changed files:\n${changed}"

                    if (changed.contains("backend/")) {
                        env.BACKEND_CHANGED = "true"
                        echo "🟦 Backend changes detected"
                    }

                    if (changed.contains("frontend/")) {
                        env.FRONTEND_CHANGED = "true"
                        echo "🟩 Frontend changes detected"
                    }

                    if (env.BACKEND_CHANGED == "false" && env.FRONTEND_CHANGED == "false") {
                        echo "✨ No changes detected — skipping builds and deploy!"
                    }
                }
            }
        }

        /* ---------------- TESTS ---------------- */
        stage('Run Backend Tests') {
            when { expression { env.BACKEND_CHANGED == "true" } }
            steps {
                dir('backend') {
                    sh '''
                        echo "Running backend tests..."
                        if [ -f pytest.ini ] || [ -d tests ]; then
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install -r requirements.txt
                            pytest -q
                        else
                            echo "No tests found — skipping."
                        fi
                    '''
                }
            }
        }

        /* ---------------- BUILD DOCKER IMAGES ---------------- */
        stage('Build Docker Images (Cached)') {
            when {
                expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" }
            }
            steps {
                script {
                    env.IMAGE_TAG = sh(
                        script: "git rev-parse --short=8 HEAD",
                        returnStdout: true
                    ).trim()
                }

                script {

                    if (env.BACKEND_CHANGED == "true") {
                        echo "🟦 Building backend image..."
                        sh """
                            docker pull ${BACKEND_IMAGE}:latest || true

                            docker build \
                                --cache-from ${BACKEND_IMAGE}:latest \
                                -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
                                -t ${BACKEND_IMAGE}:latest \
                                ./backend
                        """
                    }

                    if (env.FRONTEND_CHANGED == "true") {
                        echo "🟩 Building frontend image..."
                        sh """
                            docker pull ${FRONTEND_IMAGE}:latest || true

                            docker build \
                                --cache-from ${FRONTEND_IMAGE}:latest \
                                -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                                -t ${FRONTEND_IMAGE}:latest \
                                ./frontend
                        """
                    }
                }
            }
        }

        /* ---------------- PUSH IMAGES ---------------- */
        stage('Push to DockerHub') {
            when {
                expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" }
            }
            steps {
                script {

                    withCredentials([usernamePassword(
                        credentialsId: "${DOCKERHUB_CRED}",
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_PASS'
                    )]) {

                        sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'

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

        /* ---------------- DEPLOY USING ANSIBLE ---------------- */
        stage('Deploy via Ansible → Kubernetes') {
            when {
                expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" }
            }
            steps {
                echo "🚀 Deploying to Kubernetes using Ansible..."

                sh """
                    ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/deploy_update_k8s.yml \
                    --extra-vars \\
                    "backend_image=${BACKEND_IMAGE}:${IMAGE_TAG} frontend_image=${FRONTEND_IMAGE}:${IMAGE_TAG}"
                """
            }
        }

        /* ---------------- VERIFY ---------------- */
        stage('Kubernetes Verification') {
            when {
                expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" }
            }
            steps {
                sh """
                    kubectl get deployments -n default
                    kubectl get pods -n default
                """
            }
        }
    }

    /* ---------------- EMAIL NOTIFICATIONS ---------------- */
    post {

        success {
            echo "SUCCESS: Pipeline finished successfully!"

            mail to: 'vandanamohanaraj@gmail.com',
                 subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: """Hey Mohan,

The CI/CD pipeline completed successfully.

Details:
- Job: ${env.JOB_NAME}
- Build: ${env.BUILD_NUMBER}
- Backend Changed: ${env.BACKEND_CHANGED}
- Frontend Changed: ${env.FRONTEND_CHANGED}

Logs:
${env.BUILD_URL}
"""
        }

        failure {
            echo "FAILURE: Pipeline failed!"

            mail to: 'vandanamohanaraj@gmail.com',
                subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """Pipeline failed.

Details:
- Job: ${env.JOB_NAME}
- Build: ${env.BUILD_NUMBER}
- Check logs for details.

Logs:
${env.BUILD_URL}
"""
        }

        always {
            sh 'docker logout || true'
        }
    }
}

////
// pipeline {
//     agent any

//     environment {
//         DOCKERHUB_CRED = 'mrvandana1'     // Jenkins Credentials ID (USERNAME + PASS/TOKEN)
//         DOCKERHUB_USER = 'mrvandana1'            // Your DockerHub username

//         BACKEND_IMAGE  = "${DOCKERHUB_USER}/rag-backend"
//         FRONTEND_IMAGE = "${DOCKERHUB_USER}/rag-frontend"

//         ANSIBLE_INVENTORY = 'ansible/inventory.ini'
//     }

//     options {
//         buildDiscarder(logRotator(numToKeepStr: '50'))
//         timestamps()
//     }

//     stages {

//         /* ---------------- CHECKOUT ---------------- */
//         stage('Checkout') {
//             steps {
//                 echo "...Checking out source code..."
//                 checkout scm
//                 echo "Checked out: ${env.GIT_COMMIT}"
//             }
//         }

//         stage('Run Backend Tests') {
//             steps {
//                 dir('backend') {
//                     sh '''
//                         echo "Running backend tests..."
//                         if [ -f pytest.ini ] || [ -d tests ]; then
//                             python3 -m venv venv
//                             . venv/bin/activate
//                             pip install -r requirements.txt
//                             pytest -q
//                         else
//                             echo "No tests found — skipping."
//                         fi
//                     '''
//                 }
//             }
//         }

//         /* ---------------- BUILD DOCKER IMAGES ---------------- */
//         stage('Build Docker Images (Cached)') {
//             steps {
//                 script {
//                     env.IMAGE_TAG = sh(
//                         script: "git rev-parse --short=8 HEAD",
//                         returnStdout: true
//                     ).trim()
//                 }

//                 sh """
//                     echo "Building backend with cache..."
//                     docker build \
//                         --cache-from ${BACKEND_IMAGE}:latest \
//                         -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
//                         -t ${BACKEND_IMAGE}:latest \
//                         ./backend

//                     echo "Building frontend with cache..."
//                     docker build \
//                         --cache-from ${FRONTEND_IMAGE}:latest \
//                         -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
//                         -t ${FRONTEND_IMAGE}:latest \
//                         ./frontend
//                 """
//             }
//         }

//         /* ---------------- PUSH DOCKER IMAGES ---------------- */
//         stage('Push to DockerHub') {
//             steps {
//                 echo "Logging in & pushing images..."

//                 withCredentials([usernamePassword(
//                     credentialsId: "${DOCKERHUB_CRED}",
//                     usernameVariable: 'DH_USER',
//                     passwordVariable: 'DH_PASS'
//                 )]) {
//                     sh '''
//                         echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin

//                         docker push ${BACKEND_IMAGE}:${IMAGE_TAG}
//                         docker push ${BACKEND_IMAGE}:latest

//                         docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
//                         docker push ${FRONTEND_IMAGE}:latest
//                     '''
//                 }
//             }
//         }

//         /* ---------------- DEPLOY USING ANSIBLE --> K8S ---------------- */
//         stage('Deploy via Ansible → Kubernetes') {
//             steps {
//                 echo "Deploying to Kubernetes using Ansible..."

//                 sh """
//                     ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/deploy_update_k8s.yml \
//                     --extra-vars "backend_image=${BACKEND_IMAGE}:${IMAGE_TAG} frontend_image=${FRONTEND_IMAGE}:${IMAGE_TAG}"
//                 """
//             }
//         }

//         /* ---------------- VERIFY ---------------- */
//         stage('Kubernetes Verification') {
//             steps {
//                 sh '''
//                     echo "Checking Kubernetes deployments & pods..."
//                     kubectl get deployments --all-namespaces
//                     kubectl get pods --all-namespaces
//                 '''
//             }
//         }

//         /* ---------------- CLEANUP ---------------- */
//         // stage('Cleanup Docker Space') {
//         //     steps {
//         //         echo "Cleaning unused Docker layers..."
//         //         sh 'docker system prune -af || true'
//         //     }
//         // }
//     }

//     /* ---------------- EMAIL NOTIFICATION ---------------- */
//     post {
//         success {
//             echo "SUCCESS: Pipeline finished successfully!"

//             mail to: 'vandanamohanaraj@gmail.com',
//                  subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
//                  body: """Hey Mohan,

// YDemn we did it :)

// Details:
// - Job: ${env.JOB_NAME}
// - Build: ${env.BUILD_NUMBER}
// - Backend Image: ${BACKEND_IMAGE}:${IMAGE_TAG}
// - Frontend Image: ${FRONTEND_IMAGE}:${IMAGE_TAG}

// Logs:
// ${env.BUILD_URL}
// """
//         }

//         failure {
//             echo "FAILURE: Pipeline failed!"

//             mail to: 'vandanamohanaraj@gmail.com',
//                 subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
//                 body: """Bro we failed ,

// Your Jenkins pipeline FAILED.

// Details:
// - Job: ${env.JOB_NAME}
// - Build: ${env.BUILD_NUMBER}

// we are cooked bro 💀

// Logs:
// ${env.BUILD_URL}
// """
//         }

//         always {
//             sh 'docker logout || true'
//         }
//     }
// }
