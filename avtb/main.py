import logging

import time
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import operator
import traceback
from avtb import get_all_video_from_url, get_video_download_link, HOST, add_one_line_to_file, download

from MainWindow import Ui_MainWindow

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='log.log',
                    filemode='w')
"""
选择输入文件
开始
查看结果输出
记录日志
"""


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        # 一些参数
        root_path = os.path.dirname(os.path.abspath(__file__))
        self.input_data_path = default_input_data_path = os.path.join(root_path)

        # 设置默认值
        self.textEdit.setText(default_input_data_path)

        # 绑定事件
        self.btn_start.pressed.connect(self.start_search_balance)
        self.btn_select.pressed.connect(self.showDialog)

        self.show()

    def start_search_balance(self):
        # 重置
        self.progressBar.setValue(0)
        self.textBrowser.append('-'*40)
        self.textBrowser.append('')

        starttime = time.time()
        # 页码
        page_start = int(self.textEdit_3.toPlainText())
        page_end = int(self.textEdit_4.toPlainText())
        output_filename = self.textEdit_2.toPlainText()

        self.total = page_end - page_start + 1
        count = 0
        results = []

        _module = 'guochan'

        # 爬取每一页
        url = 'http://www.avtb008.com/{module}/{page}/'
        for page in range(page_start, page_end + 1):
            try:
                # 下载每一个
                if page == 1:
                    page = ''
                else:
                    page = 'recent/{}/'.format(page)
                for title, u, thumb in get_all_video_from_url(url.format(module=_module, page=page)):
                    try:
                        download_link = get_video_download_link(''.join((HOST, u)))
                        if output_filename:
                            add_one_line_to_file(os.path.join(self.input_data_path, output_filename), download_link)
                        else:
                            download(download_link, 'videos/{}.mp4'.format(title))
                    except Exception as e:
                        print(e)
                    self.textBrowser.append('%s >>> %s' % (title, output_filename))
                    QApplication.processEvents()
            except Exception as e:
                logging.error(traceback.format_exc())
            count += 1
            self.progressBar.setValue(count * 100.0 / self.total)
            QApplication.processEvents()
        self.textBrowser.append('完成! 用时: {}s'.format(time.time() - starttime))

    def showDialog(self):
        self.input_data_path, _ = QFileDialog.getOpenFileName(self, '选择文件', './')
        if self.input_data_path:
            self.textEdit.setText(self.input_data_path)
        else:
            self.textBrowser.append('请选择文件!!!')


if __name__ == '__main__':
    try:
        app = QApplication([])
        app.setApplicationName("Vivo")

        window = MainWindow()
        app.exec_()
    except Exception as e:
        print(e)