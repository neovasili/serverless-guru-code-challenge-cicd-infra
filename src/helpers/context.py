from aws_cdk import core


class ContextHelper:
    def __init__(self, cdk_app: core.App):
        self.app = cdk_app

        context_termination_protection = self.app.node.try_get_context("termination_protection")
        context_project = self.app.node.try_get_context("project")
        context_version = self.app.node.try_get_context("version")
        context_stage = self.app.node.try_get_context("stage")
        stack_prefix = self.app.node.try_get_context("stack_prefix")

        self.app_termination_protection = False
        if context_termination_protection is not None:
            self.app_termination_protection = context_termination_protection in ("True", "true", True)

        self.app_tags = dict()
        self.app_project = context_project if context_project is not None else "SGCC"
        self.app_version = context_version if context_version is not None else "v0.0.1"
        self.app_stage = context_stage if context_stage is not None else "dev"

        self.app_tags["project"] = self.app_project
        self.app_tags["version"] = self.app_version
        self.app_tags["stage"] = self.app_stage

        self.app_stack_prefix = f"{stack_prefix}-" if stack_prefix is not None else ""


class ArtifactsContext(ContextHelper):
    def __init__(self, cdk_app: core.App):
        super().__init__(cdk_app)

        deploy_accounts = self.app.node.try_get_context("deploy_accounts")
        self.app_deploy_accounts = deploy_accounts if deploy_accounts is not None else list()
