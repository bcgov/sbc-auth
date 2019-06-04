// Edit your app's name below
def APP_NAME = 'auth-api'

// Edit your environment TAG names below
def TAG_NAMES = ['latest', 'dev', 'test', 'prod']

// You shouldn't have to edit these if you're following the conventions
def BUILD_CONFIG = APP_NAME

//EDIT LINE BELOW (Change `IMAGESTREAM_NAME` so it matches the name of your *output*/deployable image stream.)
def IMAGESTREAM_NAME = APP_NAME

// You'll need to change this to point to your application component's folder within your repository
def CONTEXT_DIRECTORY = 'auth-api'

// Edit your namespaces names below
def NAMESPACES = ['1rdehl-tools', '1rdehl-dev', '1rdehl-test', '1rdehl-prod']

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

// Get an image's hash tag
String getImageTagHash(String imageName, String tag = "") {

  if(!tag?.trim()) {
    tag = "latest"
  }

  def istag = openshift.raw("get istag ${imageName}:${tag} -o template --template='{{.image.dockerImageReference}}'")
  return istag.out.tokenize('@')[1].trim()
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
        name: 'jnlp',
        image: 'docker-registry.default.svc:5000/1rdehl-tools/jenkins-slave-python3:3.7.3',
        resourceRequestCpu: '1000m',
        resourceLimitCpu: '2000m',
        resourceRequestMemory: '2Gi',
        resourceLimitMemory: '4Gi',
        workingDir: '/tmp',
        command: '',
        args: '${computer.jnlpmac} ${computer.name}',
        envVars: [
            secretEnvVar(key: 'DATABASE_TEST_URL', secretName: 'apitest-secrets', secretKey: 'DATABASE_TEST_URL'),
            secretEnvVar(key: 'KEYCLOAK_BASE_URL', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_BASE_URL'),
            secretEnvVar(key: 'KEYCLOAK_REALMNAME', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_REALMNAME'),
            secretEnvVar(key: 'KEYCLOAK_ADMIN_CLIENTID', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_ADMIN_CLIENTID'),
            secretEnvVar(key: 'KEYCLOAK_ADMIN_SECRET', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_ADMIN_SECRET'),
            secretEnvVar(key: 'KEYCLOAK_AUTH_AUDIENCE', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_AUTH_AUDIENCE'),
            secretEnvVar(key: 'KEYCLOAK_AUTH_CLIENT_SECRET', secretName: 'apitest-secrets', secretKey: 'KEYCLOAK_AUTH_CLIENT_SECRET')
        ]
      )
    ]
  ){
    node(pod_label) {

      stage('Checkout Source') {
        echo "Checking out source code ..."
        checkout scm
      }

      stage('Run pytest') {
        echo "Running pytest ... "
        sh '''
          #!/bin/bash
          echo $DATABASE_TEST_URL
        '''
        dir('auth-api') {
          try {
            sh '''
                python -m venv venv
                source venv/bin/activate
                pip install flake8 pylint pytest coverage
                pip install -r requirements.txt
                pip install -r requirements/dev.txt
                export PYTHONPATH=./src/
                coverage run -m pytest
                python -m coverage xml

            '''
            cobertura coberturaReportFile: 'coverage.xml'
          } catch (Exception e) {
              echo "EXCEPTION: ${e}"
          }
        }
      }
    }
  }
}

