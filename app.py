#!/usr/bin/env python3

from aws_cdk import core as cdk

from src.helpers.context import (
    ArtifactsContext,
)
from src.stacks.artifacts import ArtifactsStack


app = cdk.App()

environment = cdk.Environment(region="eu-west-1")

artifacts_context = ArtifactsContext(cdk_app=app)

artifacts_stack = ArtifactsStack(
    scope=app,
    env=environment,
    context=artifacts_context,
)

app.synth()
