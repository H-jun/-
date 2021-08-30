from PySide2.QtWidgets import QApplication, QMessageBox, QFileDialog, QMainWindow
from PySide2.QtUiTools import QUiLoader
import time
import subprocess
import os, sys
import shutil
import cv2
import weblfasr
import re
from threading import Thread
from PySide2.QtGui import QColor

# api = weblfasr.RequestApi(appid="26e457a3", secret_key="868f2a7fd824e25d5c58e7bdbfacd028", upload_file_path=r"E:/bb.mp3")
# api.all_api_request()

class Stats:

    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load('ui/01.ui')
        self.ui.SelectMusic.clicked.connect(self.selectMusicFile)
        # 批量剪辑下的选择视频
        self.ui.SelectVideo.clicked.connect(self.selectVideoFile)
        # 批量剪辑下的选择文件夹
        self.ui.SelectDir.clicked.connect(self.select_output_path)
        # 获取视频变速滑块值
        self.ui.VideoSpeed.valueChanged.connect(self.speed_slider)
        # 获取色调滑块值
        # self.ui.ToneSlider.valueChanged.connect(self.tone_slider)
        # 获取饱和度滑块值
        self.ui.SaturationSlider.valueChanged.connect(self.saturation_slider)
        # 获取亮度滑块值
        self.ui.BrightnessSlider.valueChanged.connect(self.brightness_slider)
        # 获取对比度滑块值
        self.ui.ContrastSlider.valueChanged.connect(self.contrast_slider)
        # 获取红滑块值
        self.ui.RedSlider.valueChanged.connect(self.red_slider)
        # 获取绿滑块值
        self.ui.GreenSlider.valueChanged.connect(self.green_slider)
        # 获取蓝滑块值
        self.ui.BlueSlider.valueChanged.connect(self.blue_slider)
        # 导出视频
        self.ui.StartOutput.clicked.connect(self.start_output)

        '''视频分割'''
        # 选择视频
        self.ui.CutSelectVideo.clicked.connect(self.split_select_video)
        # 选择导出路径
        self.ui.pushButton_44.clicked.connect(self.split_select_output_path)
        # 开始导出
        self.ui.pushButton_45.clicked.connect(self.export_split_video)

        '''语音识别'''
        # 选择音频
        self.ui.pushButton_53.clicked.connect(self.select_audio_file)
        # 选择导出文件夹
        self.ui.pushButton_54.clicked.connect(self.audio_select_output_path)
        # 开始识别
        self.ui.pushButton_55.clicked.connect(self.ocr_media)

        '''视频裁剪去水印'''
        # 选择视频
        self.ui.pushButton_12.clicked.connect(self.cut_select_video)
        # 输出路径
        self.ui.pushButton_2.clicked.connect(self.cut_outdir)
        # 开始处理
        self.ui.pushButton_11.clicked.connect(self.cut_start)


    # 设置日志输出函数
    def logging_print(self,logging):
        self.ui.textEdit.append(logging)
        QApplication.processEvents()
        time.sleep(0.2)



    # 选择文件夹
    def selectFolder(self):
        MainWindow = QMainWindow()
        FileDialog = QFileDialog(MainWindow)
        FileDirectory = FileDialog.getExistingDirectory(MainWindow, "导出路径")  # 选择目录，返回选中的路径

    # 选择背景音乐文件
    def selectMusicFile(self):
        MainWindow = QMainWindow()

        FileDialog = QFileDialog(MainWindow)
        FileDirectory = \
        FileDialog.getOpenFileName(MainWindow, "选择音乐文件", "", "Video files (*.mp3 *.flac *.mwa *.wav *.w4a)")[0]

        self.ui.AudioFile.setText(FileDirectory)

    '''批量剪辑'''

    # 选择视频文件
    def selectVideoFile(self):
        MainWindow = QMainWindow()

        FileDialog = QFileDialog(MainWindow)
        FileDirectory = \
        FileDialog.getOpenFileNames(MainWindow, "选择视频文件", "", "Video files (*.mp4 *.m4v *.wmv *.mkv *.avi *.mov)")[0]
        self.paths = FileDirectory
        FileDirectory = str(FileDirectory)
        self.ui.lineEdit_81.setText(FileDirectory)

    # 变速滑块
    def speed_slider(self):
        # 获取批量剪辑下的参数数值
        video_speed = self.ui.VideoSpeed.value() / 10
        self.ui.speedValue.setText(str(video_speed))

    # #色调滑块
    # def tone_slider(self):
    #     tone_value=self.ui.ToneSlider.value()
    #     self.ui.ToneValue.setText(str(tone_value))

    # 饱和度滑块
    def saturation_slider(self):
        saturation_value = self.ui.SaturationSlider.value() / 10
        self.ui.SaturationValue.setText(str(saturation_value))

    # 明度滑块
    def brightness_slider(self):
        brightness_value = self.ui.BrightnessSlider.value() / 10
        self.ui.BrightnessValue.setText(str(brightness_value))

    # 对比度滑块
    def contrast_slider(self):
        contrast_value = self.ui.ContrastSlider.value() / 10
        self.ui.ContrastValue.setText(str(contrast_value))

    # 红
    def red_slider(self):
        red_value = self.ui.RedSlider.value() / 10
        self.ui.RedValue.setText(str(red_value))

    # 绿
    def green_slider(self):
        green_value = self.ui.GreenSlider.value() / 10
        self.ui.GreenValue.setText(str(green_value))

    # 蓝
    def blue_slider(self):
        blue_value = self.ui.BlueSlider.value() / 10
        self.ui.BlueValue.setText(str(blue_value))

    # 选择导出路径
    def select_output_path(self):
        MainWindow = QMainWindow()
        FileDialog = QFileDialog(MainWindow)
        FileDirectory = FileDialog.getExistingDirectory(MainWindow, "选择导出路径")
        self.ui.outpathEdit.setText(FileDirectory)

    # 导出视频添加多线程，防止阻塞
    def start_output(self):
        thread=Thread(target=self.start_output_thread,args=())
        thread.start()

    # 导出视频
    def start_output_thread(self):
        self.ui.StartOutput.setEnabled(False)
        # 选择路径
        video_path = self.ui.lineEdit_81.text()
        video_path = eval(video_path)
        # print(video_path)

        # 视频速度
        video_speed = self.ui.speedValue.text()
        # print(video_speed)

        # 饱和度
        saturation_value = self.ui.SaturationValue.text()
        # print(saturation_value)

        # 亮度
        bright_value = self.ui.BrightnessValue.text()
        # print(bright_value)

        # 对比度
        contrast_value = self.ui.ContrastValue.text()
        # print(contrast_value)

        # 红色
        red_value = self.ui.RedValue.text()
        # print(red_value)

        # 绿色
        green_value = self.ui.GreenValue.text()
        # print(green_value)

        # 蓝色
        blue_value = self.ui.BlueValue.text()
        # print(blue_value)

        # 输出路径
        output_path = self.ui.outpathEdit.text()
        # print(output_path)

        if not os.path.exists('./过渡/'):
            os.mkdir('./过渡/')
        self.logging_print('开始批量剪辑，请稍后...')
        for srcpath in video_path:
            # 输出文件名
            # print('srcpath:'+srcpath)
            output_name = srcpath.split('/')[-1]
            self.logging_print(output_name+" 正在处理...")
            # print('output_name:'+output_name)
            # "ffmpeg -i 0001.mp4 -vf eq=contrast=2.0:brightness=0:saturation=1:gamma_r=1:gamma_g=1:gamma_b=1 -b 600k C:\Users\hdsha\Desktop\音视频\mp4\测试\eqc41.mp4"
            cmd_color = 'ffmpeg -y -i '+'"' + srcpath +'"'+ ' -vf eq=contrast=' + contrast_value + ":brightness=" + bright_value + ':saturation=' + saturation_value + ':gamma_r=' + red_value + ':gamma_g=' + green_value + ':gamma_b=' + blue_value + ' -b 600k ' + '"'+'./过渡/' + output_name+'"'
            print(cmd_color)
            subprocess.call(cmd_color, shell=True)
            cmd_speed = 'ffmpeg -y -i '+'"'  + './过渡/' + output_name + '"' +' -filter_complex "[0:v]setpts=' + str(
                1 / float(
                    video_speed)) + '*PTS[v];[0:a]atempo=' + video_speed + '[a]" -map "[v]" -map "[a]"  '+'"'+ output_path + '/' + output_name+'"'
            print(cmd_speed)
            subprocess.call(cmd_speed, shell=True)

            self.logging_print(output_name + " 处理完成！！！")
        shutil.rmtree("./过渡/")
        self.ui.StartOutput.setEnabled(True)

    '''视频分割'''

    # 选择视频
    def split_select_video(self):
        MainWindow = QMainWindow()

        FileDialog = QFileDialog(MainWindow)
        FileDirectory = \
        FileDialog.getOpenFileNames(MainWindow, "选择视频文件", "", "Video files (*.mp4 *.m4v *.wmv *.mkv *.avi *.mov)")[0]
        self.paths = FileDirectory
        FileDirectory = str(FileDirectory)
        self.ui.lineEdit_75.setText(FileDirectory)

    # 选择文件夹
    def split_select_output_path(self):
        MainWindow = QMainWindow()
        FileDialog = QFileDialog(MainWindow)
        FileDirectory = FileDialog.getExistingDirectory(MainWindow, "选择导出路径")
        self.ui.lineEdit_78.setText(FileDirectory)

    # 导出视频添加多线程，防止阻塞
    def export_split_video(self):
        thread = Thread(target=self.export_split_video_thread, args=())
        thread.start()

    # 视频分割开始导出
    def export_split_video_thread(self):
        self.ui.pushButton_45.setEnabled(False)
        # 选择原视频
        src_videos = self.ui.lineEdit_75.text()
        src_videos=eval(src_videos)

        # 每段时长
        durtation_time=self.ui.lineEdit_79.text()
        # 结束时间
        end_time=self.ui.lineEdit_77.text()
        # end_hour = int(end_time) // 3600
        # end_minute = (int(end_time) - end_hour * 3600) // 60
        # end_second = int(end_time) % 60
        # end_time_format = '{:0>2d}:{:0>2d}:{:0>2d}'.format(end_hour, end_minute, end_second)
        # 截取段数
        cut_count_str=self.ui.lineEdit_80.text()
        # 是否保留不足规定时长的部分
        isremain = self.ui.radioButton_41.isChecked()
        # 导出路径
        export_path=self.ui.lineEdit_78.text()


        for src_video in src_videos:
            self.logging_print(src_video+" 开始分割...")
            # 获取开始时间
            start_time = self.ui.lineEdit_76.text()
            # 获取视频时长
            result=cv2.VideoCapture(src_video)
            rate=result.get(5)
            fraNum=result.get(7)
            durtation=fraNum/rate
            # 如果截取段数为-1，那么截取段数=视频时长//每段时长，也就是全部截取
            if cut_count_str=="-1":
                cut_count=(durtation-int(start_time)-int(end_time))//int(durtation_time)
            else:
                cut_count=int(cut_count_str)
            # print(durtation)
            # print('start_time:',start_time,'cut_count:',cut_count,'durtation_time:',durtation_time,'end_time:',end_time)
            # print(int(start_time)+int(cut_count)*int(durtation_time)+int(end_time))
            if durtation > int(start_time)+int(cut_count)*int(durtation_time)+int(end_time):

                for i in range(int(cut_count)):
                    if i==0:
                        start_time=int(start_time)
                    else:
                        start_time=int(start_time)+int(durtation_time)

                    index=i
                    start_hour = start_time // 3600
                    start_minute = (start_time - start_hour * 3600) // 60
                    start_second = start_time % 60
                    start_time_format = '{:0>2d}:{:0>2d}:{:0>2d}'.format(start_hour, start_minute, start_second)

                    # 导出文件名
                    export_name = src_video.split("/")[-1]
                    export_name=export_name.split(".")[0]+str(index)+'.'+export_name.split(".")[1]
                    cmd='ffmpeg -y -loglevel quiet -ss '+start_time_format+' -i '+'"'+src_video+'"'+' -c copy -t '+durtation_time +' '+'"'+ export_path+'/'+export_name+'"'
                    subprocess.call(cmd, shell=True)
                    self.logging_print(export_name+" 完成！")

                    # print(cmd)
                if isremain:
                    end_durtation=int(durtation)-int(end_time)-int(durtation_time)-start_time
                    start_time=int(durtation_time)+start_time
                    start_hour = start_time // 3600
                    start_minute = (start_time - start_hour * 3600) // 60
                    start_second = start_time % 60
                    start_time_format = '{:0>2d}:{:0>2d}:{:0>2d}'.format(start_hour, start_minute, start_second)
                    # 导出文件名
                    index += 1
                    export_name = src_video.split("/")[-1]
                    export_name = export_name.split(".")[0] + str(index) + '.' + export_name.split(".")[1]
                    cmd = 'ffmpeg -y -loglevel quiet -ss ' + start_time_format + ' -i ' +'"'+ src_video +'"'+ ' -c copy -t ' + str(end_durtation) + ' ' +'"'+ export_path + '/' + export_name+'"'
                    subprocess.call(cmd, shell=True)
                    self.logging_print(export_name + " 完成！")

            else:
                print(src_video+" 视频时长不足，请重新设置！")
                self.logging_print(src_video+" 视频时长不足，请重新设置！")
                continue
            self.logging_print(src_video + " 完成分割！！")
            self.ui.pushButton_45.setEnabled(True)

    '''语音识别'''
    # 选择语音文件
    def select_audio_file(self):
        MainWindow = QMainWindow()

        FileDialog = QFileDialog(MainWindow)
        FileDirectory = \
        FileDialog.getOpenFileNames(MainWindow, "选择音频文件", "",
                                        "Audio files (*.mp3 *.m4a *.wav)")[0]
        self.paths = FileDirectory
        FileDirectory = str(FileDirectory)
        self.ui.lineEdit_88.setText(FileDirectory)

    # 选择导出文件夹
    def audio_select_output_path(self):
        MainWindow = QMainWindow()
        FileDialog = QFileDialog(MainWindow)
        FileDirectory = FileDialog.getExistingDirectory(MainWindow, "选择导出路径")
        self.ui.lineEdit_92.setText(FileDirectory)

    # 语音识别添加多线程，防止阻塞
    def ocr_media(self):
        thread = Thread(target=self.ocr_media_thread, args=())
        thread.start()

    #开始识别
    def ocr_media_thread(self):
        self.ui.pushButton_55.setEnabled(False)
        # 选择文件
        audio_files = self.ui.lineEdit_88.text()
        audio_files=eval(audio_files)
        # 腾讯APPID
        tx_appid = self.ui.lineEdit_89.text()
        # 腾讯SecretID
        # tx_secretid = self.ui.lineEdit_90.text()
        # 腾讯SecretKey
        tx_secretkey = self.ui.lineEdit_91.text()
        # 选择导出文件夹
        ocr_output_dir = self.ui.lineEdit_92.text()
        for audio_file in audio_files:
            audio_name=audio_file.split('/')[-1]
            self.logging_print(audio_name+" 开始识别语音文字...该功能时间较长，请稍后...")
            audio_name=audio_name.split('.')[0]
            api = weblfasr.RequestApi(appid=tx_appid, secret_key=tx_secretkey,
                                      upload_file_path=audio_file)
            api.all_api_request()
            aa_data=open('aa.txt','rb').read()
            aa_data=aa_data.decode()
            print(aa_data)
            text_lists=re.findall('onebest":"(.*?)"',aa_data)
            write_path=ocr_output_dir+'/'+audio_name+'.txt'
            print(write_path)
            with open(write_path,'w',encoding='utf-8') as fp:
                for text_list in text_lists:
                    fp.write(text_list)
                self.logging_print(write_path+" 写入完成！！！")
        self.ui.pushButton_55.setEnabled(True)
    '''视频裁剪去水印'''
    # 选择视频
    def cut_select_video(self):
        MainWindow = QMainWindow()

        FileDialog = QFileDialog(MainWindow)
        FileDirectory = \
        FileDialog.getOpenFileNames(MainWindow, "选择视频文件", "", "Video files (*.mp4 *.m4v *.wmv *.mkv *.avi *.mov)")[0]
        self.paths = FileDirectory
        FileDirectory = str(FileDirectory)
        self.ui.lineEdit_6.setText(FileDirectory)

    # 选择输出文件夹
    def cut_outdir(self):
        MainWindow = QMainWindow()
        FileDialog = QFileDialog(MainWindow)
        FileDirectory = FileDialog.getExistingDirectory(MainWindow, "选择导出路径")
        self.ui.lineEdit_5.setText(FileDirectory)

    # 开始处理添加多线程，防止阻塞
    def cut_start(self):
        thread = Thread(target=self.cut_start_thread, args=())
        thread.start()

    # 开始处理
    def cut_start_thread(self):
        # 是否视频倒放
        is_reverse=self.ui.checkBox_4.isChecked()
        # 是否去水印
        is_unwatermark=self.ui.checkBox_5.isChecked()
        # 是否视频裁剪
        is_cutting=self.ui.checkBox_6.isChecked()
        # 获取视频列表
        video_list=self.ui.lineEdit_6.text()
        video_list=eval(video_list)
        # 如果视频列表已选择，则开始以下处理
        if video_list:
            for video in video_list:
                if not os.path.exists('./复制'):
                    os.mkdir('./复制')
                if not os.path.exists('./处理'):
                    os.mkdir('./处理')
                video_name = video.split('/')[-1]
                copy_video='./复制/'+video_name
                deal_video='./处理/'+video_name
                if os.path.isfile(copy_video):
                    os.remove(copy_video)
                shutil.copyfile(video,copy_video)

                # 视频倒放
                if is_reverse:
                    # 视频倒放，无音频
                    if self.ui.radioButton.isChecked():
                        cmd_reverse = 'ffmpeg -y -i "' + copy_video + '" -filter_complex [0:v]reverse[v] -map [v] "' + deal_video + '"'
                    # 视频倒放，音频不变
                    if self.ui.radioButton_2.isChecked():
                        cmd_reverse = 'ffmpeg -y -i "'+copy_video+'" -vf reverse "'+deal_video+'"'
                    # 音频倒放，视频不变
                    if self.ui.radioButton_9.isChecked():
                        cmd_reverse = 'ffmpeg -y -i "' + copy_video + '" -map 0 -c:v copy -af "areverse" "' + deal_video + '"'
                    # 音视频同时倒放
                    if self.ui.radioButton_10.isChecked():
                        cmd_reverse = 'ffmpeg -y -i "' + copy_video + '" -vf reverse -af areverse -preset superfast "' + deal_video + '"'

                    print(cmd_reverse)
                    self.logging_print(video+' 开始处理倒放...')
                    subprocess.call(cmd_reverse, shell=True)
                    if os.path.isfile(copy_video):
                        os.remove(copy_video)
                    shutil.copyfile(deal_video, copy_video)
                    self.logging_print(video+' 倒放处理完成！！！')

                # 去除水印
                if is_unwatermark:
                    x_value = self.ui.lineEdit_7.text()
                    y_value = self.ui.lineEdit_8.text()
                    w_value = self.ui.lineEdit_21.text()
                    h_value = self.ui.lineEdit_22.text()
                    cmd_umwm='ffmpeg -y -i "' + copy_video + '" -vf "delogo=x='+x_value+':y='+y_value+':w='+w_value+':h='+h_value+':show=0" -c:a copy "' + deal_video + '"'
                    print(cmd_umwm)
                    self.logging_print(video + ' 开始去水印...')
                    subprocess.call(cmd_umwm, shell=True)
                    if os.path.isfile(copy_video):
                        os.remove(copy_video)
                    shutil.copyfile(deal_video, copy_video)
                    self.logging_print(video + ' 水印处理完成！！！')

                # 视频裁剪
                if is_cutting:
                    left_distance = self.ui.lineEdit_26.text()
                    right_distance = self.ui.lineEdit_24.text()
                    top_distance = self.ui.lineEdit_25.text()
                    bottom_distance = self.ui.lineEdit_23.text()
                    cap = cv2.VideoCapture(video)
                    # 获取视频宽度
                    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    # 获取视频高度
                    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                    cut_width=frame_width-int(right_distance)-int(left_distance)
                    cut_height=frame_height-int(bottom_distance)-int(top_distance)
                    cmd_cutting='ffmpeg -y -i "'+copy_video+'" -strict -2 -vf crop='+str(cut_width)+':'+str(cut_height)+':'+str(left_distance)+':'+str(top_distance)+' "'+ deal_video + '"'
                    print(cmd_cutting)
                    self.logging_print(video + ' 开始裁剪视频...')
                    subprocess.call(cmd_cutting, shell=True)
                    if os.path.isfile(copy_video):
                        os.remove(copy_video)
                    shutil.copyfile(deal_video, copy_video)
                    self.logging_print(video + ' 视频裁剪完成！！！')

                # 处理完成后，复制到目标文件夹，并删除复制和处理文件夹
                outpath=self.ui.lineEdit_5.text()+'/'+video_name
                if os.path.isfile(outpath):
                    os.remove(outpath)
                shutil.copyfile(copy_video,outpath)
                shutil.rmtree("./复制/")
                shutil.rmtree("./处理/")








app = QApplication([])
stats = Stats()

stats.ui.show()

app.exec_()
