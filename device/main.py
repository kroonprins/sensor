""" Main entry point for all services running on the device
"""

import glob
import subprocess
import time
import signal

class RestartThresholdExceeded(Exception):
    """ Exception that is raised if a process has been
        restarted more times than the allowed threshold
    """
    def __init__(self):
        Exception.__init__(self)


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
            raise RestartThresholdExceeded()

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


def start_processes(program_list):
    """ Start all python programs and return the pids
    """
    processes = []
    for program in program_list:
        new_subprocess = SubProcess(program)
        processes.append(new_subprocess)
        print str(new_subprocess)+ " Started"
    return processes

def monitor_processes(processes):
    """ Monitor the process and restart if they die
    """
    if not processes:
        print "No processes to monitor..."
        return

    while True:
        for started_process in processes:
            if started_process.is_stopped():
                print str(started_process)+" has stopped => restarting"
                try:
                    started_process.restart()
                    print str(started_process)+" has restarted"
                except RestartThresholdExceeded:
                    print str(started_process)+ " was not restarted because number \
of restarts exceeds the threshold"
                    processes.remove(started_process)
        time.sleep(2)

def stop_alive_processes(processes):
    """ Stop all processes that are alive
    """
    if not processes:
        return
    for started_process in processes:
        if not started_process.is_stopped():
            print str(started_process)+" is shutting down"
            started_process.terminate()

def termination_signal_handler(signum, frame):
    """ Handle termination signal
    """
    print "Received signal to stop the process "+str(signum)
    stop_alive_processes(STARTED_PROCESSES)
    exit(0)

def define_signal_handler():
    """ Setup the handlers for termination signal
    """
    signal.signal(signal.SIGINT, termination_signal_handler)
    signal.signal(signal.SIGTERM, termination_signal_handler)


if __name__ == '__main__':
    STARTED_PROCESSES = []
    define_signal_handler()
    try:
        STARTED_PROCESSES.extend(start_processes(glob.glob("./publishers/*.py")))
        STARTED_PROCESSES.extend(start_processes(glob.glob("./subscribers/*.py")))

        monitor_processes(STARTED_PROCESSES)
    except KeyboardInterrupt:
        pass
    finally:
        stop_alive_processes(STARTED_PROCESSES)
