# -*- coding: utf-8 -*-
from ..task import *
import os.path


class CompressMode:
    non_compress = 0,
    gzip = 1,
    bzip = 2


class ArchiveMode:
    undefined = -1,
    create = 0,
    extract = 1


class ArchiveFile(Task):
    task_name = "ArchiveFile"
    __execute_command = "tar"

    def __init__(self):
        self.archive_mode = ArchiveMode.undefined
        self.compress_mode = CompressMode.non_compress
        self.archive_file = ""
        self.target_file = ""

    def _parse_settings(self, logger):

        compress_op = ""
        if self.compress_mode == CompressMode.non_compress:
            pass
        elif self.compress_mode == CompressMode.gzip:
            compress_op = "z"
        elif self.compress_mode == CompressMode.bzip:
            compress_op = "j"
        else:
            return False

        if len(self.archive_file) <= 0:
            logger.error("Invalid archive_file")
            return False
        self.archive_file = os.path.abspath(os.path.expanduser(self.archive_file))

        if self.archive_mode == ArchiveMode.create:
            raise NotImplementedError
        elif self.archive_mode == ArchiveMode.extract:
            self.__command = "".join([ArchiveFile.__execute_command, " -", compress_op, "xf ", self.archive_file])

        else:
            return False

        dir_name = os.path.dirname(self.archive_file)
        self.__command = "".join([self.__command, " -C %s" % dir_name])
        logger.info("Command = %s" % self.__command)
        return True

    def _execute(self, logger):
        if os.system(self.__command) == 0:
            return TaskExecuteResult.success
        else:
            return TaskExecuteResult.failed
