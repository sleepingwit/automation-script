# -*- coding: utf-8 -*-
from automation.task import *
import os.path


class SummarizingMode:
    # 生成校验文件
    summarizing = 0,
    # 校验文件
    check = 1


class Sha512Sum(Task):
    task_name = "Sha512Sum"
    __execute_command = "sha512sum"

    def __init__(self):
        self.summarizing_mode = SummarizingMode.check
        self.summarizing_file = ""
        self.target_file = ""

    def _parse_settings(self, logger):
        if self.summarizing_mode == SummarizingMode.summarizing:
            raise NotImplementedError
            self.__command = "%s %s > %s" % (Sha512Sum.__execute_command, self.target_file, self.summarizing_file)
        elif self.summarizing_mode == SummarizingMode.check:
            if len(self.summarizing_file) <= 0:
                logger.error("Invalid summarizing file path")
                return False
            self.summarizing_file = os.path.abspath(self.summarizing_file)
            if not os.path.exists(self.summarizing_file) or not os.path.isfile(self.summarizing_file):
                return False
            logger.info("Summarizing mode = check")
            logger.info("Summarizing file = %s" % self.summarizing_file)
            self.__command = "%s -c %s" % (Sha512Sum.__execute_command, self.summarizing_file)
            return True
        else:
            return False

    def _execute(self, logger):
        cwd = os.getcwd()
        wd = os.path.dirname(self.summarizing_file)
        logger.info("Changing working directory to %s" % wd)
        os.chdir(wd)
        ret = os.system(self.__command)
        logger.info("Changing working directory to %s" % cwd)
        os.chdir(cwd)
        if ret == 0:
            return TaskExecuteResult.success
        else:
            return TaskExecuteResult.failed

