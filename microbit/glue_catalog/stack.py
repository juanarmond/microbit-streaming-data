from aws_cdk import core
from microbit import active_environment
from microbit.data_lake.base import BaseDataLakeBucket
from microbit.glue_catalog.base import (
    BaseDataLakeGlueDatabase,
    BaseDataLakeGlueRole,
    BaseGlueCrawler,
)


class GlueCatalogStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        data_lake_raw: BaseDataLakeBucket,
        data_lake_processed: BaseDataLakeBucket,
        **kwargs,
    ) -> None:
        self.data_lake_raw = data_lake_raw
        self.data_lake_processed = data_lake_processed
        self.deploy_env = active_environment
        super().__init__(
            scope, id=f"{self.deploy_env.value}-glue-catalog-stack", **kwargs
        )

        self.raw_database = BaseDataLakeGlueDatabase(
            self, data_lake_bucket=self.data_lake_raw
        )

        self.processed_database = BaseDataLakeGlueDatabase(
            self, data_lake_bucket=self.data_lake_processed
        )

        self.role_raw = BaseDataLakeGlueRole(
            self, data_lake_bucket=self.data_lake_raw
        )

        self.role_processed = BaseDataLakeGlueRole(
            self, data_lake_bucket=self.data_lake_processed
        )

        self.atomic_events_crawler_raw = BaseGlueCrawler(
            self,
            glue_database=self.raw_database,
            glue_role=self.role_raw,
            table_name="atomic_events",
            schedule_expression="cron(0/5 * * * ? *)",
        )

        self.atomic_events_crawler_raw.node.add_dependency(self.raw_database)
        self.atomic_events_crawler_raw.node.add_dependency(self.role_raw)

        self.atomic_events_crawler_processed = BaseGlueCrawler(
            self,
            glue_database=self.data_lake_processed,
            glue_role=self.role_processed,
            table_name="atomic_events",
            schedule_expression="cron(0/5 * * * ? *)",
        )

        self.atomic_events_crawler_processed.node.add_dependency(self.data_lake_processed)
        self.atomic_events_crawler_processed.node.add_dependency(self.role_processed)
