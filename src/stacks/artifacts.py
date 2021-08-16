from aws_cdk import core as cdk

from src.helpers.name import NameHelper
from src.helpers.context import ContextHelper
from src.constructs.ecr import ECRConstruct
from src.constructs.codebuild import (
    BuildImageCodeBuildProject,
    DeployCodeBuildProject,
)
from src.constructs.github import GithubConstruct
from src.constructs.bootstrap import BootstrapConstruct


class ArtifactsStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, context: ContextHelper, **kwargs) -> None:
        stack_name = NameHelper.to_pascal_case(name="artifacts-resources")
        super().__init__(
            scope=scope,
            id=stack_name,
            stack_name=stack_name,
            tags=context.app_tags,
            termination_protection=context.app_termination_protection,
            **kwargs,
        )

        orders_backend_repo = ECRConstruct(
            scope=self,
            construct_id="orders-backend",
            termination_protection=context.app_termination_protection,
        )

        build_image_codebuild = BuildImageCodeBuildProject(
            scope=self,
            ecr_repositories=[
                orders_backend_repo,
            ],
            termination_protection=context.app_termination_protection,
        )

        current_stack = cdk.Stack.of(self)

        deploy_backend_codebuild = DeployCodeBuildProject(
            scope=self,
            ecr_repository=orders_backend_repo,
            deploy_accounts=[current_stack.account],
            action="deploy",
        )

        destroy_backend_codebuild = DeployCodeBuildProject(
            scope=self,
            ecr_repository=orders_backend_repo,
            deploy_accounts=[current_stack.account],
            action="destroy",
        )

        github_resources = GithubConstruct(
            scope=self,
            codebuild_arns=[
                build_image_codebuild.project_arn,
                deploy_backend_codebuild.project_arn,
                destroy_backend_codebuild.project_arn,
            ],
            codebuild_logs=[
                build_image_codebuild.log_group_arn,
                deploy_backend_codebuild.log_group_arn,
                destroy_backend_codebuild.log_group_arn,
            ],
            codebuild_sources_arns=[build_image_codebuild.source_bucket_arn],
            images_ssm_parameters_arns=[
                deploy_backend_codebuild.image_ssm_arn,
                destroy_backend_codebuild.image_ssm_arn,
            ],
        )

        build_image_codebuild.add_bucket_policy(principals=[github_resources.codebuild_user_arn])

        BootstrapConstruct(
            self,
            construct_id="bootstrap",
            codebuild_roles=[
                deploy_backend_codebuild.project_role_arn,
                destroy_backend_codebuild.project_role_arn,
            ],
        )
