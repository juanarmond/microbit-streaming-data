from aws_cdk import core as cdk, aws_lambda as _lambda, aws_s3 as s3, aws_iam as iam
from microbit.data_lake.base import BaseDataLakeBucket


class LambdaFunctionsStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        processed_data_lake_bucket: BaseDataLakeBucket,
        **kwargs,
    ) -> None:
        self.processed_data_lake_bucket = processed_data_lake_bucket

        super().__init__(scope, construct_id, **kwargs)

        fn = _lambda.Function(
            scope=self,
            id=f"{self.deploy_env.value}-lambda-functions-stack",
            runtime=_lambda.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.seconds(amount=30),
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("lambda_functions/functions"),
        )

        # bucket = s3.Bucket(
        #     scope=self,
        #     id="bucket-mercado-bitcoin",
        #     bucket_name="belisco-cripto-milionario",
        # )

        fn.add_to_role_policy(
            statement=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:PutObject", "s3:ListBucket", "s3:PutObjectAcl"],
                resources=[
                    self.processed_data_lake_bucket.bucket_arn,
                    f"{self.processed_data_lake_bucket.bucket_arn}/*",
                ],
            )
        )
