#!/usr/bin/env python3
import os

from aws_cdk import core
from data_platform.data_lake.stack import DataLakeStack
from data_platform.kinesis.stack import KinesisStack

app = core.App()
data_lake = DataLakeStack(app)
kenisis = KinesisStack(app, data_lake_raw_bucket=data_lake.data_lake_raw_bucket)
app.synth()
