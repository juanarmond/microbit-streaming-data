from aws_cdk import core as cdk, aws_lambda as _lambda
from microbit.data_lake.base import BaseDataLakeBucket
from microbit import active_environment
from microbit.common_stack import CommonStack
from microbit.lambda_functions.base import (
    BaseLambdaBucket,
    LambdaRole,
)
import boto3, os


# class LambdaRole(iam.Role):
#     def __init__(
#             self,
#             scope: cdk.Construct,
#             data_lake_raw: BaseDataLakeBucket,
#             data_lake_processed: BaseDataLakeBucket,
#             **kwargs,
#     ) -> None:
#         self.deploy_env = active_environment
#         self.data_lake_raw = data_lake_raw
#         self.data_lake_processed = data_lake_processed
#
#         super().__init__(
#             scope,
#             id=f"iam-{self.deploy_env.value}-lambda-functions-role",
#             assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
#             description="Role to allow Lambda to access data lake",
#         )
#
#     def add_policy(self):
#         policy = iam.Policy(
#             self,
#             id=f"iam-{self.deploy_env.value}-lambda-functions-policy",
#             policy_name=f"iam-{self.deploy_env.value}-lambda-functions-policy",
#             statements=[
#                 iam.PolicyStatement(
#                     actions=[
#                         "s3:AbortMultipartUpload",
#                         "s3:GetBucketLocation",
#                         "s3:GetObject",
#                         "s3:ListBucket",
#                         "s3:ListBucketMultipartUploads",
#                         "s3:PutObject",
#                     ],
#                     resources=[
#                         self.data_lake_raw.bucket_arn,
#                         f"{self.data_lake_raw.bucket_arn}/*",
#                         self.data_lake_processed.bucket_arn,
#                         f"{self.data_lake_processed.bucket_arn}/*",
#                     ],
#                 )
#             ],
#         )
#         self.attach_inline_policy(policy)


class LambdaFunctionsStack(cdk.Stack):
    def __init__(
            self,
            scope: cdk.Construct,
            # construct_id: str,
            data_lake_raw: BaseDataLakeBucket,
            data_lake_processed: BaseDataLakeBucket,
            common_stack: CommonStack,
            **kwargs,
    ) -> None:
        self.common_stack = common_stack
        self.deploy_env = active_environment
        self.data_lake_raw = data_lake_raw
        self.data_lake_processed = data_lake_processed
        super().__init__(scope, id=f"{self.deploy_env.value}-lambda-functions-stack", **kwargs)

        self.lambda_bucket = BaseLambdaBucket(self)

        path = "microbit/lambda_functions/functions/"
        for filename in os.listdir(path):
            self.upload_to_aws(f"{path}/{filename}", self.lambda_bucket, filename)



        fn = _lambda.Function(
            scope=self,
            id=f"{self.deploy_env.value}-lambda-functions",
            runtime=_lambda.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.seconds(amount=30),
            handler="lambda_handler.handler",
            code=_lambda.Code.from_bucket(bucket=self.lambda_bucket, key='lambda_handler.py'),
            # code=_lambda.Code.from_inline(open("microbit/lambda_functions/functions/lambda_handler.py").read()),
            role=LambdaRole(self, self.data_lake_raw, self.data_lake_processed),
        )

    def upload_to_aws(self, local_file, bucket, s3_file):
        client = boto3.client("lambda-functions")
        try:
            client.upload_file(local_file, bucket, s3_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False