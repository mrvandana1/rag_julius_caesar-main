pipeline {
    agent any

    environment {
        DOCKERHUB_CRED = 'mrvandana1'     // Jenkins Credentials ID (USERNAME + PASS/TOKEN)
        DOCKERHUB_USER = 'mrvandana1'            // Your DockerHub username

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
                echo "Checked out: ${env.GIT_COMMIT}"
            }
        }

        /* ---------------- WARM DOCKER CACHE ---------------- */
        stage('Warm Docker Cache') {
            steps {
                sh """
                    echo "Pulling previous images for cache..."
                    docker pull ${BACKEND_IMAGE}:latest || true
                    docker pull ${FRONTEND_IMAGE}:latest || true
                """
            }
        }

        /* ---------------- TESTS ---------------- */
        stage('Run Backend Tests') {
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
            steps {
                script {
                    env.IMAGE_TAG = sh(
                        script: "git rev-parse --short=8 HEAD",
                        returnStdout: true
                    ).trim()
                }

                sh """
                    echo "Building backend with cache..."
                    docker build \
                        --cache-from ${BACKEND_IMAGE}:latest \
                        -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
                        -t ${BACKEND_IMAGE}:latest \
                        ./backend

                    echo "Building frontend with cache..."
                    docker build \
                        --cache-from ${FRONTEND_IMAGE}:latest \
                        -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                        -t ${FRONTEND_IMAGE}:latest \
                        ./frontend
                """
            }
        }

        /* ---------------- PUSH DOCKER IMAGES ---------------- */
        stage('Push to DockerHub') {
            steps {
                echo "Logging in & pushing images..."

                withCredentials([usernamePassword(
                    credentialsId: "${DOCKERHUB_CRED}",
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_PASS'
                )]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin

                        docker push ${BACKEND_IMAGE}:${IMAGE_TAG}
                        docker push ${BACKEND_IMAGE}:latest

                        docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
                        docker push ${FRONTEND_IMAGE}:latest
                    '''
                }
            }
        }

        /* ---------------- DEPLOY USING ANSIBLE --> K8S ---------------- */
        stage('Deploy via Ansible → Kubernetes') {
            steps {
                echo "Deploying to Kubernetes using Ansible..."

                sh """
                    ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/deploy_update_k8s.yml \
                    --extra-vars "backend_image=${BACKEND_IMAGE}:${IMAGE_TAG} frontend_image=${FRONTEND_IMAGE}:${IMAGE_TAG}"
                """
            }
        }

        /* ---------------- VERIFY ---------------- */
        stage('Kubernetes Verification') {
            steps {
                sh '''
                    echo "Checking Kubernetes deployments & pods..."
                    kubectl get deployments --all-namespaces
                    kubectl get pods --all-namespaces
                '''
            }
        }

        /* ---------------- CLEANUP ---------------- */
        // stage('Cleanup Docker Space') {
        //     steps {
        //         echo "Cleaning unused Docker layers..."
        //         sh 'docker system prune -af || true'
        //     }
        // }
    }

    /* ---------------- EMAIL NOTIFICATION ---------------- */
    post {
        success {
            echo "SUCCESS: Pipeline finished successfully!"

            mail to: 'vandanamohanaraj@gmail.com',
                 subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: """Hey Mohan,

YDemn we did it :)

Details:
- Job: ${env.JOB_NAME}
- Build: ${env.BUILD_NUMBER}
- Backend Image: ${BACKEND_IMAGE}:${IMAGE_TAG}
- Frontend Image: ${FRONTEND_IMAGE}:${IMAGE_TAG}

Logs:
${env.BUILD_URL}
"""
        }

        failure {
            echo "FAILURE: Pipeline failed!"

            mail to: 'vandanamohanaraj@gmail.com',
                subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """Bro we failed ,

Your Jenkins pipeline FAILED.

Details:
- Job: ${env.JOB_NAME}
- Build: ${env.BUILD_NUMBER}

we are cooked bro 💀

Logs:
${env.BUILD_URL}
"""
        }

        always {
            sh 'docker logout || true'
        }
    }
}
