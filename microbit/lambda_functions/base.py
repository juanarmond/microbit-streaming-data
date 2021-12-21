from aws_cdk import core, aws_iam as iam
from microbit.data_lake.base import BaseDataLakeBucket
from microbit import active_environment


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
        self.add_policy()
        self.add_instance_profile()

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

    def add_instance_profile(self):
        iam.CfnInstanceProfile(
            self,
            id=f"iam-{self.deploy_env.value}-lambda-data-lake-{self.layer.value}-instance-profile",
            instance_profile_name=f"iam-{self.deploy_env.value}-lambda-data-lake-{self.layer.value}-instance-profile",
            roles=[self.role_name],
        )