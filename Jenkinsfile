pipeline {
    agent any

    environment {
        DOCKERHUB_CRED = 'mrvandana1'             // Jenkins Credentials ID
        DOCKERHUB_USER = 'mrvandana1'                    // Your DockerHub username

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
                            echo "No tests found. Skipping..."
                        fi
                    '''
                }
            }
        }

        /* ---------------- BUILD DOCKER IMAGES ---------------- */
        stage('Build Docker Images') {
            steps {
                script {
                    env.IMAGE_TAG = sh(
                        script: "git rev-parse --short=8 HEAD",
                        returnStdout: true
                    ).trim()
                }

                echo "Using tag: ${IMAGE_TAG}"

                sh """
                    echo "Building backend image..."
                    docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} ./backend
                    docker tag ${BACKEND_IMAGE}:${IMAGE_TAG} ${BACKEND_IMAGE}:latest

                    echo "Building frontend image..."
                    docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} ./frontend
                    docker tag ${FRONTEND_IMAGE}:${IMAGE_TAG} ${FRONTEND_IMAGE}:latest
                """
            }
        }

        /* ---------------- PUSH DOCKER IMAGES ---------------- */
        stage('Push to DockerHub') {
            steps {
                echo "Logging into DockerHub and pushing both images..."

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

        /* ---------------- DEPLOY USING ANSIBLE ---------------- */
        stage('Deploy via Ansible → Kubernetes') {
            steps {
                echo "Deploying new images via Ansible..."

                sh """
                    ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/deploy_update_k8s.yml \
                    --extra-vars "backend_image=${BACKEND_IMAGE}:${IMAGE_TAG} frontend_image=${FRONTEND_IMAGE}:${IMAGE_TAG}"
                """
            }
        }

        /* ---------------- VERIFY KUBERNETES ---------------- */
        stage('Kubernetes Verification') {
            steps {
                sh '''
                    echo "Fetching Kubernetes status..."
                    kubectl get deployments --all-namespaces
                    kubectl get pods --all-namespaces
                '''
            }
        }

        /* ---------------- CLEANUP ---------------- */
        stage('Cleanup Docker Space') {
            steps {
                echo "Cleaning Docker unused resources..."
                sh 'docker system prune -af || true'
            }
        }
    }

    /* ---------------- EMAIL NOTIFICATION ---------------- */
    post {
        success {
            echo "SUCCESS: Pipeline finished successfully!"

            mail to: 'vandanamohanaraj@gmail.com',
                 subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: """Hey Mohan,

Your Jenkins pipeline completed successfully 😎

Details:
- Job: ${env.JOB_NAME}
- Build number: ${env.BUILD_NUMBER}
- Backend Image: ${BACKEND_IMAGE}:${IMAGE_TAG}
- Frontend Image: ${FRONTEND_IMAGE}:${IMAGE_TAG}

Logs:
${env.BUILD_URL}
"""
        }

        failure {
            echo "FAILURE: Pipeline failed."

            mail to: 'vandanamohanaraj@gmail.com',
                subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """Bro Mohan 😭,

Your Jenkins pipeline FAILED.

Details:
- Job: ${env.JOB_NAME}
- Build number: ${env.BUILD_NUMBER}

Fix fast and rerun 💀  

Logs:
${env.BUILD_URL}
"""
        }

        always {
            sh 'docker logout || true'
        }
    }
}
