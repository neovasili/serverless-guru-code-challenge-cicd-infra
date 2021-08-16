from aws_cdk import (
    core as cdk,
    aws_codebuild as codebuild,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_logs as logs,
)
from src.helpers.buildspec import BuildSpecHelper
from src.helpers.name import NameHelper
from src.constructs.s3 import DeployResourcesBucket


class CodeBuildConstruct(cdk.Construct):
    @property
    def project_arn(self):
        return self.project.project_arn

    @property
    def project_role_arn(self):
        return self.project.role.role_arn

    @property
    def log_group_arn(self):
        return self.log_group.log_group_arn

    @property
    def source_bucket_arn(self):
        return self.source_bucket.bucket_arn

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        build_spec: str,
        description: str,
        build_image: codebuild.LinuxBuildImage = None,
        privileged: bool = False,
        environment_variables: dict = None,
    ) -> None:
        super().__init__(scope, id=construct_id)

        self.project_name = f"{construct_id}-project"

        self.log_group = logs.LogGroup(
            self,
            id=f"{self.project_name}-log-group",
            log_group_name=f"/aws/codebuild/{self.project_name}",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.TWO_WEEKS,
        )

        self.logging_options = codebuild.LoggingOptions(
            cloud_watch=codebuild.CloudWatchLoggingOptions(
                enabled=True,
                log_group=self.log_group,
            ),
        )

        self.build_environment = codebuild.BuildEnvironment(
            build_image=codebuild.LinuxBuildImage.STANDARD_5_0 if build_image is None else build_image,
            compute_type=codebuild.ComputeType.SMALL,
            privileged=privileged,
        )

        self.project = codebuild.Project(
            self,
            id=self.project_name,
            build_spec=codebuild.BuildSpec.from_object_to_yaml(build_spec),
            description=description,
            environment=self.build_environment,
            environment_variables=environment_variables,
            project_name=construct_id,
            timeout=cdk.Duration.minutes(90),
            logging=self.logging_options,
        )

        self.project.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=self.project_name),
        )
        self.project.role.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=f"{self.project_name}-role"),
        )
        self.log_group.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=f"{self.project_name}-log-group"),
        )

    def add_ecr_pull_permissions(self, ecr_repositories: list):
        ecr_repo_arns = list()

        for ecr_repo in ecr_repositories:
            ecr_repo_arns.append(ecr_repo.repository_arn)

        self.ecr_policy = iam.Policy(
            self,
            id=f"{self.project_name}-pull-policy",
            policy_name=NameHelper.to_pascal_case(self.project_name),
            roles=[self.project.role],
        )

        self.ecr_policy.add_statements(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                ],
                resources=ecr_repo_arns,
            ),
        )

        self.ecr_policy.add_statements(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:GetAuthorizationToken",
                ],
                resources=["*"],
            ),
        )

        self.ecr_policy.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=f"{self.project_name}-policy"),
        )

    def add_ecr_push_permissions(self, ecr_repositories: list):
        ecr_repo_arns = list()

        for ecr_repo in ecr_repositories:
            ecr_repo_arns.append(ecr_repo.repository_arn)

        self.ecr_policy = iam.Policy(
            self,
            id=f"{self.project_name}-push-policy",
            policy_name=NameHelper.to_pascal_case(self.project_name),
            roles=[self.project.role],
        )

        self.ecr_policy.add_statements(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:PutImage",
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                ],
                resources=ecr_repo_arns,
            ),
        )

        self.ecr_policy.add_statements(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:GetAuthorizationToken",
                ],
                resources=["*"],
            ),
        )

        self.ecr_policy.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=f"{self.project_name}-policy"),
        )


class BuildImageCodeBuildProject(CodeBuildConstruct):
    def __init__(self, scope: cdk.Construct, ecr_repositories: list, termination_protection: bool) -> None:
        project_name = "build-images"

        super().__init__(
            scope,
            project_name,
            description=f"CodeBuild {project_name} for building deploy images",
            build_spec=BuildSpecHelper.get_buildspec(file_location="src/config/build-docker-image-buildspec.yml"),
            privileged=True,
        )

        self.add_ecr_push_permissions(ecr_repositories=ecr_repositories)

        self.source_bucket_construct = DeployResourcesBucket(
            self,
            construct_id=f"{self.project_name}-bucket",
            bucket_suffix=f"{self.project_name}-source-bucket",
            termination_protection=termination_protection,
        )
        self.source_bucket = self.source_bucket_construct.bucket

        self.s3_policy = iam.Policy(
            self,
            id=f"{self.project_name}-s3-policy",
            policy_name=NameHelper.to_pascal_case(f"{self.project_name}-s3-policy"),
            roles=[self.project.role],
        )

        self.s3_policy.add_statements(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:GetObjectVersion",
                    "s3:ListBucket",
                    "s3:ListBucketVersions",
                ],
                resources=[
                    self.source_bucket.arn_for_objects("*"),
                    self.source_bucket.bucket_arn,
                ],
            ),
        )

        self.s3_policy.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=f"{self.project_name}-s3-policy"),
        )

    def add_bucket_policy(self, principals: list) -> None:
        self.source_bucket_construct.add_restricted_bucket_policy(
            principals_arns=principals,
            put_object_permission=True,
        )


class DeployCodeBuildProject(CodeBuildConstruct):
    @property
    def image_ssm_arn(self):
        return self.image_repo_ssm.parameter_arn

    def __init__(
        self,
        scope: cdk.Construct,
        ecr_repository: str,
        deploy_accounts: list,
        action: str,
    ) -> None:
        project_name = ecr_repository.repository_name

        build_image = codebuild.LinuxBuildImage.from_ecr_repository(repository=ecr_repository.repository)

        super().__init__(
            scope,
            f"{project_name}-{action}",
            description=f"CodeBuild for {action} {project_name} repository",
            build_spec=BuildSpecHelper.get_buildspec(file_location=f"src/config/{action}-sls-buildspec.yml"),
            build_image=build_image,
        )
        self.add_ecr_pull_permissions(ecr_repositories=[ecr_repository])

        if len(deploy_accounts) > 0:
            policy_name = f"{project_name}-{action}-policy"

            self.deploy_policy = iam.Policy(
                self,
                id=policy_name,
                policy_name=NameHelper.to_pascal_case(policy_name),
                roles=[self.project.role],
            )

            deploy_roles = list()

            for deploy_account in deploy_accounts:
                deploy_role = f"arn:aws:iam::{deploy_account}:role/infra-automation/InfrastructureDeploy"
                deploy_roles.append(deploy_role)

            self.deploy_policy.add_statements(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "sts:AssumeRole",
                    ],
                    resources=deploy_roles,
                ),
            )

            self.deploy_policy.node.default_child.override_logical_id(
                NameHelper.to_pascal_case(name=policy_name),
            )

        current_stack = cdk.Stack.of(self)

        self.image_repo_ssm = ssm.StringParameter(
            scope=self,
            id=f"{project_name}-codebuild-image-base",
            parameter_name=f"/codebuild/{project_name}-{action}/image-base",
            string_value=f"{current_stack.account}.dkr.ecr.{current_stack.region}.amazonaws.com/{project_name}",
        )
        self.image_repo_ssm.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=f"{project_name}-{action}-ssm-image-base"),
        )
