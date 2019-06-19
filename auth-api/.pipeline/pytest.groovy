#!/usr/bin/env groovy

// Edit your app's name below
def APP_NAME = 'auth-api'

// You'll need to change this to point to your application component's folder within your repository
def CONTEXT_DIRECTORY = 'auth-api'

// ================================================================================================
// SonarQube Scanner Settings
// ------------------------------------------------------------------------------------------------

// The name of the SonarQube route.  Used to dynamically get the URL for SonarQube.
def SONAR_ROUTE_NAME = 'sonarqube'

// The namespace in which the SonarQube route resides.  Used to dynamically get the URL for SonarQube.
// Leave blank if the pipeline is running in same namespace as the route.
def SONAR_ROUTE_NAMESPACE = '1rdehl-tools'

// The name of your SonarQube project
def SONAR_PROJECT_NAME = 'BC Registries Auth API'

// The project key of your SonarQube project
def SONAR_PROJECT_KEY = 'BCRegistriesAuthAPI'

// The base directory of your project.
// This is relative to the location of the `sonar-runner` directory within your project.
// More accurately this is relative to the Gradle build script(s) that manage the SonarQube Scanning
def SONAR_PROJECT_BASE_DIR = '../auth-api'

// The source code directory you want to scan.
// This is relative to the project base directory.
def SONAR_SOURCES = './'
// ================================================================================================

// define groovy functions
import groovy.json.JsonOutput

// set a status to github pull request
def pullrequestStatus(token, state, targetUrl, context, description, pullRequestUrl) {
  //only set the status for pull request
  if (env.CHANGE_ID) {
    def payload = JsonOutput.toJson([state: state,
        target_url: targetUrl,
        context: context,
        description: description
    ])

    //def encodedReq = URLEncoder.encode(payload, "UTF-8")
    sh("curl -s -H \"Authorization: token ${token}\" -H \"Accept: application/json\" -H \"Content-type: application/json\" -X POST -d \'${payload}\' \"${pullRequestUrl}\"")
  }
}

// Gets the URL associated to a named route.
// If you are attempting to access a route outside the local namespace (the namespace in which this script is running)
// The Jenkins service account from the local namespace will need 'view' access to the remote namespace.
@NonCPS
String getUrlForRoute(String routeName, String projectNameSpace = '') {

  def nameSpaceFlag = ''
  if(projectNameSpace?.trim()) {
    nameSpaceFlag = "-n ${projectNameSpace}"
  }

  def url = sh (
    script: "oc get routes ${nameSpaceFlag} -o wide --no-headers | awk \'/${routeName}/{ print match(\$0,/edge/) ?  \"https://\"\$2 : \"http://\"\$2 }\'",
    returnStdout: true
  ).trim()

  return url
}

@NonCPS
String getSonarQubePwd() {

  sonarQubePwd = sh (
    script: 'oc env dc/sonarqube --list | awk  -F  "=" \'/SONARQUBE_ADMINPW/{print $2}\'',
    returnStdout: true
  ).trim()

  return sonarQubePwd
}

@NonCPS
boolean triggerBuild(String contextDirectory) {
  // Determine if code has changed within the source context directory.
  def changeLogSets = currentBuild.changeSets
  def filesChangeCnt = 0
  for (int i = 0; i < changeLogSets.size(); i++) {
    def entries = changeLogSets[i].items
    for (int j = 0; j < entries.length; j++) {
      def entry = entries[j]
      //echo "${entry.commitId} by ${entry.author} on ${new Date(entry.timestamp)}: ${entry.msg}"
      def files = new ArrayList(entry.affectedFiles)
      for (int k = 0; k < files.size(); k++) {
        def file = files[k]
        def filePath = file.path
        //echo ">> ${file.path}"
        if (filePath.contains(contextDirectory)) {
          filesChangeCnt = 1
          k = files.size()
          j = entries.length
        }
      }
    }
  }

  if ( filesChangeCnt < 1 ) {
    echo('The changes do not require a build.')
    return false
  }
  else {
    echo('The changes require a build.')
    return true
  }
}


// define job properties - keep 10 builds only
properties([[$class: 'BuildDiscarderProperty', strategy: [$class: 'LogRotator', artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: '10']]])

def run_pipeline = true

// build wasn't triggered by changes so check with user
if( !triggerBuild(CONTEXT_DIRECTORY) ) {
  stage('No changes. Run pipeline?') {
      try {
        timeout(time: 1, unit: 'DAYS') {
            input message: "Run pipeline?", id: "1234"//, submitter: 'admin'
        }
      } catch (Exception e) {
        run_pipeline = false;
      }
  }
}

