from multiprocessing import Pool
import logging
import subprocess
import time


def callable(command):
    try:
        # logging.info(f"Command {command}")
        time_before = time.time()
        output = subprocess.run(command, capture_output=True, check=True)
        time_taken = (time.time() - time_before)

        # logging.info(f"Time taken for command: {time_taken}")
        return output, time_taken
    except subprocess.CalledProcessError as e:
        if e.stdout:
            logging.error(f"STDOUT: Error during invocation: {e.stdout}")
        if e.stderr:
            logging.error(f"STDERR: Error during invocation: {e.stderr}")


def default_error_callback(self, error):
    logging.error(error)
