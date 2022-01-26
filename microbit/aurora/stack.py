import os
from aws_cdk import core
from aws_cdk import (
    aws_iam as iam,
    aws_rds as rds,
    aws_ec2 as ec2,
)
from microbit.common_stack import CommonStack
from microbit.data_lake.base import BaseDataLakeBucket
# from microbit.aurora.base import (BaseAuroraBucket, RDSRole)
from microbit import active_environment


class RDSRole(iam.Role):
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
            id=f"iam-{self.deploy_env}-data-lake-rds-role",
            assumed_by=iam.ServicePrincipal("rds.amazonaws.com"),
            description="Role to allow RDS to access data from data lake",
        )
        self.add_policy()

    def add_policy(self):
        policy = iam.Policy(
            self,
            id=f"iam-{self.deploy_env}-data-lake-rds-policy",
            policy_name=f"iam-{self.deploy_env}-data-lake-rds-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "s3:PutObjectTagging",
                        "s3:DeleteObject",
                        "s3:ListBucket",
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

        return policy


class RdsStack(core.Stack):
    def __init__(
            self,
            scope: core.Construct,
            common_stack: CommonStack,
            data_lake_raw: BaseDataLakeBucket,
            data_lake_processed: BaseDataLakeBucket,
            **kwargs,
    ) -> None:
        self.common_stack = common_stack
        self.deploy_env = active_environment
        self.data_lake_raw = data_lake_raw
        self.data_lake_processed = data_lake_processed
        super().__init__(scope, id=f"{self.deploy_env.value}-rds-aurora-stack", **kwargs)

        # import_bucket = self.data_lake_processed
        # export_bucket = s3.Bucket(self, "exportbucket")

        cluster = rds.DatabaseCluster(self, "microbit_aurora",
                                      engine=rds.DatabaseClusterEngine.AURORA_POSTGRESQL,
                                      # credentials=rds.Credentials.from_generated_secret("clusteradmin"),
                                      # Optional - will default to 'admin' username and generated password
                                      instance_props=rds.InstanceProps(
                                          # optional , defaults to t3.medium
                                          instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2,
                                                                            ec2.InstanceSize.SMALL),
                                          vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
                                          vpc=self.common_stack.custom_vpc, ),
                                      # s3_import_buckets=[import_bucket],
                                      s3_import_role=RDSRole(self, self.data_lake_raw, self.data_lake_processed)
                                      # s3_export_buckets = [export_bucket]
                                      )

        # instance = rds.DatabaseInstance(self, "Instance",
        #                                 engine=rds.DatabaseInstanceEngine.oracle_se2(
        #                                     version=rds.OracleEngineVersion.VER_19_0_0_0_2020_04_R1),
        #                                 # optional, defaults to m5.large
        #                                 instance_type=ec2.InstanceType.of(
        #                                     ec2.InstanceClass.BURSTABLE3,
        #                                     ec2.InstanceSize.SMALL),
        #                                 # credentials=rds.Credentials.from_generated_secret("syscdk"),
        #                                 # Optional - will default to 'admin' username and generated password
        #                                 vpc=self.common_stack.custom_vpc,
        #                                 vpc_subnets=ec2.SubnetSelection(
        #                                     subnet_type=ec2.SubnetType.PRIVATE
        #                                 )
        #                                 )

        # roles = RDSRole(self, self.data_lake_raw, self.data_lake_processed)
        # instance.grant_connect(roles)
