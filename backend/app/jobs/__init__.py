"""Scheduled background jobs.

Each module here is an executable entrypoint intended to be run by a scheduler
(Render Cron Job, Kubernetes CronJob, cron, etc.), for example:

    python -m app.jobs.auto_assign
"""
