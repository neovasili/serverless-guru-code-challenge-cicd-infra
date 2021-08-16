from aws_cdk import (
    core as cdk,
    aws_iam as iam,
    aws_ssm as ssm,
)
from src.helpers.name import NameHelper


class GithubConstruct(cdk.Construct):
    @property
    def codebuild_user_arn(self):
        return self.codebuild_user.user_arn

    def __init__(
        self,
        scope: cdk.Construct,
        codebuild_arns: list,
        codebuild_logs: list,
        codebuild_sources_arns: list,
        images_ssm_parameters_arns: list,
    ) -> None:
        construct_id = "github"
        super().__init__(scope, id=construct_id)

        codebuild_name = NameHelper.to_pascal_case(name="github-code-build-bot")
        logical_name = "GithubCodeBuildBot"

        self.codebuild_user = iam.User(
            scope=self,
            id=f"{construct_id}-codebuild-user",
            user_name=codebuild_name,
        )

        self.access_keys = iam.CfnAccessKey(
            scope=self,
            id=f"{construct_id}-codebuild-user-keys",
            user_name=self.codebuild_user.user_name,
        )

        self.ssm_access_keys = ssm.StringParameter(
            scope=self,
            id=f"{construct_id}-codebuild-user-ssm-keys",
            parameter_name="/codebuild/github/credentials",
            string_value=str(
                {
                    "access_key_id": self.access_keys.ref,
                    "access_secret_key": self.access_keys.attr_secret_access_key,
                }
            ),
            # type=ssm.ParameterType.SECURE_STRING,  --> CloudFormation does not support secure SSM parameters
        )

        self.user_permissions = iam.Policy(
            scope=self,
            id=f"{construct_id}-user-permissions",
            policy_name=f"{codebuild_name}Policy",
        )

        self.user_permissions.add_statements(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "codebuild:StartBuild",
                    "codebuild:BatchGetBuilds",
                ],
                resources=codebuild_arns,
            ),
        )
        self.user_permissions.add_statements(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:GetLogEvents",
                ],
                resources=codebuild_logs,
            ),
        )
        sources_arns = list()

        for codebuild_source_arn in codebuild_sources_arns:
            sources_arns.append(codebuild_source_arn)
            sources_arns.append(f"{codebuild_source_arn}/*")

        self.user_permissions.add_statements(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:GetObjectVersion",
                    "s3:ListBucket",
                    "s3:ListBucketVersions",
                ],
                resources=sources_arns,
            ),
        )

        if len(images_ssm_parameters_arns) > 0:
            self.user_permissions.add_statements(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "ssm:GetParameter",
                        "ssm:GetParameters",
                    ],
                    resources=images_ssm_parameters_arns,
                ),
            )

        self.user_permissions.attach_to_user(user=self.codebuild_user)

        self.codebuild_user.node.default_child.override_logical_id(logical_name)
        self.access_keys.override_logical_id(f"{logical_name}AccessKeys")
        self.ssm_access_keys.node.default_child.override_logical_id(f"{logical_name}SSMAccessKeys")
        self.user_permissions.node.default_child.override_logical_id(f"{logical_name}Policy")
