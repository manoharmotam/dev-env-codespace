pipeline {

    agent any
    environment {
        AWS_CRED_ID = 'aws-user'
        AWS_REGION = 'us-east-1'
    }
    stages {
        stage ('Create EC2 instance') {
            steps {
                withAWS(credentials: "${AWS_CRED_ID}", region: "${AWS_REGION}") {
                    script {
                        sh '''
                            aws ec2 run-instances \
                            --image-id ami-0c7217cdde317cfec \
                            --instance-type t2.micro \
                            --key-name 'ami2'
                        '''
                    }
                }
            }
        }
    }
}