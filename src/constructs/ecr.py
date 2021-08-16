from aws_cdk import (
    core as cdk,
    aws_ecr as ecr,
)
from src.helpers.name import NameHelper


class ECRConstruct(cdk.Construct):
    @property
    def repository_name(self):
        return self.repo_name

    @property
    def repository_arn(self):
        return self.repository.repository_arn

    def __init__(
        self,
        scope,
        construct_id: str,
        termination_protection: bool,
    ) -> None:
        super().__init__(scope, id=construct_id)

        self.repo_name = construct_id

        repo_id = f"{construct_id}-ecr-repo"

        self.repository = ecr.Repository(
            scope=scope,
            id=repo_id,
            image_scan_on_push=True,
            image_tag_mutability=ecr.TagMutability.IMMUTABLE,
            repository_name=construct_id,
        )
        self.repository.add_lifecycle_rule(
            description="CI lifecycle rule",
            max_image_age=cdk.Duration.days(1),
            tag_status=ecr.TagStatus.TAGGED,
            tag_prefix_list=["ci_"],
        )

        self.repository.node.default_child.override_logical_id(NameHelper.to_pascal_case(name=repo_id))

        self.__set_delete_retention_policy(termination_protection=termination_protection)

    def __set_delete_retention_policy(self, termination_protection: bool) -> None:
        if not termination_protection:
            self.repository.node.find_child("Resource").cfn_options.deletion_policy = cdk.CfnDeletionPolicy.DELETE
