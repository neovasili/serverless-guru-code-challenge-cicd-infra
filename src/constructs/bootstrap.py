from aws_cdk import (
    core as cdk,
    aws_iam as iam,
)
from src.helpers.name import NameHelper


class BootstrapConstruct(cdk.Construct):
    def __init__(self, scope: cdk.Construct, construct_id: str, codebuild_roles: list) -> None:
        super().__init__(scope, id=construct_id)

        role_name = NameHelper.to_pascal_case(name="infrastructure-deploy")

        codebuild_roles_principals = iam.CompositePrincipal(iam.ServicePrincipal("codebuild.amazonaws.com"))

        for role in codebuild_roles:
            codebuild_roles_principals.add_principals(iam.ArnPrincipal(arn=role))

        self.deploy_role = iam.Role(
            self,
            id=f"{construct_id}-deploy-role",
            role_name=role_name,
            path="/infra-automation/",
            assumed_by=codebuild_roles_principals,
            description=f"{construct_id} Deploy IAM Role",
        )

        self.deploy_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))

        self.deploy_role.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=f"{role_name}-role"),
        )
