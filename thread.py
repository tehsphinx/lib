from .functions import *
import copy
import queue
import threading
from queue import Queue

__author__ = 'tehsphinx'


class BusyBee(threading.Thread):
    def __init__(self, function, thread_name, *args):
        threading.Thread.__init__(self, name=thread_name)
        self.thread_name = thread_name
        self.function = function
        self.args = args
        self.result = None

    def run(self):
        self.result = self.function(*self.args)


class BusyBeeQueue():
    def __init__(self, function, thread_name_prefix='Thread', size=5, eternal=False, gather_results=False,
                 gather_non_empty=True, max_queue=0):
        """

        @param function: function to be processed for each job
        @param thread_name_prefix: name of the Thread. Number is appended. default: "Thread"
        @param size: amound of workers you want to work on your queue
        @param eternal: keep running even if queue is empty. New jobs can be added any time and will then be processed
        @param gather_results: if this is true, work_bees function will wait for the bees to Nfinish and return the result of all the jobs
        """
        self.lock = threading.Lock()
        self.queue = Queue(maxsize=max_queue)

        self.function = function
        self.thread_name_prefix = thread_name_prefix
        self.size = size
        self.eternal = eternal
        self.gather_results = gather_results
        self.gather_non_empty = gather_non_empty
        self.bees = []

        self.stop_working = False

    def add_jobs(self, jobs):
        self.lock.acquire()
        for job in jobs:
            try:
                self.queue.put(job, block=False)
            except queue.Full:
                log.warn('job(s) lost. maxsize of queue is full')
                break
        self.lock.release()

    def stop_bees(self):
        self.stop_working = True

    def work_bees(self) -> list:
        thread_names = ['{0}-{1}'.format(self.thread_name_prefix, x) for x in range(self.size)]
        self.bees = []

        for thread_name in thread_names:
            bee = BusyBee(self._process_jobs, thread_name)
            self.bees.append(bee)
            bee.start()
            log.dbg('STARTED THREAD {0}'.format(thread_name))

        if self.gather_results:
            results = []
            for bee in self.bees:
                bee.join()
                results += bee.result
            return results

    def _process_jobs(self) -> list:
        results = []
        while not self.stop_working and (not self.queue.empty() or self.eternal):
            # TODO: rewrite case self.eternal = True. Use block feature of self.queue.get()
            self.lock.acquire()
            if not self.queue.empty():
                job = self.queue.get()
                """@type: dict"""
                log.dbg('GOT JOB', job)

                self.lock.release()
            else:
                self.lock.release()
                job = None

            if job:
                if self.gather_results:
                    if self.gather_non_empty:
                        results.append({'job': job, 'result': self.function(**job)})
                    else:
                        result = self.function(**job)
                        if result:
                            results.append(result)
                else:
                    self.function(**job)

        return results

    def check_on_bees(self):
        """
        checks on bees status and starts new ones if necessary. Only works with eternal = True and without gathering of results (for now)
        """
        if self.eternal and not self.gather_results:
            thread_names = [b.thread_name for b in self.bees if not b.isAlive()]
            self.bees = [b for b in self.bees if b.isAlive()]

            for thread_name in thread_names:
                bee = BusyBee(self._process_jobs, thread_name)
                self.bees.append(bee)
                bee.start()
                log.dbg('STARTED THREAD {0}'.format(thread_name))

    def has_jobs(self):
        return not self.queue.empty()

    def remaining_queue(self):
        """WARNING: not sure this should be used... could break things. Have a look at extract_queue instead"""
        jobs = []

        self.lock.acquire()
        while not self.queue.empty():
            jobs.append(self.queue.get())
        self.lock.release()

        return jobs

    def extract_queue(self) -> list:
        self.lock.acquire()
        jobs = copy.deepcopy(self.queue.queue)
        self.lock.release()

        return list(jobs)


class HamsterWheel(threading.Thread):
    """Thread that executes a task every N seconds"""

    def __init__(self, function, thread_name, args=None, interval=10):
        threading.Thread.__init__(self, name=thread_name)
        self._finished = threading.Event()
        self._interval = interval
        self._args = args if args is not None else {}

        self._function = function

    def run(self):
        while True:
            if self._finished.isSet():
                return
            log.dbg('EXECUTING HAMSTER WHEEL JOB')
            self._function(**self._args)

            # sleep for interval or until shutdown
            self._finished.wait(self._interval)

    def stop(self):
        """Stop this thread"""
        self._finished.set()

