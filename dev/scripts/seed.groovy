def createPipelineJob(name) {
    pipelineJob(name) {
        definition {
            cps {
                script('''
                    pipeline {
                        agent any
                        stages {
                            stage("Stage 1") {
                                steps {
                                    echo "Pipline ${name} has started."
                                }
                            }
                            stage("Stage 2") {
                                steps {
                                    echo "Pipline ${name} has finished."
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

pipelineJobs = ['pipeline-a-new-pipeline','pipeline-the-pipeline-strikes-back','pipeline-return-of-the-pipeline']

pipelineJobs.each{ job ->
    println "Creating pipeline ${job}"
    createPipelineJob(job)
}
