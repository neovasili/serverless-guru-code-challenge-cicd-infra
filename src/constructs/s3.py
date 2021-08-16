from aws_cdk import (
    core as cdk,
    aws_s3 as s3,
    aws_iam as iam,
)

from src.helpers.name import NameHelper


class S3Construct(cdk.Construct):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        bucket_suffix: str,
        termination_protection: bool = True,
        versioned: bool = False,
        lifecycle_rules: list = None,
        public_read_access: bool = False,
        website_index_document: str = None,
        website_error_document: str = None,
    ) -> None:
        super().__init__(scope, id=construct_id)

        self.bucket_suffix = bucket_suffix

        current_stack = cdk.Stack.of(self)

        bucket_lifecycle_rules = list()

        self.bucket = s3.Bucket(
            self,
            id=bucket_suffix,
            bucket_name=f"{current_stack.account}-{bucket_suffix}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True if not public_read_access else False,
                ignore_public_acls=True,
                restrict_public_buckets=True if not public_read_access else False,
            ),
            lifecycle_rules=bucket_lifecycle_rules,
            public_read_access=public_read_access,
            website_index_document=website_index_document,
            website_error_document=website_error_document,
            versioned=versioned,
        )

        if not termination_protection:
            self.bucket.node.find_child("Resource").cfn_options.deletion_policy = cdk.CfnDeletionPolicy.DELETE

        self.bucket.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=bucket_suffix),
        )

    def add_restricted_bucket_policy(self, principals_arns: list, put_object_permission: bool = False) -> None:
        bucket_policy_principals = list()

        actions = [
            "s3:GetObject",
            "s3:GetObjectVersion",
            "s3:ListBucket",
            "s3:ListBucketVersions",
        ]

        if put_object_permission:
            actions.insert(0, "s3:PutObject")

        for principal in principals_arns:
            bucket_policy_principals.append(iam.ArnPrincipal(arn=principal))

        self.bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=bucket_policy_principals,
                actions=actions,
                resources=[
                    self.bucket.arn_for_objects("*"),
                    self.bucket.bucket_arn,
                ],
            ),
        )

        self.bucket.policy.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=f"{self.bucket_suffix}-policy"),
        )

    def add_read_bucket_policy_for_canonical_users(self, canonical_users: list) -> None:
        actions = [
            "s3:GetObject",
        ]

        bucket_policy_principals = list()

        for canonical_user in canonical_users:
            bucket_policy_principals.append(iam.CanonicalUserPrincipal(canonical_user_id=canonical_user))

        self.bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=bucket_policy_principals,
                actions=actions,
                resources=[
                    self.bucket.arn_for_objects("*"),
                ],
            ),
        )

        self.bucket.policy.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=f"{self.bucket_suffix}-policy"),
        )


class DeployResourcesBucket(S3Construct):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        bucket_suffix: str,
        termination_protection: bool = True,
    ):
        super().__init__(
            scope,
            construct_id,
            bucket_suffix,
            termination_protection=termination_protection,
        )
        self.__add_temp_resources_lifecycle_rule()

    def __add_temp_resources_lifecycle_rule(self):
        self.bucket.add_lifecycle_rule(
            abort_incomplete_multipart_upload_after=cdk.Duration.days(1),
            enabled=True,
            expiration=cdk.Duration.days(30),
        )


class WebsiteBucket(S3Construct):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        bucket_suffix: str,
        website_index_document: str,
        website_error_document: str,
        termination_protection: bool = True,
    ):
        super().__init__(
            scope,
            construct_id,
            bucket_suffix,
            public_read_access=True,
            website_index_document=website_index_document,
            website_error_document=website_error_document,
            termination_protection=termination_protection,
        )

        self.bucket.policy.node.default_child.override_logical_id(
            NameHelper.to_pascal_case(name=f"{self.bucket_suffix}-policy"),
        )


class ResourcesBucket(S3Construct):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        bucket_suffix: str,
        versioned: bool = True,
        termination_protection: bool = True,
    ):
        super().__init__(
            scope,
            construct_id,
            bucket_suffix,
            termination_protection=termination_protection,
            versioned=versioned,
        )
