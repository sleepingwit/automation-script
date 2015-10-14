# -*- coding: utf-8 -*-
import automation
import sys
import os
import os.path


#切换工作目录到当前脚本所在目录
this_module_path = sys.argv[0]
this_module_path = os.path.realpath(os.path.expanduser(this_module_path))
os.chdir(os.path.dirname(this_module_path))

schedule = automation.TaskSchedule("UpdateGameServer", "log/UpdateGameServer.log", "result/UpdateGameServerResult.log")

#删除下载的文件
remove_downloads = automation.actions.RemoveTree()
remove_downloads.target_directory = "downloads/"
remove_downloads.ignore_errors = True
schedule.push_step(remove_downloads)

# 下载压缩包
download_tar = automation.actions.FtpDownload()
download_tar.user = "weilu"
download_tar.password = "123456"
download_tar.hosts = "192.168.0.249"
download_tar.target_file = "release.tar.gz"
download_tar.local_file = "downloads/"
schedule.push_step(download_tar)

# 下载校验文件
download_sha512 = automation.actions.FtpDownload()
download_sha512.user = "weilu"
download_sha512.password = "123456"
download_sha512.hosts = "192.168.0.249"
download_sha512.target_file = "release.tar.sha512"
download_sha512.local_file = "downloads/"
schedule.push_step(download_sha512)

# 校验压缩包
sha512sum = automation.actions.Sha512Sum()
sha512sum.summarizing_mode = automation.actions.SummarizingMode.check
sha512sum.summarizing_file = "downloads/release.tar.sha512"
schedule.push_step(sha512sum)

# 删除遗留的文件
# remove_tree = automation.actions.RemoveTree()
# remove_tree.target_directory = "downloads/GameServer"
# remove_tree.ignore_errors = True
# schedule.push_step(remove_tree)

# 解压压缩包
extractArchive = automation.actions.ArchiveFile()
extractArchive.archive_file = "downloads/release.tar.gz"
extractArchive.archive_mode = automation.actions.ArchiveMode.extract
extractArchive.compress_mode = automation.actions.CompressMode.gzip
schedule.push_step(extractArchive)

# 复制到指定目录
copy_tree = automation.actions.CopyTree()
copy_tree.source_directory = "downloads/release"
copy_tree.target_directory = "/home/weilu/RealGameServer"
schedule.push_step(copy_tree)

schedule.run()
