from aws_cdk import core as cdk, aws_lambda as _lambda, aws_iam as iam
from microbit.data_lake.base import BaseDataLakeBucket
from microbit import active_environment


class LambdaRole(iam.Role):
    def __init__(
        self,
        scope: cdk.Construct,
        data_lake_processed_bucket: BaseDataLakeBucket,
        **kwargs,
    ) -> None:
        self.deploy_env = active_environment
        self.data_lake_processed_bucket = data_lake_processed_bucket

        super().__init__(
            scope,
            id=f"iam-{self.deploy_env.value}-lambda-functions-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Role to allow Lambda to save data to data lake processed",
        )

    def add_policy(self):
        policy = iam.Policy(
            self,
            id=f"iam-{self.deploy_env.value}-data-lake-processed-lambda-functions-policy",
            policy_name=f"iam-{self.deploy_env.value}-data-lake-processed-lambda-functions-policy",
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
                        self.data_lake_processed_bucket.bucket_arn,
                        f"{self.data_lake_processed_bucket.bucket_arn}/*",
                    ],
                )
            ],
        )
        self.attach_inline_policy(policy)



class LambdaFunctionsStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        processed_data_lake_bucket: BaseDataLakeBucket,
        **kwargs,
    ) -> None:
        self.deploy_env = active_environment
        self.data_lake_processed_bucket = processed_data_lake_bucket
        super().__init__(scope, construct_id, **kwargs)

        fn = _lambda.Function(
            scope=self,
            id=f"{self.deploy_env.value}-lambda-functions-stack",
            runtime=_lambda.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.seconds(amount=30),
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("microbit/lambda_functions/functions"),
        )

        fn.add_to_role_policy(
            statement=self.lambda_functions_role.role_arn
        )

    @property
    def lambda_functions_role(self):
        return LambdaRole(
            self,
            deploy_env=self.deploy_env,
            data_lake_processed_bucket=self.data_lake_processed_bucket,
        )
