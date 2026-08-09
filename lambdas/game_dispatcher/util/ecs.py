import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ecs = boto3.client("ecs", region_name=os.environ["AWS_REGION"])

# Tracker tasks are launched with startedBy = "game#<game_id>" so the dispatcher
# can tell, on a later run, which games already have a live tracker without
# needing to mutate the schedule table.
_STARTED_BY_PREFIX = "game#"


def get_tracked_game_ids() -> set[int]:
    """Return game_ids that currently have a running/pending tracker task.

    Both list_tasks and describe_tasks cap at 100 tasks/ARNs per call; with at
    most ~15 concurrent game trackers we will never approach that, so a single
    call to each is sufficient.
    """
    cluster = os.environ["ECS_CLUSTER"]

    # desiredStatus RUNNING also surfaces tasks still in PENDING/PROVISIONING.
    task_arns = ecs.list_tasks(cluster=cluster, desiredStatus="RUNNING").get("taskArns", [])
    if not task_arns:
        return set()

    tracked: set[int] = set()
    for task in ecs.describe_tasks(cluster=cluster, tasks=task_arns).get("tasks", []):
        started_by = task.get("startedBy", "")
        if started_by.startswith(_STARTED_BY_PREFIX):
            tracked.add(int(started_by[len(_STARTED_BY_PREFIX):]))

    return tracked


def start_tracker(game_id: int):
    """Launch a Fargate task to poll live state for a single game."""
    subnets = os.environ["TASK_SUBNETS"].split(",")
    security_groups = os.environ["TASK_SECURITY_GROUPS"].split(",")

    resp = ecs.run_task(
        cluster=os.environ["ECS_CLUSTER"],
        taskDefinition=os.environ["TASK_DEFINITION"],
        launchType="FARGATE",
        count=1,
        startedBy=f"{_STARTED_BY_PREFIX}{game_id}",
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": subnets,
                "securityGroups": security_groups,
                "assignPublicIp": os.environ.get("ASSIGN_PUBLIC_IP", "ENABLED"),
            }
        },
        overrides={
            "containerOverrides": [
                {
                    "name": os.environ["CONTAINER_NAME"],
                    "environment": [
                        {"name": "GAME_ID", "value": str(game_id)},
                        {"name": "AWS_REGION", "value": os.environ["AWS_REGION"]},
                    ],
                }
            ]
        },
    )

    failures = resp.get("failures", [])
    if failures:
        raise RuntimeError(f"run_task failed for game {game_id}: {failures}")

    task_arn = resp["tasks"][0]["taskArn"]
    logger.info("Started tracker task %s for game %s", task_arn, game_id)
    return task_arn
