from aws_cdk import core as cdk, aws_lambda as _lambda, aws_s3 as s3, aws_s3_notifications as s3n
from microbit.data_lake.base import BaseDataLakeBucket
from microbit import active_environment
from microbit.common_stack import CommonStack
from microbit.lambda_functions.base import LambdaRole


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
        super().__init__(
            scope, id=f"{self.deploy_env.value}-lambda-functions-stack", **kwargs
        )

        self.fn = _lambda.Function(
            scope=self,
            id=f"{self.deploy_env.value}-lambda-functions",
            runtime=_lambda.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.seconds(amount=120),
            handler="index.lambda_handler",
            code=_lambda.Code.from_inline(
                open("microbit/lambda_functions/functions/lambda_handler.py").read()
            ),
            role=LambdaRole(self, self.data_lake_raw, self.data_lake_processed),
        )

        # # create s3 notification for lambda function
        # notification = s3n.LambdaDestination(fn)
        #
        # # # assign notification for the s3 event type (ex: OBJECT_CREATED)
        # self.data_lake_raw.add_event_notification(s3.EventType.OBJECT_CREATED, notification)
