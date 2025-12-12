pipeline {
  agent any

  environment {
    // configure these in Jenkins credentials or as pipeline/global env
    DOCKERHUB_CRED = 'dockerhub-cred-id'      // Jenkins credential id (username/password)
    DOCKERHUB_USER = 'yourdockerhubuser'      // DockerHub username/org
    BACKEND_IMAGE  = "${env.DOCKERHUB_USER}/rag-backend"
    FRONTEND_IMAGE = "${env.DOCKERHUB_USER}/rag-frontend"
    KUBE_CONTEXT   = 'minikube'               // adjust if needed
    ANSIBLE_INVENTORY = 'ansible/inventory.ini'
  }

  options {
    buildDiscarder(logRotator(numToKeepStr: '50'))
    timestamps()
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
        echo "Checked out: ${env.GIT_COMMIT}"
      }
    }

    stage('Run tests') {
      steps {
        dir('backend') {
          // adjust test command if you use pytest/unittest
          sh '''
            echo "Running backend tests..."
            if [ -f pytest.ini ] || [ -d tests ]; then
              pytest -q || (echo "pytest failed" && exit 1)
            else
              echo "No pytest config or tests folder found — skipping tests"
            fi
          '''
        }
      }
    }

    stage('Build Docker images') {
      steps {
        script {
          // use commit sha for tags
          def tag = sh(script: "git rev-parse --short=8 HEAD", returnStdout: true).trim()
          env.IMAGE_TAG = tag
        }

        // Build backend
        sh """
          echo "Building backend image..."
          docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} ./backend
          docker tag ${BACKEND_IMAGE}:${IMAGE_TAG} ${BACKEND_IMAGE}:latest
        """

        // Build frontend
        sh """
          echo "Building frontend image..."
          docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} ./frontend
          docker tag ${FRONTEND_IMAGE}:${IMAGE_TAG} ${FRONTEND_IMAGE}:latest
        """
      }
    }

    stage('Push images') {
      steps {
        script {
          withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CRED}",
                                            usernameVariable: 'DH_USER',
                                            passwordVariable: 'DH_PASS')]) {
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
    }

    stage('Ansible: update k8s (playbook)') {
      steps {
        // We assume ansible + kubectl are available on Jenkins agent (or run this on controller that has them)
        sh '''
          echo "Running ansible playbook to update k8s manifests and deployments..."
          ansible-playbook -i ${ANSIBLE_INVENTORY} ansible/deploy_update_k8s.yml --extra-vars "backend_image=${BACKEND_IMAGE}:${IMAGE_TAG} frontend_image=${FRONTEND_IMAGE}:${IMAGE_TAG}"
        '''
      }
    }

    stage('Kubernetes: verify') {
      steps {
        sh '''
          echo "K8s status (deployments & pods):"
          kubectl get deployments --all-namespaces || true
          kubectl get pods --all-namespaces || true
        '''
      }
    }
  }

  post {
    success {
      echo "Pipeline finished SUCCESS"
    }
    failure {
      echo "Pipeline FAILED"
    }
    always {
      sh 'docker logout || true'
    }
  }
}
