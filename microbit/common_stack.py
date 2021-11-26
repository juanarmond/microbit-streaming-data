from aws_cdk import core
from aws_cdk import aws_ec2 as ec2
from microbit import active_environment


class CommonStack(core.Stack):
    def __init__(self, scope: core.Construct, **kwargs) -> None:
        self.deploy_env = active_environment
        super().__init__(scope, id=f"{self.deploy_env.value}-common-stack", **kwargs)

        self.custom_vpc = ec2.Vpc(self, f"vpc-{self.deploy_env.value}")

        self.orders_rds_sg = ec2.SecurityGroup(
            self,
            f"orders-{self.deploy_env.value}-sg",
            vpc=self.custom_vpc,
            allow_all_outbound=True,
            security_group_name=f"orders-{self.deploy_env.value}-sg",
        )

        self.orders_rds_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("0.0.0.0/0"), connection=ec2.Port.tcp(5432)
        )

        for subnet in self.custom_vpc.private_subnets:
            self.orders_rds_sg.add_ingress_rule(
                peer=ec2.Peer.ipv4(subnet.ipv4_cidr_block),
                connection=ec2.Port.tcp(5432),
            )