from microbit.data_lake.base import BaseDataLakeBucket, DataLakeLayer
from aws_cdk import core
from aws_cdk import (
    aws_s3 as s3,
    aws_s3_notifications as s3n
)

from microbit import active_environment
from microbit.lambda_functions.stack import LambdaFunctionsStack


class DataLakeStack(core.Stack):
    def __init__(self, scope: core.Construct, **kwargs) -> None:
        self.deploy_env = active_environment
        super().__init__(scope, id=f"{self.deploy_env.value}-data-lake-stack", **kwargs)

        # Data Lake Raw
        self.data_lake_raw = BaseDataLakeBucket(
            self, deploy_env=self.deploy_env, layer=DataLakeLayer.RAW
        )

        self.data_lake_raw.add_lifecycle_rule(
            transitions=[
                s3.Transition(
                    storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                    transition_after=core.Duration.days(90),
                ),
                s3.Transition(
                    storage_class=s3.StorageClass.GLACIER,
                    transition_after=core.Duration.days(360),
                ),
            ],
            enabled=True,
        )

        # Data Lake Processed
        self.data_lake_processed = BaseDataLakeBucket(
            self, deploy_env=self.deploy_env, layer=DataLakeLayer.PROCESSED
        )

        # # create s3 notification for lambda function
        # notification = s3n.LambdaDestination(LambdaFunctionsStack.fn)
        #
        # # assign notification for the s3 event type (ex: OBJECT_CREATED)
        # self.data_lake_raw.add_event_notification(s3.EventType.OBJECT_CREATED, notification)
