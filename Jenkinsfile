#!/usr/bin/env groovy

pipeline {
  agent any

  options {
    timeout(time: 30, unit: 'MINUTES')
  }

  triggers {
    cron('H 4 * * *')
  }

  stages {
    stage('Build and push CTT server image') {
      steps {
        script {
          dockerImage = docker.build("radonconsortium/radon-ctt:latest", "./ctt-server")
          withDockerRegistry(credentialsId: 'dockerhub-radonconsortium') {
            dockerImage.push("latest")
          }
        }
      }
    }
  }
}
