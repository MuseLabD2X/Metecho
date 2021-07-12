# Generated by Django 3.2 on 2021-04-20 20:47


from django.db import migrations


def normalize_project_collaborators(apps, schema_editor):
    """
    Replace copies of GitHub collaborator objects with plain IDs
    and only store the canonical representation of collaborators in Projects.
    """
    Epic = apps.get_model("api", "Epic")
    Task = apps.get_model("api", "Task")

    for epic in Epic.objects.filter(github_users__isnull=False):
        epic.github_users = tuple(
            set(user["id"] for user in epic.github_users if user.get("id"))
        )
        epic.save()

    for task in Task.objects.all():
        if task.assigned_dev:
            task.assigned_dev_id = task.assigned_dev.get("id")
        if task.assigned_qa:
            task.assigned_qa_id = task.assigned_qa.get("id")
        if task.reviewers:
            task.reviewers = [user["id"] for user in task.reviewers if user.get("id")]
        task.save()


def denormalize_project_collaborators(apps, schema_editor):
    """
    Create copies of complete GitHub collaborator objects on all models that need them.
    """
    Project = apps.get_model("api", "Project")

    for project in Project.objects.all():
        collaborators = {collab["id"]: collab for collab in project.github_users}

        for epic in project.epics.all():
            epic.github_users = [collaborators[_id] for _id in epic.github_users]
            epic.save()

            for task in epic.tasks.all():
                if task.assigned_dev_id:
                    task.assigned_dev = collaborators[task.assigned_dev_id]
                if task.assigned_qa_id:
                    task.assigned_qa = collaborators[task.assigned_qa_id]
                if task.reviewers:
                    task.reviewers = [collaborators[_id] for _id in task.reviewers]
                task.save()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0098_add_task_assignee_ids"),
    ]

    operations = [
        migrations.RunPython(
            normalize_project_collaborators,
            reverse_code=denormalize_project_collaborators,
        )
    ]