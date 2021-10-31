#!/usr/bin/env python3

from aws_cdk import core
from data_lake.stack import DataLakeStack
from kinesis.stack import KinesisStack

app = core.App()
data_lake = DataLakeStack(app)
kinesis = KinesisStack(app, data_lake_raw_bucket=data_lake.data_lake_raw_bucket)
app.synth()
