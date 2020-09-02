pipeline {
  agent any
  stages {
    stage('connect to newman service') {
      steps {
        sh 'docker exec -it chp-test-suite_web_1 sh'
      }
    }

  }
}