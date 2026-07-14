"""Celery has been removed.

Async tasks (webhooks, emails, retention) are now handled inline
or via a lightweight background worker. See background.py.
"""
