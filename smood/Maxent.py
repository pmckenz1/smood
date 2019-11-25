#!/usr/bin/env python

import os
import subprocess as sps


class Maxent:
    """
    Opens a view to seq-gen in a subprocess so that many gene trees can be
    cycled through without the overhead of opening/closing subprocesses.
    """

    def __init__(self,
                 maxent_path):

        # set binary path for conda env and check for binary
        self.binary = maxent_path
        assert os.path.exists(self.binary), (
            "binary {} not found".format(self.binary))

        # call open_subprocess to set the shell
        self.shell = None

    def open_subprocess(self):
        """
        Open a persistent Popen bash shell
        """
        # open
        self.shell = sps.Popen(
            ["bash"], stdin=sps.PIPE, stdout=sps.PIPE, bufsize=0)

    def close_subprocess(self):
        """
        Cleanup and shutdown the subprocess shell.
        """
        self.shell.stdin.close()
        self.shell.terminate()
        self.shell.wait(timeout=1.0)

    def feed_maxent(self, envfiles_dir, occfile, outputs_dir):
        """
        Feed a command string a read results until empty line.
        TODO: allow kwargs to add additional seq-gen args.
        """
        # command string
        cmd = (
            "java -mx512m -jar {} nowarnings environmentallayers={} samplesfile={} outputdirectory={} redoifexists autorun; echo done\n"
            .format(self.binary, envfiles_dir, occfile, outputs_dir)
        )

        # feed to the shell
        self.shell.stdin.write(cmd.encode())
        self.shell.stdin.flush()

        # catch returned results until done\n
        hold = []
        for line in iter(self.shell.stdout.readline, b"done\n"):
            hold.append(line.decode())
