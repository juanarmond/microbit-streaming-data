from aws_cdk import core as cdk, aws_lambda as _lambda, aws_iam as iam, aws_ec2 as ec2
from microbit.data_lake.base import BaseDataLakeBucket
from microbit import active_environment
from microbit.common_stack import CommonStack


class LambdaRole(iam.Role):
    def __init__(
        self,
        scope: cdk.Construct,
        data_lake_raw: BaseDataLakeBucket,
        data_lake_processed: BaseDataLakeBucket,
        **kwargs,
    ) -> None:
        self.deploy_env = active_environment
        self.data_lake_raw = data_lake_raw
        self.data_lake_processed = data_lake_processed

        super().__init__(
            scope,
            id=f"iam-{self.deploy_env.value}-lambda-functions-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Role to allow Lambda to access data lake",
        )

    def add_policy(self):
        policy = iam.Policy(
            self,
            id=f"iam-{self.deploy_env.value}-lambda-functions-policy",
            policy_name=f"iam-{self.deploy_env.value}-lambda-functions-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "s3:AbortMultipartUpload",
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
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



class LambdaFunctionsStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        processed_data_lake_bucket: BaseDataLakeBucket,
        common_stack: CommonStack,
        **kwargs,
    ) -> None:
        self.common_stack = common_stack
        self.deploy_env = active_environment
        self.data_lake_processed = processed_data_lake_bucket
        super().__init__(scope, construct_id, **kwargs)

        # self.lambda_sg = ec2.SecurityGroup(
        #     self,
        #     f"redshift-{self.deploy_env.value}-sg",
        #     vpc=self.common_stack.custom_vpc,
        #     allow_all_outbound=True,
        #     security_group_name=f"redshift-{self.deploy_env.value}-sg",
        # )
        #
        # self.lambda_sg.add_ingress_rule(
        #     peer=ec2.Peer.ipv4("0.0.0.0/0"), connection=ec2.Port.tcp(5439)
        # )
        #
        # for subnet in self.common_stack.custom_vpc.private_subnets:
        #     self.lambda_sg.add_ingress_rule(
        #         peer=ec2.Peer.ipv4(subnet.ipv4_cidr_block),
        #         connection=ec2.Port.tcp(5439),
        #     )

        fn = _lambda.Function(
            scope=self,
            id=f"{self.deploy_env.value}-lambda-functions-stack",
            runtime=_lambda.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.seconds(amount=30),
            handler="lambda_handler.handler",
            # code=_lambda.Code.from_asset("microbit/lambda_functions/functions"),
            code=_lambda.Code.from_inline(open("microbit/lambda_functions/functions/lambda_handler.py").read()),
            role=LambdaRole(self, self.data_lake_processed),
            # security_groups=[self.lambda_sg],
            # vpc=self.common_stack.custom_vpc,
            # vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )