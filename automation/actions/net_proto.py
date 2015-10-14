# -*- coding: utf-8 -*-
from ..task import Task, TaskExecuteResult
from ftplib import FTP
import os
import os.path
import shutil


class FtpDownload(Task):

    def __init__(self):
        self.task_name = "FtpDownload"
        self.hosts = "127.0.0.1"
        self.user = "user"
        self.password = "passwd"
        self.target_file = ""
        self.local_file = ""

    def _parse_settings(self, logger):
        logger.info("hosts = %s" % self.hosts)
        logger.info("user = %s" % self.user)
        logger.info("password = %s" % self.password)
        if len(self.target_file) <= 0:
            logger.error("Target file is empty.")
            return False

        target_file_name = os.path.basename(self.target_file)
        if len(target_file_name) <= 0:
            logger.error("Invalid target file name.")
            return False

        if len(self.local_file) > 0:
            self.local_file = os.path.expanduser(self.local_file)
            dir_name = os.path.dirname(self.local_file)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            file_name = os.path.basename(self.local_file)
            if len(file_name) <= 0:
                self.local_file = os.path.join(dir_name, target_file_name)
        else:
            self.local_file = os.path.join(os.getcwd(), target_file_name)

        self.local_file = os.path.abspath(self.local_file)
        logger.info("Target file: %s" % self.target_file)
        logger.info("Local file: %s" % self.local_file)
        return True

    def _execute(self, logger):
        logger.info("FtpDownload start execute")

        if len(self.target_file) > 0 and len(self.local_file) > 0:
            ftp = FTP()
            ftp.connect(host=self.hosts, timeout=10)
            ftp.login(self.user, self.password)
            cmd = "RETR %s" % self.target_file
            local_file = open(self.local_file, "wb")
            ftp.retrbinary(cmd, local_file.write)
            local_file.close()
            logger.info("FtpDownload Success")
            ftp.close()
            return TaskExecuteResult.success
        else:
            logger.error("Invalid settings")
            return TaskExecuteResult.failed
