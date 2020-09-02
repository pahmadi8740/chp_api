pipeline {
  agent any
  stages {
    stage('connect to newman service') {
      steps {
        sh 'docker exec -it chp-test-suite_newman_1 sh'
      }
    }

  }
}