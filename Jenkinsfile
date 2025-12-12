pipeline {
    agent any

    environment {
        BACKEND_IMAGE = "rag-backend"
        FRONTEND_IMAGE = "rag-frontend"
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
                    env.BACKEND_CHANGED = sh(script: "git diff --name-only HEAD~1 HEAD | grep backend | wc -l", returnStdout: true).trim() != "0"
                    env.FRONTEND_CHANGED = sh(script: "git diff --name-only HEAD~1 HEAD | grep frontend | wc -l", returnStdout: true).trim() != "0"
                }
                echo "Backend changed: ${env.BACKEND_CHANGED}"
                echo "Frontend changed: ${env.FRONTEND_CHANGED}"
            }
        }

        stage("Prepare Tag") {
            when { expression { env.BACKEND_CHANGED || env.FRONTEND_CHANGED } }
            steps {
                script {
                    env.IMAGE_TAG = sh(script: "git rev-parse --short=8 HEAD", returnStdout: true).trim()
                }
                echo "IMAGE_TAG = ${env.IMAGE_TAG}"
            }
        }

        stage("Build Docker Images") {
            when { expression { env.BACKEND_CHANGED || env.FRONTEND_CHANGED } }
            steps {
                script {
                    sh "eval \$(minikube docker-env)"

                    if (env.BACKEND_CHANGED) {
                        sh """
                            docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} -t ${BACKEND_IMAGE}:latest backend/
                        """
                    }

                    if (env.FRONTEND_CHANGED) {
                        sh """
                            docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} -t ${FRONTEND_IMAGE}:latest frontend/
                        """
                    }
                }
            }
        }

        stage("Load images into Minikube") {
            when { expression { env.BACKEND_CHANGED || env.FRONTEND_CHANGED } }
            steps {
                script {
                    if (env.BACKEND_CHANGED) {
                        sh """
                            docker save ${BACKEND_IMAGE}:${IMAGE_TAG} -o backend.tar
                            minikube image load backend.tar
                        """
                    }

                    if (env.FRONTEND_CHANGED) {
                        sh """
                            minikube image load ${FRONTEND_IMAGE}:${IMAGE_TAG}
                        """
                    }
                }
            }
        }

        stage("Deploy to K8s") {
            steps {
                sh "ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/playbook-k8.yml"
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Pipeline finished successfully!"
            mail to: 'vandanamohanaraj@gmail.com',
                 subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: """Hey Mohan,

Your CI/CD pipeline completed successfully.

Details:
- Job: ${env.JOB_NAME}
- Build: ${env.BUILD_NUMBER}
- Backend Changed: ${env.BACKEND_CHANGED}
- Frontend Changed: ${env.FRONTEND_CHANGED}
- IMAGE_TAG: ${env.IMAGE_TAG}

Logs:
${env.BUILD_URL}
"""
        }

        failure {
            echo "FAILURE: Pipeline failed!"
            mail to: 'vandanamohanaraj@gmail.com',
                 subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: """Pipeline failed.

Check logs for more details:
${env.BUILD_URL}
"""
        }

        always {
            sh 'docker logout || true'
        }
    }
}



// pipeline {
//     agent any 

//     environment {
//         DOCKERHUB_CRED = 'mrvandana1'
//         DOCKERHUB_USER = 'mrvandana1'

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
//                 echo "Checked out commit ${env.GIT_COMMIT}"
//             }
//         }

//         /* ---------------- DETECT CHANGES ---------------- */
//         stage('Detect Changed Services') {
//             steps {
//                 script {

//                     env.BACKEND_CHANGED  = "false"
//                     env.FRONTEND_CHANGED = "false"

//                     def changed = sh(script: "git diff --name-only HEAD~1 HEAD", returnStdout: true).trim()

//                     echo "Changed files:\n${changed}"

//                     if (changed.contains("backend/")) {
//                         env.BACKEND_CHANGED = "true"
//                         echo "🟦 Backend changes detected"
//                     }

//                     if (changed.contains("frontend/")) {
//                         env.FRONTEND_CHANGED = "true"
//                         echo "🟩 Frontend changes detected"
//                     }

//                     if (env.BACKEND_CHANGED == "false" && env.FRONTEND_CHANGED == "false") {
//                         echo "✨ No changes detected — skipping builds and deploy!"
//                     }
//                 }
//             }
//         }

