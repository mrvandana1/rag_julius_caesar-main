

pipeline {
    agent any

    // --- CONFIGURE THESE in Jenkins (or keep as env below) ---
    environment {
        DOCKERHUB_CRED = 'mrvandana1'         // Jenkins credential id (username/password)
        DOCKERHUB_USER = 'mrvandana1'
        BACKEND_IMAGE  = "${DOCKERHUB_USER}/rag-backend"
        FRONTEND_IMAGE = "${DOCKERHUB_USER}/rag-frontend"
        ANSIBLE_INVENTORY = 'ansible/inventory.ini'

        // Toggles (you can also turn these into Jenkins boolean parameters)
        // Set MINIKUBE_MODE="true" to build inside minikube's docker daemon
        // Set PUSH_TO_DOCKERHUB="true" to push built images to DockerHub (only used when MINIKUBE_MODE != "true")
        MINIKUBE_MODE = "true"
        PUSH_TO_DOCKERHUB = "false"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '50'))
        timestamps()
        // Add ANSI color, timeout, etc. if desired
    }

    stages {

        stage('Checkout') {
            steps {
                echo "...Checking out source code..."
                checkout scm
                echo "Checked out commit ${env.GIT_COMMIT}"
            }
        }

        stage('Detect Changed Services') {
            steps {
                script {
                    env.BACKEND_CHANGED  = "false"
                    env.FRONTEND_CHANGED = "false"

                    def changed = sh(script: "git diff --name-only HEAD~1 HEAD || true", returnStdout: true).trim()
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

        stage('Prepare Image Tag') {
            when { expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" } }
            steps {
                script {
                    env.IMAGE_TAG = sh(script: "git rev-parse --short=8 HEAD", returnStdout: true).trim()
                    echo "Using IMAGE_TAG = ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Build Docker Images') {
            when { expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" } }
            steps {
                script {
                    if (env.MINIKUBE_MODE == "true") {
                        echo "🔧 MINIKUBE_MODE enabled — building images inside Minikube's Docker daemon"
                        // Connect the shell to Minikube's docker
                        sh "eval \$(minikube -p minikube docker-env)"

                        if (env.BACKEND_CHANGED == "true") {
                            echo "🟦 Building backend inside Minikube..."
                            sh """
                                docker build -t rag-backend:${IMAGE_TAG} -t rag-backend:latest ./backend
                            """
                        }

                        if (env.FRONTEND_CHANGED == "true") {
                            echo "🟩 Building frontend inside Minikube..."
                            sh """
                                docker build -t rag-frontend:${IMAGE_TAG} -t rag-frontend:latest ./frontend
                            """
                        }
                    } else {
                        echo "🌐 Building images for remote registry (DockerHub) flow"
                        if (env.BACKEND_CHANGED == "true") {
                            sh """
                                docker pull ${BACKEND_IMAGE}:latest || true
                                docker build --cache-from ${BACKEND_IMAGE}:latest -t ${BACKEND_IMAGE}:${IMAGE_TAG} -t ${BACKEND_IMAGE}:latest ./backend
                            """
                        }
                        if (env.FRONTEND_CHANGED == "true") {
                            sh """
                                docker pull ${FRONTEND_IMAGE}:latest || true
                                docker build --cache-from ${FRONTEND_IMAGE}:latest -t ${FRONTEND_IMAGE}:${IMAGE_TAG} -t ${FRONTEND_IMAGE}:latest ./frontend
                            """
                        }
                    }
                }
            }
        }

        stage('Push to DockerHub (optional)') {
            when {
                allOf {
                    expression { env.PUSH_TO_DOCKERHUB == "true" }
                    expression { env.MINIKUBE_MODE != "true" } // only meaningful for registry flow
                }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CRED}", usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
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
                        sh 'docker logout || true'
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when { expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" } }
            steps {
                script {
                    echo "🚀 Deploying to Kubernetes..."

                    if (env.MINIKUBE_MODE == "true") {
                        // Using Minikube-local images -> set image to local tags (imagePullPolicy: Never in manifests)
                        if (env.BACKEND_CHANGED == "true") {
                            sh "kubectl set image deployment/rag-backend rag-backend=rag-backend:${IMAGE_TAG} --record"
                        }
                        if (env.FRONTEND_CHANGED == "true") {
                            sh "kubectl set image deployment/rag-frontend rag-frontend=rag-frontend:${IMAGE_TAG} --record"
                        }

                        // Optional: run your Ansible playbook if you want Ansible to apply manifests or do extra steps.
                        // Pass the local image names so ansible tasks are aware.
                        sh """
                            ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/site.yml \\
                                --extra-vars "backend_image=${env.BACKEND_CHANGED == 'true' ? "rag-backend:${IMAGE_TAG}" : 'none'} frontend_image=${env.FRONTEND_CHANGED == 'true' ? "rag-frontend:${IMAGE_TAG}" : 'none'}" || true
                        """
                    } else {
                        // Remote registry flow: use full registry tags pushed to DockerHub
                        if (env.BACKEND_CHANGED == "true") {
                            sh "kubectl set image deployment/rag-backend rag-backend=${BACKEND_IMAGE}:${IMAGE_TAG} --record"
                        }
                        if (env.FRONTEND_CHANGED == "true") {
                            sh "kubectl set image deployment/rag-frontend rag-frontend=${FRONTEND_IMAGE}:${IMAGE_TAG} --record"
                        }

                        // Call Ansible with full registry tags too (Ansible can also apply manifests or other tasks)
                        sh """
                            ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/site.yml \\
                                --extra-vars "backend_image=${env.BACKEND_CHANGED == 'true' ? "${BACKEND_IMAGE}:${IMAGE_TAG}" : 'none'} frontend_image=${env.FRONTEND_CHANGED == 'true' ? "${FRONTEND_IMAGE}:${IMAGE_TAG}" : 'none'}" || true
                        """
                    }
                }
            }
        }

        stage('Kubernetes Verification') {
            when { expression { env.BACKEND_CHANGED == "true" || env.FRONTEND_CHANGED == "true" } }
            steps {
                sh """
                    echo ">>> Deployments:"
                    kubectl get deployments -o wide

                    echo ">>> Pods:"
                    kubectl get pods -o wide

                    echo ">>> Describe recent rollout (backend):"
                    kubectl rollout status deployment/rag-backend --timeout=120s || true

                    echo ">>> Describe recent rollout (frontend):"
                    kubectl rollout status deployment/rag-frontend --timeout=120s || true
                """
            }
        }
    } // stages

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

