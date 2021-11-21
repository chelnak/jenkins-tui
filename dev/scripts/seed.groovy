def createPipelineJob(name) {
    // A method that createse a basic pipeline job
    pipelineJob(name) {
        definition {
            cps {
                script('''
                    pipeline {
                        agent any
                        environment {
                            random_num = "${Math.abs(new Random().nextInt(20+1))}"
                        }
                        stages {
                            stage("Stage 1") {
                                steps {
                                    echo "Pipline has started."
                                    sleep(time:env.random_num,unit:"SECONDS")
                                }
                            }
                            stage("Stage 2") {
                                steps {
                                    echo "Pipline has finished."
                                }
                            }
                        }
                    }'''.stripIndent()
                )
                sandbox()
            }
        }
    }
}

def createFreestyleJob(name) {
    // A method that createse a basic freestyle job
    freeStyleJob(name) {
        description("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")
        steps{
            shell('''
                echo "Freestyle job has started."
                sleep $[ ( $RANDOM % 20 )  + 1 ]s
            '''.stripIndent()
            )
        }
    }
}

def createMultibranchPipelineJob(name, sourceId ,owner, repositoryName) {
    // A method that creates a basic multibranch pipeline job
    multibranchPipelineJob(name) {
        branchSources {
            github {
                id(sourceId)
                repoOwner(owner)
                repository(repositoryName)
            }
        }
    }
}

// Pipeline jobs

pipelineJobFolderName = "pipeline-jobs"

folder(pipelineJobFolderName) {
    displayName('Pipeline Jobs')
    description('A folder that contains pipeline jobs.')
}

pipelineJobs = ['pipeline-a-new-pipeline','pipeline-the-pipeline-strikes-back','pipeline-return-of-the-pipeline']

pipelineJobs.each{ job ->
    println "Creating pipeline ${pipelineJobFolderName}/${job}"
    createPipelineJob("${pipelineJobFolderName}/${job}")
}

// Freestyle jobs

freestyleJobFolderName = "freestyle-jobs"

folder(freestyleJobFolderName) {
    displayName('Freestyle Jobs')
    description('A folder that contains freestyle jobs.')
}

freestyleJobs = ['freestyle-the-next-generation','freestyle-deep-space-nine','freestyle-enterprise']

freestyleJobs.each{ job ->
    println "Creating freestyle ${freestyleJobFolderName}/${job}"
    createFreestyleJob("${freestyleJobFolderName}/${job}")
}

// Multibranch Pipeline jobs

multibranchPipelineJobFolderName = "multibranch-pipeline-jobs"

folder(multibranchPipelineJobFolderName) {
    displayName('Multibranch Pipeline Jobs')
    description('A folder that contains multibranch pipeline jobs.')
}

multibranchPipelineJobs = [
    [
        id: "1",
        owner: "jenkinsci",
        repository: "job-dsl-plugin"
    ]
]

multibranchPipelineJobs.each{ job ->
    println "Creating multibranch pipeline ${multibranchPipelineJobFolderName}/${job.repository}"
    createMultibranchPipelineJob("${multibranchPipelineJobFolderName}/${job.repository}", job.id, job.owner, job.repository)
}