//         /* ---------------- TESTS ---------------- */
//         stage('Run Backend Tests') {
//             when { expression { env.BACKEND_CHANGED == "true" } }
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
//             when {
//                 expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" }
//             }
//             steps {
//                 script {
//                     env.IMAGE_TAG = sh(
//                         script: "git rev-parse --short=8 HEAD",
//                         returnStdout: true
//                     ).trim()
//                 }

//                 script {

//                     if (env.BACKEND_CHANGED == "true") {
//                         echo "🟦 Building backend image..."
//                         sh """
//                             docker pull ${BACKEND_IMAGE}:latest || true

//                             docker build \
//                                 --cache-from ${BACKEND_IMAGE}:latest \
//                                 -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
//                                 -t ${BACKEND_IMAGE}:latest \
//                                 ./backend
//                         """
//                     }

//                     if (env.FRONTEND_CHANGED == "true") {
//                         echo "🟩 Building frontend image..."
//                         sh """
//                             docker pull ${FRONTEND_IMAGE}:latest || true

//                             docker build \
//                                 --cache-from ${FRONTEND_IMAGE}:latest \
//                                 -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
//                                 -t ${FRONTEND_IMAGE}:latest \
//                                 ./frontend
//                         """
//                     }
//                 }
//             }
//         }

//         /* ---------------- PUSH IMAGES ---------------- */
//         stage('Push to DockerHub') {
//             when {
//                 expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" }
//             }
//             steps {
//                 script {

//                     withCredentials([usernamePassword(
//                         credentialsId: "${DOCKERHUB_CRED}",
//                         usernameVariable: 'DH_USER',
//                         passwordVariable: 'DH_PASS'
//                     )]) {

//                         sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'

//                         if (env.BACKEND_CHANGED == "true") {
//                             sh """
//                                 docker push ${BACKEND_IMAGE}:${IMAGE_TAG}
//                                 docker push ${BACKEND_IMAGE}:latest
//                             """
//                         }

//                         if (env.FRONTEND_CHANGED == "true") {
//                             sh """
//                                 docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
//                                 docker push ${FRONTEND_IMAGE}:latest
//                             """
//                         }
//                     }
//                 }
//             }
//         }

//         /* ---------------- DEPLOY USING ANSIBLE ---------------- */
//         /* ---------------- DEPLOY USING ANSIBLE ---------------- */
//         stage('Deploy via Ansible → Kubernetes') {
//             when {
//                 expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" }
//             }
//             steps {
//                 echo "🚀 Deploying to Kubernetes using Ansible (roles-based)..."

//                 script {
//                     // Build dynamic vars
//                     def backend_var = (env.BACKEND_CHANGED == "true") 
//                         ? "backend_image=${BACKEND_IMAGE}:${IMAGE_TAG}" 
//                         : "backend_image=none"

//                     def frontend_var = (env.FRONTEND_CHANGED == "true") 
//                         ? "frontend_image=${FRONTEND_IMAGE}:${IMAGE_TAG}" 
//                         : "frontend_image=none"

//                     // Run Ansible
//                     sh """
//                         ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/site.yml \
//                         --extra-vars "${backend_var} ${frontend_var}"
//                     """
//                 }
//             }
//         }



//         /* ---------------- VERIFY ---------------- */
//         stage('Kubernetes Verification') {
//             when {
//                 expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" }
//             }
//             steps {
//                 sh """
//                     kubectl get deployments -n default
//                     kubectl get pods -n default
//                 """
//             }
//         }
//     }

//     /* ---------------- EMAIL NOTIFICATIONS ---------------- */
//     post {

//         success {
//             echo "SUCCESS: Pipeline finished successfully!"

//             mail to: 'vandanamohanaraj@gmail.com',
//                  subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
//                  body: """Hey Mohan,

// The CI/CD pipeline completed successfully.

// Details:
// - Job: ${env.JOB_NAME}
// - Build: ${env.BUILD_NUMBER}
// - Backend Changed: ${env.BACKEND_CHANGED}
// - Frontend Changed: ${env.FRONTEND_CHANGED}

// Logs:
// ${env.BUILD_URL}
// """
//         }

//         failure {
//             echo "FAILURE: Pipeline failed!"

//             mail to: 'vandanamohanaraj@gmail.com',
//                 subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
//                 body: """Pipeline failed.

// Details:
// - Job: ${env.JOB_NAME}
// - Build: ${env.BUILD_NUMBER}
// - Check logs for details.

// Logs:
// ${env.BUILD_URL}
// """
//         }

//         always {
//             sh 'docker logout || true'
//         }
//     }
// }

