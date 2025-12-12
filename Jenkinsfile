pipeline {
    agent any

    environment {
        BACKEND_IMAGE  = "mrvandana1/rag-backend"
        FRONTEND_IMAGE = "mrvandana1/rag-frontend"
        DOCKER_CREDS   = "mrvandana1"
        ANSIBLE_INVENTORY = "ansible/inventory-k8"
        KUBECONFIG = "/var/lib/jenkins/.kube/config"
    }


    stages {

        stage("Checkout") {
            steps { checkout scm }
        }

        stage("Detect Changes") {
            steps {
                script {
                    def changed = sh(
                        script: "git diff --name-only HEAD~1 HEAD || true",
                        returnStdout: true
                    ).trim()

                    echo "Changed files:\n${changed}"

                    BACKEND_CHANGED  = changed.contains("backend/")
                    FRONTEND_CHANGED = changed.contains("frontend/")

                    if (!BACKEND_CHANGED && !FRONTEND_CHANGED) {
                        echo "No changes → stopping pipeline"
                        currentBuild.result = "SUCCESS"
                        return
                    }
                }
            }
        }

        // stage("Determine Tags") {
        //     steps {
        //         script {

        //             // Generate new commit-based tag
        //             def commitTag = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()

        //             // BACKEND TAG LOGIC
        //             if (BACKEND_CHANGED) {
        //                 BACKEND_TAG = commitTag
        //             } else {
        //                 BACKEND_TAG = sh(
        //                     script: "kubectl get deployment rag-backend -o=jsonpath='{.spec.template.spec.containers[0].image}' | cut -d: -f2",
        //                     returnStdout: true
        //                 ).trim()
        //             }

        //             // FRONTEND TAG LOGIC
        //             if (FRONTEND_CHANGED) {
        //                 FRONTEND_TAG = commitTag
        //             } else {
        //                 FRONTEND_TAG = sh(
        //                     script: "kubectl get deployment rag-frontend -o=jsonpath='{.spec.template.spec.containers[0].image}' | cut -d: -f2",
        //                     returnStdout: true
        //                 ).trim()
        //             }

        //             echo "BACKEND_TAG:  ${BACKEND_TAG}"
        //             echo "FRONTEND_TAG: ${FRONTEND_TAG}"
        //         }
        //     }
        // }
        stage("Test kubectl") {
            steps {
                sh """
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    kubectl get nodes
                """
            }
        }

        stage("Determine Tags") {
            steps {
                script {

                    echo "==========[ DETERMINE TAGS STAGE STARTED ]=========="

                    // Ensure correct kubeconfig
                    echo "[INFO] Setting KUBECONFIG for Jenkins"
                    sh "export KUBECONFIG=/var/lib/jenkins/.kube/config"

                    // Current commit tag
                    def commitTag = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    echo "[INFO] Current COMMIT TAG = ${commitTag}"

                    // ---- DEBUG PRINT FOR FILE CHANGES ----
                    echo "[INFO] BACKEND_CHANGED  = ${BACKEND_CHANGED}"
                    echo "[INFO] FRONTEND_CHANGED = ${FRONTEND_CHANGED}"

                    // ---- READ CURRENT TAGS FROM K8S ----
                    def currentBackendImage = sh(
                        script: "kubectl get deployment rag-backend -o=jsonpath='{.spec.template.spec.containers[0].image}' || true",
                        returnStdout: true
                    ).trim()

                    def currentFrontendImage = sh(
                        script: "kubectl get deployment rag-frontend -o=jsonpath='{.spec.template.spec.containers[0].image}' || true",
                        returnStdout: true
                    ).trim()

                    echo "[DEBUG] K8s backend image   = ${currentBackendImage}"
                    echo "[DEBUG] K8s frontend image  = ${currentFrontendImage}"

                    // Extract tags safely
                    def currentBackendTag  = currentBackendImage.tokenize(':')[-1]
                    def currentFrontendTag = currentFrontendImage.tokenize(':')[-1]

                    echo "[DEBUG] Extracted backend tag from K8s  = ${currentBackendTag}"
                    echo "[DEBUG] Extracted frontend tag from K8s = ${currentFrontendTag}"

                    // ---- BACKEND TAG DECISION ----
                    if (BACKEND_CHANGED) {
                        BACKEND_TAG = commitTag
                        echo "[TAG-LOGIC] Backend changed → using NEW tag = ${BACKEND_TAG}"
                    } else {
                        BACKEND_TAG = currentBackendTag
                        echo "[TAG-LOGIC] Backend unchanged → using EXISTING tag = ${BACKEND_TAG}"
                    }

                    // ---- FRONTEND TAG DECISION ----
                    if (FRONTEND_CHANGED) {
                        FRONTEND_TAG = commitTag
                        echo "[TAG-LOGIC] Frontend changed → using NEW tag = ${FRONTEND_TAG}"
                    } else {
                        FRONTEND_TAG = currentFrontendTag
                        echo "[TAG-LOGIC] Frontend unchanged → using EXISTING tag = ${FRONTEND_TAG}"
                    }

                    // Final validation
                    if (!BACKEND_TAG) { error "[ERROR] BACKEND_TAG EMPTY" }
                    if (!FRONTEND_TAG) { error "[ERROR] FRONTEND_TAG EMPTY" }

                    echo "==========[ FINAL TAGS TO USE ]=========="
                    echo "✔ BACKEND_TAG  = ${BACKEND_TAG}"
                    echo "✔ FRONTEND_TAG = ${FRONTEND_TAG}"
                    echo "==================================================="
                }
            }
        }

        stage("Build Images") {
            steps {
                script {
                    echo "Building images using normal Docker daemon (not Minikube)"


                    if (BACKEND_CHANGED) {
                        sh """
                            docker build -t ${BACKEND_IMAGE}:${BACKEND_TAG} backend/
                            docker tag ${BACKEND_IMAGE}:${BACKEND_TAG} ${BACKEND_IMAGE}:latest
                        """
                    }

                    if (FRONTEND_CHANGED) {
                        sh """
                            docker build -t ${FRONTEND_IMAGE}:${FRONTEND_TAG} frontend/
                            docker tag ${FRONTEND_IMAGE}:${FRONTEND_TAG} ${FRONTEND_IMAGE}:latest
                        """
                    }
                }
            }
        }

        stage("Push to DockerHub") {
            steps {
                script {
                    withCredentials([
                        usernamePassword(
                            credentialsId: DOCKER_CREDS, 
                            usernameVariable: 'USER', 
                            passwordVariable: 'PASS'
                        )
                    ]) {

                        sh """echo "$PASS" | docker login -u "$USER" --password-stdin"""

                        if (BACKEND_CHANGED) {
                            sh """
                                docker push ${BACKEND_IMAGE}:${BACKEND_TAG}
                                docker push ${BACKEND_IMAGE}:latest
                            """
                        }

                        if (FRONTEND_CHANGED) {
                            sh """
                                docker push ${FRONTEND_IMAGE}:${FRONTEND_TAG}
                                docker push ${FRONTEND_IMAGE}:latest
                            """
                        }
                    }
                }
            }
        }

        stage("Deploy via Ansible") {
            steps {
                sh """
                    ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/playbook-k8.yml \
                    --extra-vars "backend_tag=${BACKEND_TAG} frontend_tag=${FRONTEND_TAG}"
                """
            }
        }
    }

    post {
        success {
            mail to: 'vandanamohanaraj@gmail.com',
                 subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "Pipeline successful.\nBackend tag: ${BACKEND_TAG}\nFrontend tag: ${FRONTEND_TAG}"
        }
        failure {
            mail to: 'vandanamohanaraj@gmail.com',
                 subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "Pipeline failed. Check logs."
        }
    }
}