if( run_pipeline ) {

  // create api pod to run verification steps
  def pod_label = "api-pod-${UUID.randomUUID().toString()}"

  // The jenkins-python3nodejs template has been purpose built for supporting SonarQube scanning.
  podTemplate(
    label: pod_label,
    name: 'jenkins-slave-python3',
    serviceAccount: 'jenkins',
    cloud: 'openshift',
    containers: [
      containerTemplate(
        name: 'python37',
        image: 'docker-registry.default.svc:5000/1rdehl-tools/jenkins-slave-python3:latest',
        resourceRequestCpu: '100m',
        resourceLimitCpu: '1000m',
        resourceRequestMemory: '1Gi',
        resourceLimitMemory: '2Gi',
        workingDir: '/tmp',
        command: '',
        //args: '${computer.jnlpmac} ${computer.name}',
        envVars: [
            secretEnvVar(key: 'DATABASE_TEST_URL', secretName: 'apitest-secrets', secretKey: 'DATABASE_TEST_URL'),
            secretEnvVar(key: 'KEYCLOAK_BASE_URL', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_BASE_URL'),
            secretEnvVar(key: 'KEYCLOAK_REALMNAME', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_REALMNAME'),
            secretEnvVar(key: 'KEYCLOAK_ADMIN_CLIENTID', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_ADMIN_CLIENTID'),
            secretEnvVar(key: 'KEYCLOAK_ADMIN_SECRET', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_ADMIN_SECRET'),
            secretEnvVar(key: 'KEYCLOAK_AUTH_AUDIENCE', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_AUTH_AUDIENCE'),
            secretEnvVar(key: 'KEYCLOAK_AUTH_CLIENT_SECRET', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_AUTH_CLIENT_SECRET'),
            secretEnvVar(key: 'GITHUB_TOKEN', secretName: 'apitest-secrets', secretKey: 'GITHUB_TOKEN')
        ]
      )
    ]
  ){
    node(pod_label) {

      stage('Checkout Source') {
        echo "Checking out source code ..."
        checkout scm
      }

      def gitCommitSHA = sh(returnStdout: true, script: 'git rev-parse  HEAD').trim()
      def allPRs = sh(returnStdout: true, script: "origin 'pull/*/head'")
      List result = allPRs.split( '\n' ).findAll { it.contains(gitCommitSHA) && it.contains("refs/pull") }
      if (result.size() ==1 ){
          def str = result[0]
          def prId = str.substring(str.indexOf("pull")+5,str.lastIndexOf("head")-1)
          echo "Pull request id: ${prId}"
      }

      dir('auth-api') {
        sh '''
          #!/bin/bash
          source /opt/app-root/bin/activate
          pip install -r requirements.txt
          pip install -r requirements/dev.txt
        '''
        stage('pylint') {
          echo "pylint checking..."
          try{
            sh '''
              source /opt/app-root/bin/activate
              export PYTHONPATH=./src/
              pylint --rcfile=setup.cfg --load-plugins=pylint_flask --disable=C0301,W0511 src/auth_api --exit-zero --output-format=parseable > pylint.log
            '''
          } catch (Exception e) {
            echo "EXCEPTION: ${e}"
            pullrequestStatus("${env.GITHUB_TOKEN}",
                              "error",
                              "${env.BUILD_URL}" + "pylint/",
                              'continuous-integration/pylint',
                              'Linter(pylint) check succeeded!',
                              'https://api.github.com/repos/pwei1018/devops-platform-workshops-labs/statuses/28005fcaa9ede2d7768c86dfdc1e296e62a6c511')
            currentBuild.result = "FAILURE"

          } finally {
            def pyLint = scanForIssues tool: pyLint(pattern: 'pylint.log')
            publishIssues issues: [pyLint]

            if (currentBuild.result != "FAILURE") {
              pullrequestStatus("${env.GITHUB_TOKEN}",
                                "success",
                                "${env.BUILD_URL}" + "pylint/",
                                'continuous-integration/pylint',
                                'Linter(pylint) check succeeded!',
                                'https://api.github.com/repos/pwei1018/devops-platform-workshops-labs/statuses/28005fcaa9ede2d7768c86dfdc1e296e62a6c511')
            }

          }
        }

        stage('Unit test & Coverage') {
          echo "testing..."
          try{
            sh '''
              source /opt/app-root/bin/activate
              export PYTHONPATH=./src/
              pytest
            '''
          } catch (Exception e) {
            echo "EXCEPTION: ${e}"
            pullrequestStatus("${env.GITHUB_TOKEN}",
                            "error",
                            "${env.BUILD_URL}" + "pytest/",
                            'continuous-integration/pytest',
                            'Unit testes failed!',
                            'https://api.github.com/repos/pwei1018/devops-platform-workshops-labs/statuses/28005fcaa9ede2d7768c86dfdc1e296e62a6c511')
            currentBuild.result = "FAILURE"
          } finally {
            junit 'pytest.xml'

            if (currentBuild.result != "FAILURE") {
              pullrequestStatus("${env.GITHUB_TOKEN}",
                                "success",
                                "${env.BUILD_URL}" + "testReport/",
                                'continuous-integration/pytest',
                                'Unit testes succeeded!',
                                'https://api.github.com/repos/pwei1018/devops-platform-workshops-labs/statuses/28005fcaa9ede2d7768c86dfdc1e296e62a6c511')

            }

            cobertura(
              coberturaReportFile: "coverage.xml",
              onlyStable: false,
              failNoReports: true,
              failUnhealthy: false,
              failUnstable: false,
              autoUpdateHealth: true,
              autoUpdateStability: true,
              zoomCoverageChart: true,
              maxNumberOfBuilds: 0,
              lineCoverageTargets: '80, 80, 80',
              conditionalCoverageTargets: '80, 80, 80',
              classCoverageTargets: '80, 80, 80',
              fileCoverageTargets: '80, 80, 80',
            )

            if (currentBuild.result == 'SUCCESS') {
              pullrequestStatus("${env.GITHUB_TOKEN}",
                    "success",
                    "${env.BUILD_URL}" + "cobertura/",
                    'continuous-integration/coverage',
                    'Coverage succeeded!',
                    'https://api.github.com/repos/pwei1018/devops-platform-workshops-labs/statuses/28005fcaa9ede2d7768c86dfdc1e296e62a6c511')
            } else {
              pullrequestStatus("${env.GITHUB_TOKEN}",
                                  "error",
                                  "${env.BUILD_URL}" + "cobertura/",
                                  'continuous-integration/coverage',
                                  'Coverage failed!',
                                  'https://api.github.com/repos/pwei1018/devops-platform-workshops-labs/statuses/28005fcaa9ede2d7768c86dfdc1e296e62a6c511')
            }

          }
        }
      }

      stage('SonarQube Analysis') {
        echo "Performing static SonarQube code analysis ..."

        SONARQUBE_URL = getUrlForRoute(SONAR_ROUTE_NAME, SONAR_ROUTE_NAMESPACE).trim()
        SONARQUBE_PWD = getSonarQubePwd().trim()
        echo "URL: ${SONARQUBE_URL}"
        echo "PWD: ${SONARQUBE_PWD}"

        try {
          // The `sonar-runner` MUST exist in your project and contain a Gradle environment consisting of:
          // - Gradle wrapper script(s)
          // - A simple `build.gradle` file that includes the SonarQube plug-in.
          //
          // An example can be found here:
          // - https://github.com/BCDevOps/sonarqube
          dir('sonar-runner') {
            // ======================================================================================================
            // Set your SonarQube scanner properties at this level, not at the Gradle Build level.
            // The only thing that should be defined at the Gradle Build level is a minimal set of generic defaults.
            //
            // For more information on available properties visit:
            // - https://docs.sonarqube.org/display/SCAN/Analyzing+with+SonarQube+Scanner+for+Gradle
            // ======================================================================================================
            sh (
              returnStdout: true,
              script: "./gradlew sonarqube --stacktrace --info \
                -Dsonar.verbose=true \
                -Dsonar.host.url=${SONARQUBE_URL} \
                -Dsonar.projectName='${SONAR_PROJECT_NAME}' \
                -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                -Dsonar.projectBaseDir=${SONAR_PROJECT_BASE_DIR} \
                -Dsonar.sources=${SONAR_SOURCES}"
            )
          }
        } catch (Exception e) {
          echo "EXCEPTION: ${e}"
          pullrequestStatus("${env.GITHUB_TOKEN}",
                          "error",
                          "${SONARQUBE_URL}" + "/dashboard?id=" + "${SONAR_PROJECT_KEY}",
                          'continuous-integration/sonarqube',
                          'Sonarqube scan failed!',
                          'https://api.github.com/repos/pwei1018/devops-platform-workshops-labs/statuses/28005fcaa9ede2d7768c86dfdc1e296e62a6c511')
          currentBuild.result = "FAILURE"
        } finally {
          pullrequestStatus("${env.GITHUB_TOKEN}",
                    "success",
                    "${SONARQUBE_URL}" + "/dashboard?id=" + "${SONAR_PROJECT_KEY}",
                    'continuous-integration/sonarqube',
                    'Sonarqube scan succeeded!',
                    'https://api.github.com/repos/pwei1018/devops-platform-workshops-labs/statuses/28005fcaa9ede2d7768c86dfdc1e296e62a6c511')
        }
      }
    }
  }
}

