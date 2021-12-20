#!/usr/bin/env python3

from aws_cdk import core
from microbit.data_lake.stack import DataLakeStack
from microbit.common_stack import CommonStack
from microbit.kinesis.stack import KinesisStack
from microbit.lambda_functions.stack import LambdaFunctionsStack
from microbit.glue_catalog.stack import GlueCatalogStack
from microbit.athena.stack import AthenaStack
from microbit.redshift.stack import RedshiftStack

app = core.App()
data_lake = DataLakeStack(app)
common_stack = CommonStack(app)
# kinesis = KinesisStack(app, data_lake_raw_bucket=data_lake.data_lake_raw_bucket)
lambda_functions = LambdaFunctionsStack(app, "LambdaFunctionsStack")
# glue_catalog = GlueCatalogStack(
#     app,
#     raw_data_lake_bucket=data_lake.data_lake_raw_bucket,
#     processed_data_lake_bucket=data_lake.data_lake_processed_bucket,
# )
# athena_stack = AthenaStack(app)
# redshift = RedshiftStack(
#     app,
#     data_lake_raw=data_lake.data_lake_raw_bucket,
#     data_lake_processed=data_lake.data_lake_processed_bucket,
#     common_stack=common_stack,
# )
app.synth()
