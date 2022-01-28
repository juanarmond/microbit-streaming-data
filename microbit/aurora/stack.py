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
        self.aurora_sg = ec2.SecurityGroup(
            self,
            f"aurora-{self.deploy_env.value}-sg",
            vpc=self.common_stack.custom_vpc,
            allow_all_outbound=True,
            security_group_name=f"aurora-{self.deploy_env.value}-sg",
        )

        self.aurora_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("0.0.0.0/0"), connection=ec2.Port.tcp(3306)
        )

        for subnet in self.common_stack.custom_vpc.private_subnets:
            self.aurora_sg.add_ingress_rule(
                peer=ec2.Peer.ipv4(subnet.ipv4_cidr_block),
                connection=ec2.Port.tcp(3306),
            )

        cluster = rds.DatabaseCluster(
            self,
            f"microbit-{self.deploy_env.value}-aurora",
            default_database_name="microbit_aurora",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_13_3
            ),
            cluster_identifier=f"microbit-{self.deploy_env.value}-aurora-cluster",
            instance_identifier_base=f"microbit-{self.deploy_env.value}-aurora-instance",
            # credentials=rds.Credentials.from_generated_secret("clusteradmin"),
            # Optional - will default to 'admin' username and generated password
            instance_props=rds.InstanceProps(
                # optional , defaults to t3.medium
                instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3,
                                                  ec2.InstanceSize.MEDIUM),
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                vpc=self.common_stack.custom_vpc,
                security_groups=[self.aurora_sg]
                ),
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
