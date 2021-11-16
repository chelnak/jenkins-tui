def createPipelineJob(name) {
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

pipelineJobs = ['pipeline-a-new-pipeline','pipeline-the-pipeline-strikes-back','pipeline-return-of-the-pipeline']

pipelineJobs.each{ job ->
    println "Creating pipeline ${job}"
    createPipelineJob(job)
}
