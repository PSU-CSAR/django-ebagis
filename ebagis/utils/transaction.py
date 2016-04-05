from __future__ import absolute_import

from celery import current_task, shared_task
from celery.states import STARTED
from celery.contrib.abortable import AbortableTask

from django.db import transaction

from ..exceptions import AbortedError


# this is just adding the if_aborted method to AbortableTask
class AbortableTask(AbortableTask):
    abstract = True

    def if_aborted(self):
        if self.is_aborted():
            raise AbortedError


# this is a reusable decorator used to create abortable celery tasks
def abortable_task(funct):
    # we need to wrap the task callable with the boilerplate
    # to handle the setup stuff related to allowing aborts
    def task_wrapper(self, *args, **kwargs):
        try:
            # check if aborted before doing anything
            # if so, this will raise Aborted Error
            self.if_aborted()
            # if not aborted set to started
            # FIXUP: this seems to be a race condition
            self.update_state(state=STARTED)
            # call the task function
            ret = funct(self, *args, **kwargs)
        except AbortedError:
            return "Task Aborted"
        return ret
    # celery uses the function name to identify tasks at creation
    # so we need to "change" the name of our wrapper function to
    # match the callable we want to be a task
    task_wrapper.__name__ = funct.__name__
    # return the callable wrapped in task_wrapper, but add
    # the shared task decorator with the AbortableTask base
    return shared_task(task_wrapper, bind=True, base=AbortableTask)


# we define our own atomic decorator that will check if the task
# is aborted before exiting the transaction, and if true rollback
# by raising an AbortedException
def atomic(funct):
    def abort_wrapper(*args, **kwargs):
        ret = funct(*args, **kwargs)
        if current_task and hasattr(current_task, "if_aborted"):
            current_task.if_aborted()
        return ret
    return transaction.atomic(abort_wrapper)
