# -*- coding: utf-8 -*-
from abc import *
from collections import deque
import logging
import logging.handlers
import os
import os.path
import shutil

class TaskExecuteResult:
    success = 1
    failed = 0


class Task:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.task_name = "undefined"

    def run(self, logger):
        if not self._parse_settings(logger):
            return TaskExecuteResult.failed
        else:
            return self._execute(logger)

    @abstractmethod
    def _execute(self, logger):
        raise NotImplementedError

    @abstractmethod
    def _parse_settings(self, logger):
        raise NotImplementedError


class TaskSchedule:
    success_end = "TaskSchedule Run Success"
    failed_end = "TaskSchedule Run Failed"

    def __init__(self, name, log_file, result_file, log_level=logging.DEBUG):
        self.name = name
        self.__task_deque = deque()
        log_file = os.path.abspath(os.path.expanduser(log_file))
        dir_name = os.path.dirname(log_file)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        self.logger = logging.getLogger(self.name)

        formatter = logging.Formatter(fmt="%(asctime)s\t%(levelname)s\t%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        file_handler = logging.FileHandler(log_file, 'w', 'utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(log_level)
        self.logger.addHandler(stream_handler)

        self.logger.setLevel(log_level)

        result_file = os.path.abspath(os.path.expanduser(result_file))
        result_dir_name = os.path.dirname(result_file)
        if not os.path.exists(result_dir_name):
            os.makedirs(result_dir_name)
        if os.path.exists(result_file):
            os.remove(result_file)
        self.log_formatter = formatter
        self.result_file = result_file

    def run(self):
        self.logger.debug("Start Run")
        ret = True
        number = 0
        for task in self.__task_deque:
            number += 1

            try:
                self.logger.info(">>>>> Task [%d] [%s] executing" % (number, task.task_name))
                task_ret = task.run(self.logger)
                self.logger.info("<<<<< Task [%d] [%s] executed" % (number, task.task_name))
                self.logger.info("")
            except Exception as ex:
                self.logger.fatal(ex)
                ret = False
                break

            if task_ret != TaskExecuteResult.success:
                ret = False
                break

        if ret:
            self.logger.info(self.success_end)
            self.__log_result(self.success_end)
        else:
            self.logger.error(self.failed_end)
            self.__log_result(self.failed_end)

    def __log_result(self, result):
        logger = logging.getLogger(self.name + "_result")
        file_handler = logging.FileHandler(self.result_file, 'w', 'utf-8')
        file_handler.setFormatter(self.log_formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        logger.info(result)

    def push_step(self, step):
        self.__task_deque.append(step)
        return step

