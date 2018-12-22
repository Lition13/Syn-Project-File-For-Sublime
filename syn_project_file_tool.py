import os
import sys
import shutil
import sublime
import sublime_plugin

# 文件信息列表
FILE_INFO = {}

# 项目根目录
PROJECT_ROOT = ""

# 当前 Windows 系统上操作的根目录 
SRC_ROOT = ""

# 目标根目录
DEST_ROOT = ""

# 项目文件信息
PROJECT_FILES = {}

# 加载 Preferences 配置
SETTINGS = sublime.load_settings('SynProjectFileTool.sublime-settings')

def Init():
	# 初始化配置信息
	settings = sublime.load_settings('Preferences.sublime-settings')
	SRC_ROOT = settings.get("syf_src_root", SETTINGS.get("syf_src_root", ""))
	PROJECT_ROOT = settings.get("syf_project_root", SETTINGS.get("syf_project_root", ""))
	DEST_ROOT = settings.get("syf_dest_root", SETTINGS.get("syf_dest_root", ""))

	for root , dirs, files in os.walk(SRC_ROOT):
		for name in files:
			temp_path = os.path.join(root, name)
			file_time = os.stat(temp_path).st_mtime  # 获取最后修改时间
			PROJECT_FILES[temp_path] = file_time

# 拷贝文件
def move_file(fill_path):
	# 判断是否为理想的文件
	if fill_path.find(PROJECT_ROOT) == -1:
		return
	file_tail = fill_path[fill_path.find(PROJECT_ROOT) + len(PROJECT_ROOT):]
	# sublime.message_dialog(file_tail)
	if FILE_INFO.get(fill_path) == None or FILE_INFO[fill_path] == True :
		if not os.path.exists(DEST_ROOT+file_tail):
			sublime.error_message("move fail, file: %s" % fill_path)
		# sublime.message_dialog(DEST_ROOT+file_tail)
		shutil.copyfile(fill_path, DEST_ROOT + file_tail)          #移动文件
		FILE_INFO[fill_path] = False


# 展示文件列表
def show_file():
	msg_list = list()
	for fill_path, value in FILE_INFO.items():
		file_tail = fill_path[fill_path.find(PROJECT_ROOT) + len(PROJECT_ROOT):]
		msg_list.append("%s: %s" % (file_tail, value))
	sublime.message_dialog("\n\n".join(msg_list))


def is_filter_file(file_name):
	filter_words = [".pyc", "~$"]
	for word in filter_words:
		if file_name.find(word) != -1:
			return True

	return False


def check_file_change():
	for root , dirs, files in os.walk(SRC_ROOT):
		for name in files:
			temp_path = os.path.join(root, name)
			file_time = os.stat(temp_path).st_mtime  # 获取最后修改时间

			if is_filter_file(name) == True : # 过滤文件
				continue

			if PROJECT_FILES.get(temp_path) :
				if PROJECT_FILES[temp_path] != file_time : # 有修改的文件
					# isSkip = True
					FILE_INFO[temp_path] = True
					PROJECT_FILES[temp_path] = file_time
					# sublime.message_dialog("Update, %s:%s:%s|%s" % (temp_path, PROJECT_FILES[temp_path], FILE_INFO.get(temp_path), file_time))
			else: # 新增的文件
				# sublime.message_dialog("New, %s:%s:%s|%s" % (temp_path, PROJECT_FILES.get(temp_path), FILE_INFO.get(temp_path), file_time))
				FILE_INFO[temp_path] = True
				PROJECT_FILES[temp_path] = file_time


class MoveSpecFile(sublime_plugin.EventListener):
	# 该方法用于监听修改文件时将文件加入文件列表
	def on_modified(self, view):
		if view.file_name() == None:
			return
		
		# 判断当前修改的文件是否为当前 Windows 系统上操作的根目录的文件
		if view.file_name().find(SRC_ROOT) == -1:
			return

		# 将文件存入文件列表中进行管理
		if not FILE_INFO.get(view.file_name()):
			FILE_INFO[view.file_name()] = True
		FILE_INFO[view.file_name()] = True


	# 该方法用于监听保存时移动文件 
	# def on_post_save(self, view):
	# 	move_file(view.file_name())  



class MoveFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		msg_list = list()
		for fill_path, value in FILE_INFO.items():
			if value == True:
				move_file(fill_path)
				msg_list.append(fill_path)
		sublime.message_dialog("\n\n".join(msg_list))
		FILE_INFO.clear()



class ShowFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		show_file()



class ClearFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		show_file()
		FILE_INFO.clear()


class ClearSpecFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.file_list = list()
		for fill_path, value in FILE_INFO.items():
			if value == True :
				self.file_list.append(fill_path)

		window = sublime.active_window()
		if window:
			window.show_quick_panel(self.file_list, self.on_done)



	def on_done(self, selected):
		if selected != -1 :
			FILE_INFO[self.file_list[selected]] = False


class MoveSpecFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.file_list = list()
		for fill_path, value in FILE_INFO.items():
			if value == True :
				self.file_list.append(fill_path)

		window = sublime.active_window()
		if window:
			window.show_quick_panel(self.file_list, self.on_done)



	def on_done(self, selected):
		if selected != -1 :
			msg_list = list()
			move_file(self.file_list[selected])
			msg_list.append(self.file_list[selected])
			sublime.message_dialog("\n\n".join(msg_list))
			FILE_INFO[self.file_list[selected]] = False



init()

def delay():
	check_file_change()
	sublime.set_timeout_async(lambda:delay(), DELAY_TIME * 1000)


DELAY_TIME = 1
sublime.set_timeout_async(lambda:delay(), DELAY_TIME * 1000)