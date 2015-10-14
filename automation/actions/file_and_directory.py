# -*- coding: utf-8 -*-
from ..task import Task, TaskExecuteResult
import os
import os.path
import shutil


class CopyTree(Task):
    task_name = "CopyTree"

    def __init__(self):
        self.source_directory = ""
        self.target_directory = ""

    def _parse_settings(self, logger):
        if len(self.source_directory) <= 0:
            logger.error("Invalid source directory")
            return False
        if len(self.target_directory) <= 0:
            logger.error("Invalid target directory")
            return False

        self.source_directory = os.path.abspath(os.path.expanduser(self.source_directory))
        self.target_directory = os.path.abspath(os.path.expanduser(self.target_directory))
        if self.source_directory == self.target_directory:
            logger.error("Same directory")
            return False
        logger.info("Source directory = %s" % self.source_directory)
        logger.info("Target directory = %s" % self.target_directory)
        return True

    def _execute(self, logger):
        self.__logger = logger
        self.__files_copied = 0
        self.__copy_tree(self.source_directory, self.target_directory, copy_function=self.__copy)
        logger.info("%d files total copied" % self.__files_copied)
        return TaskExecuteResult.success

    def __copy(self, src, dst):
        shutil.copy2(src, dst)
        self.__logger.info("Copied:  %s" % dst)
        self.__files_copied += 1

    def __copy_tree(self, src, dst, symlinks=False, ignore=None,
                    copy_function=shutil.copy2, ignore_dangling_symlinks=False):
        # shutil.copytree 函数复制了一份，做了点小修改，创建dst目录的时候如果已经存在不抛异常
        names = os.listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()

        # 这里是修改的地方
        if not os.path.exists(dst):
            os.makedirs(dst)

        errors = []
        for name in names:
            if name in ignored_names:
                continue
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    if symlinks:
                        # We can't just leave it to `copy_function` because legacy
                        # code with a custom `copy_function` may rely on copytree
                        # doing the right thing.
                        os.symlink(linkto, dstname)
                        shutil.copystat(srcname, dstname, follow_symlinks=not symlinks)
                    else:
                        # ignore dangling symlink if the flag is on
                        if not os.path.exists(linkto) and ignore_dangling_symlinks:
                            continue
                        # otherwise let the copy occurs. copy2 will raise an error
                        copy_function(srcname, dstname)
                elif os.path.isdir(srcname):
                    # 递归调用修改版本的copytree
                    self.__copy_tree(srcname, dstname, symlinks, ignore, copy_function)
                else:
                    # Will raise a SpecialFileError for unsupported file types
                    copy_function(srcname, dstname)
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except shutil.Error as err:
                errors.extend(err.args[0])
            except OSError as why:
                errors.append((srcname, dstname, str(why)))
        try:
            shutil.copystat(src, dst)
        except OSError as why:
            # Copying file access times may fail on Windows
            if why.winerror is None:
                errors.append((src, dst, str(why)))
        if errors:
            raise shutil.Error(errors)
        return dst


class RemoveTree(Task):
    task_name = "RemoveTree"

    def __init__(self):
        self.target_directory = ""
        self.ignore_errors = False

    def _parse_settings(self, logger):
        if len(self.target_directory) <= 0:
            logger.error("Invalid target directory")
            return False
        self.target_directory = os.path.abspath(os.path.expanduser(self.target_directory))
        logger.info("Target directory = %s" % self.target_directory)
        return True

    def _execute(self, logger):
        shutil.rmtree(self.target_directory, ignore_errors=self.ignore_errors)
        return TaskExecuteResult.success

