import aws_cdk as cdk
from aws_cdk import (
    Stack,
    pipelines,
    aws_codepipeline_actions as pipeline_actions_,
    aws_codebuild as aws_codebuild_,
    Fn,
)
from constructs import Construct
from nautash_ahmad.nautash_ahmad_pipeline_stage import NautashAhmadPipelineStage

class NautashAhmadPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Creating a source step for pipeline
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.pipelines/CodePipelineSource.html#aws_cdk.pipelines.CodePipelineSource.git_hub
        source = pipelines.CodePipelineSource.git_hub(
            'nautash2022skipq/Sprint-06', 'master',
            authentication=cdk.SecretValue.secrets_manager("NautashAhmadGithubAccessToken"),
            trigger=pipeline_actions_.GitHubTrigger('POLL')
        )
        
        # Creating a build step for pipeline
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.pipelines/ShellStep.html
        synth = pipelines.ShellStep(
            'NautashAhmadPipelineShellStep',
            commands=[
                'npm install -g aws-cdk',
                'pip install -r requirements.txt',
                'cdk synth'
            ],
            primary_output_directory='cdk.out',
            input=source
        )
        
        # Creating a pipeline
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.pipelines/CodePipeline.html
        pipeline = pipelines.CodePipeline(self, "NautashAhmadPipeline", synth=synth)
        
        # Importing the exported variable across different stacks
        # Import: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.core/Fn.html#aws_cdk.core.Fn.import_value
        # Export: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.core/CfnOutput.html
        # Ref: https://lzygo1995.medium.com/how-to-export-and-import-stack-output-values-in-cdk-ff3e066ca6fc
        gateway_url = Fn.import_value('CfnRestApiGatewayUrlVar')
        
        # Adding stages to pipeline
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.core/Stage.html
        staging = NautashAhmadPipelineStage(self, 'Staging')
        production = NautashAhmadPipelineStage(self, 'Production')
        
        # Adding pre and post steps to pipeline stages
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/AddStageOpts.html
        
        # Running test cases
        pipeline.add_stage(staging, pre=[
            pipelines.ShellStep('StagingPipelineRunTestCases', commands=[
                'npm install -g aws-cdk',
                'pip install -r requirements.txt',
                'pip install -r requirements-dev.txt',
                'pytest'
            ])
        ])
        
        # Adding manual approval
        pipeline.add_stage(production, pre=[
            pipelines.ManualApprovalStep('ProductionPipelineManualApproval')
        ])