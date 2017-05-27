""" Main entry point for all python services running on the device
"""

import glob
import logging
import signal
import subprocess
import time
from constants import LOGGING_FORMAT, LOGGING_LEVEL, \
                      PROCESS_MONITORING_INTERVAL

logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
LOGGER = logging.getLogger('main')

if __name__ == '__main__':
    class RestartThresholdExceeded(Exception):
        """ Exception that is raised if a process has been
            restarted more times than the allowed threshold
        """
        def __init__(self, restarts):
            Exception.__init__(self)
            self.restarts = restarts


    class SubProcess(object):
        """ Wrapper around python sub process
        """

        _RESTART_THRESHOLD = 100

        def __init__(self, program):
            self.program = program
            self.restart_count = 0
            self._process = self._start()

        def is_stopped(self):
            """ Check if the process is still running
            """
            if self._process is None:
                return True
            else:
                return self._process.poll() is not None

        def terminate(self):
            """ Stop the process
            """
            if not self.is_stopped():
                self._process.terminate()
                self._process.wait()
            self._process = None

        def _start(self):
            """ Start the process after construction
            """
            return subprocess.Popen(['python', self.program])

        def restart(self):
            """ Restart the process
            """
            if self.restart_count > SubProcess._RESTART_THRESHOLD:
                raise RestartThresholdExceeded(self.restart_count)

            self.terminate()
            self._process = self._start()
            self.restart_count = self.restart_count + 1

        def get_pid(self):
            """ Return the pid of the running process. Returns None if not running.
            """
            if self.is_stopped():
                return None
            return self._process.pid

        def __str__(self):
            pid = self.get_pid()
            result = "[Program "+self.program
            if pid:
                result += " with pid "+str(pid)
            result += "]"
            return result


    def _start_processes(program_list):
        """ Start all python programs and return the pids
        """
        processes = []
        for program in program_list:
            new_subprocess = SubProcess(program)
            processes.append(new_subprocess)
            LOGGER.info("Process %s started", new_subprocess)
        return processes

    def _monitor_processes(processes):
        """ Monitor the process and restart if they die
        """
        if not processes:
            LOGGER.warning("There are no processes to monitor")
            return

        LOGGER.debug("Start monitoring processes (interval %s)", PROCESS_MONITORING_INTERVAL)
        while True:
            for started_process in processes:
                if started_process.is_stopped():
                    LOGGER.warn("Process %s has stopped => restarting", started_process)
                    try:
                        started_process.restart()
                        LOGGER.info("Process %s has restarted", started_process)
                    except RestartThresholdExceeded as exc:
                        LOGGER.error("Process %s was not restarted because number of "+\
                                    "restarts exceeds the threshold %d", \
                                    started_process, exc.restarts)
                        processes.remove(started_process)
            if not processes:
                raise Exception("No more processes to monitor")
            time.sleep(PROCESS_MONITORING_INTERVAL)

    def _stop_alive_processes(processes):
        """ Stop all processes that are alive
        """
        if not processes:
            LOGGER.debug("No processes are alive => nothing to do")
            return
        for started_process in processes:
            if not started_process.is_stopped():
                LOGGER.info("Shutting down process %s", started_process)
                started_process.terminate()

    def _end_program(signum, frame):
        LOGGER.debug("Received termination signal %i", signum)
        _exit_program(0)

    def _exit_program(exit_code):
        if exit_code != 0:
            LOGGER.error("Exiting with error code %d", exit_code)
        else:
            LOGGER.info("Exiting normally")
        _stop_alive_processes(STARTED_PROCESSES)
        exit(exit_code)

    LOGGER.info("Starting program")

    STARTED_PROCESSES = []

    signal.signal(signal.SIGINT, _end_program)
    signal.signal(signal.SIGTERM, _end_program)

    try:
        STARTED_PROCESSES.extend(_start_processes(glob.glob("./publishers/*.py")))
        STARTED_PROCESSES.extend(_start_processes(glob.glob("./subscribers/*.py")))
        LOGGER.debug("Started processes: %s", STARTED_PROCESSES)
        _monitor_processes(STARTED_PROCESSES)
    except Exception:
        LOGGER.error("Exception occurred", exc_info=True)
        _exit_program(1)

