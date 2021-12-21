from aws_cdk import core as cdk, aws_lambda as _lambda
from microbit.data_lake.base import BaseDataLakeBucket
from microbit import active_environment
from microbit.common_stack import CommonStack
from microbit.lambda_functions.base import (
    LambdaRole,
)


class LambdaFunctionsStack(cdk.Stack):
    def __init__(
            self,
            scope: cdk.Construct,
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

        fn = _lambda.Function(
            scope=self,
            id=f"{self.deploy_env.value}-lambda-functions",
            runtime=_lambda.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.seconds(amount=30),
            handler="lambda_handler.handler",
            # code=_lambda.Code.from_bucket(bucket=self.lambda_bucket, key='lambda_handler.py'),
            code=_lambda.Code.from_inline(open("microbit/lambda_functions/functions/lambda_handler.py").read()),
            role=LambdaRole(self, self.data_lake_raw, self.data_lake_processed),
        )
