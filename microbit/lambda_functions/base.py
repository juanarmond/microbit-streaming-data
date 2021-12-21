from aws_cdk import core
from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam
)
from microbit.data_lake.base import BaseDataLakeBucket
from microbit import active_environment


class BaseLambdaBucket(s3.Bucket):
    def __init__(self, scope: core.Construct, **kwargs) -> None:
        self.deploy_env = scope.deploy_env
        self.obj_name = f"s3-microbit-{self.deploy_env.value}-lambda-functions"

        super().__init__(
            scope,
            id=self.obj_name,
            bucket_name=self.obj_name,
            removal_policy=core.RemovalPolicy.DESTROY,
            block_public_access=self.default_block_public_access(),
            encryption=self.default_encryption(),
            versioned=True,
            **kwargs,
        )

        self.add_lifecycle_rule(expiration=core.Duration.days(60))

    @staticmethod
    def default_block_public_access():
        """
        Block public access by default
        """
        block_public_access = s3.BlockPublicAccess(
            block_public_acls=True,
            block_public_policy=True,
            ignore_public_acls=True,
            restrict_public_buckets=True,
        )
        return block_public_access

    @staticmethod
    def default_encryption():
        """
        Enables encryption by default
        """
        encryption = s3.BucketEncryption(s3.BucketEncryption.S3_MANAGED)
        return encryption


class LambdaRole(iam.Role):
    def __init__(
            self,
            scope: core.Construct,
            data_lake_raw: BaseDataLakeBucket,
            data_lake_processed: BaseDataLakeBucket,
            **kwargs,
    ) -> None:
        self.deploy_env = active_environment
        self.data_lake_raw = data_lake_raw
        self.data_lake_processed = data_lake_processed

        super().__init__(
            scope,
            id=f"iam-{self.deploy_env.value}-lambda-functions-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Role to allow Lambda to access data lake",
        )

    def add_policy(self):
        policy = iam.Policy(
            self,
            id=f"iam-{self.deploy_env.value}-lambda-functions-policy",
            policy_name=f"iam-{self.deploy_env.value}-lambda-functions-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "s3:AbortMultipartUpload",
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:PutObject",
                    ],
                    resources=[
                        self.data_lake_raw.bucket_arn,
                        f"{self.data_lake_raw.bucket_arn}/*",
                        self.data_lake_processed.bucket_arn,
                        f"{self.data_lake_processed.bucket_arn}/*",
                    ],
                )
            ],
        )
        self.attach_inline_policy(policy)
