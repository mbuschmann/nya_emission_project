from __future__ import print_function, division
import os, sys, time
import datetime as dt
from PyQt5.QtGui import QIcon
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import urllib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

scriptpath = os.path.dirname(os.path.abspath(__file__))
print(scriptpath)
scriptpath = 'C:/Users/ftir/nya_emission_project'
sys.path.append(os.path.join(scriptpath, 'motorcontrol'))
sys.path.append(os.path.join(scriptpath, 'blackbody'))
sys.path.append(os.path.join(scriptpath, 'vertex80'))
sys.path.append(os.path.join(scriptpath, 'gui'))
sys.path.append(os.path.join(scriptpath, 'hutch_sensor'))
sys.path.append(os.path.join(scriptpath, 'fft'))
sys.path.append(os.path.join(scriptpath, 'ftsreader'))
from nya_em import NyaEM
from fft_ftir import fft_ftir



class nyaemgui(NyaEM, QtWidgets.QMainWindow,fft_ftir):
    def __init__(self):
        self.blocksr80comm = False
        self.blockv80comm = False #True
        self.blockmotorcomm = False
        super().__init__()
        #
        #
        self.title = 'Ny-Ålesund Emission Measurements'
        self.setWindowTitle(self.title)
        #
        self.checkbox = False
        #
        self.emailsent = 0
        #
        self.initUI()
        #
        #        self._update_canvas()
        #
        self.bck = QtCore.QTimer()
        self.bck.setInterval(1000)
        self.bck.timeout.connect(self.Update_StatusBox)
        self.bck.start()

        self.rseq = QtCore.QTimer()
        self.rseq.setInterval(1000)
        self.rseq.timeout.connect(self.run_sequence)
        self.rseq.start()

        self.check_cond = QtCore.QTimer()
        self.check_cond.setInterval (1000)
        self.check_cond.timeout.connect(self.check_conditions)
        self.check_cond.start()

        self.timer_al = QtCore.QTimer()
        self.timer_al.setInterval (100)
        self.timer_al.timeout.connect(self._update_actual_line)
        self.timer_al.start()

    def write_sequence(self):

        self.sequence_box.clear()
        for l in self.sequence:
            self.sequence_box.appendPlainText('%s %s'%(l,self.sequence[l]))

    def write_v80parms(self):
        self.vertex_box.clear()
        for l in self.v80.meas_params.keys():
            self.vertex_box.appendPlainText('%s %s'%(l,self.v80.meas_params[l]))

        self.sequence_box.clear()
        for l in self.sequence:
            self.sequence_box.appendPlainText('%s %s'%(l,self.sequence[l]))

    def write_conditions(self):
        self.condition_box.appendPlainText('%s %s' % ('Vertex 80',self.condition_v80))
        self.condition_box.appendPlainText('%s %s' % ('Hutch open',self.condition_hutch))


    def Choose_SequenceFile(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self._main,'Load Sequence File')
        self.sequence_file = file[0]
        if self.sequence_file:
            self.load_sequence(self.sequence_file)
            self.write_sequence()
            self.write_v80parms()

    def initMaintab(self):
        self._main.gridlayout = QtWidgets.QGridLayout()

        self.sequence_box = QtWidgets.QPlainTextEdit(self._main)
        self.vertex_box = QtWidgets.QPlainTextEdit(self._main)
        self.condition_box = QtWidgets.QPlainTextEdit(self._main)
        self.condition_box.resize(32,8)
        self.actual_line = QtWidgets.QLabel(self._main)
        self.actual_line.setText('No sequence started')

        self.write_sequence()
        self.write_v80parms()
        self.write_conditions()

        self._main.gridlayout.addWidget(self.actual_line,0,1,1,2)
        self._main.gridlayout.addWidget(self.sequence_box,1,1,5,2)
        self._main.gridlayout.addWidget(self.vertex_box,6,1,5,2)
        self._main.gridlayout.addWidget(self.condition_box,11,1,2,2)


        loadseq_button = QtWidgets.QPushButton('Load sequence',self._main)
        loadseq_button.setToolTip("Load Sequence")
        self._main.gridlayout.addWidget(loadseq_button, 0, 0, 1, 1)
        loadseq_button.clicked.connect(self.Choose_SequenceFile)

        run_button = QtWidgets.QPushButton('Run Sequence', self._main)
        run_button.setToolTip("Run Sequence")
        self._main.gridlayout.addWidget(run_button,1,0,1,1)
        run_button.clicked.connect(self.start_sequence)

        stop_button = QtWidgets.QPushButton('Stop Sequence', self._main)
        stop_button.setToolTip("Stop Sequence immediately")
        self._main.gridlayout.addWidget(stop_button,2,0,1,1)
        stop_button.clicked.connect(self.stop_sequence)

        term_button = QtWidgets.QPushButton('Terminate Sequence', self._main)
        term_button.setToolTip("Stop Sequence immediately")
        self._main.gridlayout.addWidget(term_button, 3, 0, 1, 1)
        term_button.clicked.connect(self.terminate_sequence)

        self.ht1textbox = QtWidgets.QLineEdit(self)
        self.ht1textbox.setText('%3i'%self.preset_temps['ht1'])
        self._main.gridlayout.addWidget(self.ht1textbox, 5, 0, 1, 1)
        ht1tempbutton = QtWidgets.QPushButton('HT1 temp:', self)
        ht1tempbutton.setToolTip("Enter the current HT1 preset temperature")
        self._main.gridlayout.addWidget(ht1tempbutton, 4, 0, 1, 1, QtCore.Qt.AlignRight)
        ht1tempbutton.clicked.connect(self.setht1param)

        self.ir301textbox = QtWidgets.QLineEdit(self)
        self.ir301textbox.setText('%3.1f'%self.preset_temps['ir301'])
        self._main.gridlayout.addWidget(self.ir301textbox, 7, 0, 1, 1)
        ir301tempbutton = QtWidgets.QPushButton('IR301 temp:', self)
        ir301tempbutton.setToolTip("Enter the current IR301 preset temperature")
        self._main.gridlayout.addWidget(ir301tempbutton, 6, 0, 1, 1, QtCore.Qt.AlignRight)
        ir301tempbutton.clicked.connect(self.setir301param)

        ##matplotlib integration from:
        ##https://matplotlib.org/gallery/user_interfaces/embedding_in_qt_sgskip.html#sphx-glr-gallery-user-interfaces-embedding-in-qt-sgskip-py
        plot_box = QtWidgets.QGroupBox(self._main)
        plot_box.gridlayout = QtWidgets.QGridLayout()
        self._main.gridlayout.addWidget(plot_box, 1,4, 12, 4)
        self.dynamic_canvas = FigureCanvas(Figure(figsize=(6, 5)))
#        self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(self.dynamic_canvas,plot_box))
        plot_box.nav = NavigationToolbar(self.dynamic_canvas,plot_box)
        plot_box.gridlayout.addWidget(plot_box.nav,1,0,1,1)
        self._dynamic_ax1, self._dynamic_ax2 = self.dynamic_canvas.figure.subplots(2)
        plot_box.gridlayout.addWidget(self.dynamic_canvas,0,0,1,1)
        plot_box.setLayout(plot_box.gridlayout)

        self._main.setLayout(self._main.gridlayout)

    def initManualtab(self):

        self._manu.gridlayout = QtWidgets.QGridLayout()
        self._manu.setLayout(self._manu.gridlayout)
        measurebutton = QtWidgets.QPushButton('Start measurement', self)
        measurebutton.setToolTip("Start a measurement")
        self._manu.gridlayout.addWidget(measurebutton, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        measurebutton.clicked.connect(self.start_measure)
        #
        stopmeasurebutton = QtWidgets.QPushButton('Stop measurement', self)
        stopmeasurebutton.setToolTip("Stop a measurement")
        self._manu.gridlayout.addWidget(stopmeasurebutton, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        stopmeasurebutton.clicked.connect(self.stop_measure)
        #
        savemeasurebutton = QtWidgets.QPushButton('Save measurement', self)
        savemeasurebutton.setToolTip("Save the last measurement")
        self._manu.gridlayout.addWidget(savemeasurebutton, 0, 2, 1, 1, QtCore.Qt.AlignLeft)
        savemeasurebutton.clicked.connect(self.save_measurement)
        #
        self.setsr80textbox = QtWidgets.QLineEdit(self)
        self.setsr80textbox.setText('20')
        self._manu.gridlayout.addWidget(self.setsr80textbox, 1, 0, 1, 1, QtCore.Qt.AlignLeft)
        setsr80button = QtWidgets.QPushButton('Set SR80 temperature', self)
        self._manu.gridlayout.addWidget(setsr80button, 1, 1, 1, 1, QtCore.Qt.AlignLeft)
        setsr80button.clicked.connect(self.set_sr80temp)
        #
        self.setsr800textbox = QtWidgets.QLineEdit(self)
        self.setsr800textbox.setText('20')
        self._manu.gridlayout.addWidget(self.setsr800textbox, 2, 0, 1, 1, QtCore.Qt.AlignLeft)
        setsr800button = QtWidgets.QPushButton('Set SR800 temperature', self)
        self._manu.gridlayout.addWidget(setsr800button, 2, 1, 1, 1, QtCore.Qt.AlignLeft)
        setsr800button.clicked.connect(self.set_sr800temp)
        #


        reinitmotorbutton = QtWidgets.QPushButton('Reinit motor', self)
        reinitmotorbutton.setToolTip("Re-Initialize Mirror")
        self._manu.gridlayout.addWidget(reinitmotorbutton, 3, 0, 1, 1, QtCore.Qt.AlignLeft)
        reinitmotorbutton.clicked.connect(self.reinitmotor)
        #
        roofbutton = QtWidgets.QPushButton('Point to roof', self)
        roofbutton.setToolTip("Point mirror to roof")
        self._manu.gridlayout.addWidget(roofbutton, 4, 0, 1, 1, QtCore.Qt.AlignLeft)
        roofbutton.clicked.connect(self.motor_roof)
        #
        sr80button = QtWidgets.QPushButton('Point to SR80', self)
        sr80button.setToolTip("Point mirror to SR80 black body")
        self._manu.gridlayout.addWidget(sr80button, 5, 0, 1, 1, QtCore.Qt.AlignLeft)
        sr80button.clicked.connect(self.motor_sr80)
        #
        sr800button = QtWidgets.QPushButton('Point to SR800', self)
        sr800button.setToolTip("Point mirror to SR800 black body")
        self._manu.gridlayout.addWidget(sr800button, 6, 0, 1, 1, QtCore.Qt.AlignLeft)
        sr800button.clicked.connect(self.motor_sr800)
        #
        ht1button = QtWidgets.QPushButton('Point to ht1', self)
        ht1button.setToolTip("Point mirror to self build heat bed black body")
        self._manu.gridlayout.addWidget(ht1button, 7, 0, 1, 1, QtCore.Qt.AlignLeft)
        ht1button.clicked.connect(self.motor_ht1)
        #
        rtbutton = QtWidgets.QPushButton('Point to rt', self)
        rtbutton.setToolTip("Point mirror to self built room temperature black body")
        self._manu.gridlayout.addWidget(rtbutton, 8, 0, 1, 1, QtCore.Qt.AlignLeft)
        rtbutton.clicked.connect(self.motor_rt)
        #
        ir301button = QtWidgets.QPushButton('Point to IR301', self)
        ir301button.setToolTip("Point mirror to IR301 black body")
        self._manu.gridlayout.addWidget(ir301button, 9, 0, 1, 1, QtCore.Qt.AlignLeft)
        ir301button.clicked.connect(self.motor_ir301)
        #
        parkbutton = QtWidgets.QPushButton('Park mirror', self)
        parkbutton.setToolTip("Point mirror to park position")
        self._manu.gridlayout.addWidget(parkbutton, 10, 0, 1, 1, QtCore.Qt.AlignLeft)
        parkbutton.clicked.connect(self.motor_park)
        #
        sr800onbutton = QtWidgets.QPushButton('Switch SR800 on', self)
        sr800onbutton.setToolTip("Switch SR800 on")
        self._manu.gridlayout.addWidget(sr800onbutton, 3, 1, 1, 1, QtCore.Qt.AlignLeft)
        sr800onbutton.clicked.connect(self.switch_sr800_on)
        #
        sr800offbutton = QtWidgets.QPushButton('Switch SR800 off', self)
        sr800offbutton.setToolTip("Switch SR800 off")
        self._manu.gridlayout.addWidget(sr800offbutton, 4, 1, 1, 1, QtCore.Qt.AlignLeft)
        sr800offbutton.clicked.connect(self.switch_sr800_off)
        #
        #
        ir301onbutton = QtWidgets.QPushButton('Switch IR301 on', self)
        ir301onbutton.setToolTip("Switch IR301 on")
        self._manu.gridlayout.addWidget(ir301onbutton, 5, 1, 1, 1, QtCore.Qt.AlignLeft)
        ir301onbutton.clicked.connect(self.switch_ir301_on)
        #
        ir301offbutton = QtWidgets.QPushButton('Switch IR301 off', self)
        ir301offbutton.setToolTip("Switch IR301 off")
        self._manu.gridlayout.addWidget(ir301offbutton, 6, 1, 1, 1, QtCore.Qt.AlignLeft)
        ir301offbutton.clicked.connect(self.switch_ir301_off)
        #
        emailbutton = QtWidgets.QPushButton('Send diagnostics email', self)
        emailbutton.setToolTip("Send diagnostics emai")
        self._manu.gridlayout.addWidget(emailbutton, 7, 1, 1, 1, QtCore.Qt.AlignLeft)
        emailbutton.clicked.connect(self.send_diag_email)
        #
        self.paramtextbox = QtWidgets.QLineEdit(self)
        self.paramtextbox.setText(' | '.join([k + ':' + str(j) for k, j in self.v80.meas_params.items()]))
        self._manu.gridlayout.addWidget(self.paramtextbox, 0, 3, 1, 4)
        parambutton = QtWidgets.QPushButton('Update params', self)
        parambutton.setToolTip("Set Vertex80 measurement parameters")
        self._manu.gridlayout.addWidget(parambutton, 1, 5, 1, 1, QtCore.Qt.AlignRight)
        parambutton.clicked.connect(self.setv80param)
        #
        self.v80commcheckbox = QtWidgets.QCheckBox('Block Vertex80 communications')
        self.v80commcheckbox.stateChanged.connect(self.set_blockv80comm)
        self._manu.gridlayout.addWidget(self.v80commcheckbox, 2, 3, 1 ,1, QtCore.Qt.AlignLeft)
        #
        self.sr80commcheckbox = QtWidgets.QCheckBox('Block SR80 communications')
        self.sr80commcheckbox.stateChanged.connect(self.set_blocksr80comm)
        self._manu.gridlayout.addWidget(self.sr80commcheckbox, 3, 3, 1, 1, QtCore.Qt.AlignLeft)
        #
        #
        # self.dirlistwidget = QtWidgets.QListWidget()
        # self.make_listwidget()
        ##import ipdb; ipdb.set_trace()
        # self.dirlistwidget.itemClicked.connect(self.listclick)
        # self.gridlayout.addWidget(self.dirlistwidget, 1,3,3,2, QtCore.Qt.AlignRight)
        #
        #        self.show_seq = QtWidgets.QTextEdit(self._main)
        #        self._main.gridlayout.addWidget(self.show_seq)
        # Status Box
        self.Init_StatusBox()
        #
    def send_diag_email(self):
        sender_address = "ftirserv@uni-bremen.de"
        #receiver_address = "ftir_nya@iup.physik.uni-bremen.de"
        receiver_address = "m_buschmann@iup.physik.uni-bremen.de"
        with open('../ftirserv_email_password') as f:
            ll = f.readlines()
        account_password = ll[0].strip()

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Vertex 80 Error"
        msg['From'] = sender_address
        msg['To'] = receiver_address

        msg.attach(MIMEText("Vertex80 Error\n\nhtml output of EWS in html part of this email.", 'plain'))

        htmltexts = {}
        for htm in ['brow_diag.htm']:#, 'diag_scan.htm', 'diag_DTC.htm', 'diag_laser.htm', 'diag_SRC.htm', 'diag_rdy.htm']:
            try:
                with urllib.request.urlopen('http://172.18.0.110/'+htm) as f:
                     html = f.read()
                htmltexts[htm] = MIMEText(html.decode('utf8'), 'html')
            except Exception as e: print(e)
        for k in htmltexts.keys():
            msg.attach(htmltexts[k])
        with smtplib.SMTP_SSL("smtp.uni-bremen.de", 465) as smtp_server:
            smtp_server.login(sender_address, account_password)
            smtp_server.sendmail(sender_address, receiver_address, msg.as_string())

    def set_blocksr80comm(self, state):
        if state == QtCore.Qt.Checked:
            self.blocksr80comm = True
            print('Blocking SR80 communications')
        else:
            self.blocksr80comm = False

    def set_blockv80comm(self, state):
        if state == QtCore.Qt.Checked:
            self.blockv80comm = True
            print('Blocking Vertex80 communications')
        else:
            self.blockv80comm = False

    def set_sr80temp(self):
        self.setsr80temp(float(self.setsr80textbox.text()))

    def set_sr800temp(self):
        self.setsr800temp(float(self.setsr800textbox.text()))

    def initUI(self):
        self.main = QtWidgets.QWidget()

        self._tabs = QtWidgets.QTabWidget()
        self._main = QtWidgets.QWidget()
        self._manu = QtWidgets.QWidget()

        self.setCentralWidget(self.main)
        self.gridlayout = QtWidgets.QGridLayout()

        self._tabs.addTab(self._main,"Main")
        self._tabs.addTab(self._manu,"Manual")

        self.initMaintab()
        self.initManualtab()


        self.gridlayout.addWidget(self._tabs, 0, 0, 10, 1)
        self.main.setLayout(self.gridlayout)

        self._tabs.gridlayout = QtWidgets.QGridLayout()
        self._tabs.setLayout(self._tabs.gridlayout)

        self.gridlayout.setSpacing(10)


        self.setWindowTitle(self.title)
        left = 100
        top = 100
        width = 1000
        height = 800
        self.setGeometry(left,top,width,height)
        self.statusBar().showMessage('Loading')
        #
        mainMenu=self.menuBar()
        fileMenu=mainMenu.addMenu('File')
        #
        openButton = QtWidgets.QAction(QIcon('open24.png'), 'Open', self)
        openButton.setShortcut('Ctrl+O')
        openButton.setStatusTip('Open directory')
        openButton.triggered.connect(self.getfolder)
        fileMenu.addAction(openButton)
        #
        exitButton = QtWidgets.QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)
        #

        self.show()

    def Init_StatusBox(self):
        sbox = QtWidgets.QGroupBox(self.main)
        self.gridlayout.addWidget(sbox,0,1,10,1)

        sbox.gridlayout = QtWidgets.QGridLayout()
        title = QtWidgets.QLabel(sbox)
        title.setText('Status box')
        sbox.gridlayout.addWidget(title,0,0,1,1,QtCore.Qt.AlignLeft)

        ### General status and kob box

        statbox = QtWidgets.QGroupBox(sbox)
        sbox.gridlayout.addWidget(statbox, 1, 0, 1, 1)
        statbox.gridlayout = QtWidgets.QGridLayout()

        ### Conditions OK?
        statlabel = QtWidgets.QLabel(statbox)
        statlabel.setText('Conditions')
        statbox.gridlayout.addWidget(statlabel, 0, 0, 1, 2, QtCore.Qt.AlignLeft)

        self.conds = QtWidgets.QLabel(statbox)
        statbox.gridlayout.addWidget(self.conds, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        statbox.setLayout(statbox.gridlayout)

        ### Which state is the software in?
        modlabel = QtWidgets.QLabel(statbox)
        modlabel.setText('Software Mode')
        statbox.gridlayout.addWidget(modlabel,1,0,1,1,QtCore.Qt.AlignLeft)

        self.auto_modus = QtWidgets.QLabel(statbox)
        statbox.gridlayout.addWidget(self.auto_modus, 1, 1, 1, 1, QtCore.Qt.AlignLeft)

        modlabel = QtWidgets.QLabel(statbox)
        modlabel.setText('Sequence running?')
        statbox.gridlayout.addWidget(modlabel,2,0,1,1,QtCore.Qt.AlignLeft)

        self.seq_modus = QtWidgets.QLabel(statbox)
        statbox.gridlayout.addWidget(self.seq_modus, 2, 1, 1, 1, QtCore.Qt.AlignLeft)

        statbox.setLayout(statbox.gridlayout)


        ### SR 80 monitor box

        tempbox = QtWidgets.QGroupBox(sbox)
        sbox.gridlayout.addWidget(tempbox,2,0,1,1)

        tempbox.gridlayout = QtWidgets.QGridLayout()
        templabel = QtWidgets.QLabel(tempbox)
        templabel.setText('SR80 Temperature')
        tempbox.gridlayout.addWidget(templabel,1,0,1,2,QtCore.Qt.AlignLeft)
#        self.sr80_temp = QtWidgets.QLabel(sbox)
#        sbox.gridlayout.addWidget(self.sr80_temp,1,1,1,1,QtCore.Qt.AlignLeft)

        sr80_l1 = QtWidgets.QLabel(tempbox)
        sr80_l1.setText('Target')
        tempbox.gridlayout.addWidget(sr80_l1, 2, 0, 1, 1, QtCore.Qt.AlignLeft)

        self.sr80_target = QtWidgets.QLabel(tempbox)
        tempbox.gridlayout.addWidget(self.sr80_target,2,1,1,1,QtCore.Qt.AlignLeft)

        sr80_l1 = QtWidgets.QLabel(tempbox)
        sr80_l1.setText('Reached')
        tempbox.gridlayout.addWidget(sr80_l1, 3, 0, 1, 1, QtCore.Qt.AlignLeft)

        self.sr80_reached = QtWidgets.QLabel(tempbox)
        tempbox.gridlayout.addWidget(self.sr80_reached,3,1,1,1,QtCore.Qt.AlignLeft)

        sr80_l1 = QtWidgets.QLabel(tempbox)
        sr80_l1.setText('Stable')
        tempbox.gridlayout.addWidget(sr80_l1, 4, 0, 1, 1, QtCore.Qt.AlignLeft)

        self.sr80_status = QtWidgets.QLabel(tempbox)
        tempbox.gridlayout.addWidget(self.sr80_status,4,1,1,1,QtCore.Qt.AlignLeft)
        tempbox.setLayout(tempbox.gridlayout)

        #### VR80 Monitor box

        v80box = QtWidgets.QGroupBox(sbox)
        sbox.gridlayout.addWidget(v80box,3,0,1,1)
        v80box.gridlayout = QtWidgets.QGridLayout()

        v80_label = QtWidgets.QLabel(v80box)
        v80_label.setText('Vertex 80')
        v80box.gridlayout.addWidget(v80_label, 0, 0, 1, 2, QtCore.Qt.AlignLeft)

        v80_l1 = QtWidgets.QLabel(v80box)
        v80_l1.setText('Status')
        v80box.gridlayout.addWidget(v80_l1, 1, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.v80_status = QtWidgets.QLabel(v80box)
        v80box.gridlayout.addWidget(self.v80_status,1,1,1,1,QtCore.Qt.AlignLeft)

        v80_l4 = QtWidgets.QLabel(v80box)
        v80_l4.setText('Scans')
        v80box.gridlayout.addWidget(v80_l4, 2, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.v80_scans = QtWidgets.QLabel(v80box)
        v80box.gridlayout.addWidget(self.v80_scans,2,1,1,1,QtCore.Qt.AlignLeft)

        v80_l2 = QtWidgets.QLabel(v80box)
        v80_l2.setText('Detector')
        v80box.gridlayout.addWidget(v80_l2, 3, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.v80_detector = QtWidgets.QLabel(v80box)
        v80box.gridlayout.addWidget(self.v80_detector,3,1,1,1,QtCore.Qt.AlignLeft)

        v80_l3 = QtWidgets.QLabel(v80box)
        v80_l3.setText('Datafile')
        v80box.gridlayout.addWidget(v80_l3, 4, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.v80_datafile = QtWidgets.QLabel(v80box)
        v80box.gridlayout.addWidget(self.v80_datafile,4,1,1,1,QtCore.Qt.AlignLeft)

        v80_pka = QtWidgets.QLabel(v80box)
        v80_pka.setText('Amplitude')
        v80box.gridlayout.addWidget(v80_pka, 5, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.v80_pka = QtWidgets.QLabel(v80box)
        v80box.gridlayout.addWidget(self.v80_pka,5,1,1,1,QtCore.Qt.AlignLeft)
        
        v80box.setLayout(v80box.gridlayout)

        ### Hutch status

        hutchbox = QtWidgets.QGroupBox(sbox)
        sbox.gridlayout.addWidget(hutchbox,4,0,1,1)
        hutchbox.gridlayout = QtWidgets.QGridLayout()

        hutch_label = QtWidgets.QLabel(hutchbox)
        hutch_label.setText('Hutch')
        hutchbox.gridlayout.addWidget(hutch_label, 0, 0, 1, 2, QtCore.Qt.AlignLeft)
        hutchbox.setLayout(hutchbox.gridlayout)

        hutch_l1 = QtWidgets.QLabel(v80box)
        hutch_l1.setText('Status')
        hutchbox.gridlayout.addWidget(hutch_l1, 1, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.hutch_status = QtWidgets.QLabel(hutchbox)
        hutchbox.gridlayout.addWidget(self.hutch_status,1,1,1,1,QtCore.Qt.AlignLeft)
        self.hutch_remote = QtWidgets.QLabel(hutchbox)
        hutchbox.gridlayout.addWidget(self.hutch_remote,2,1,1,1,QtCore.Qt.AlignLeft)

        sbox.setLayout(sbox.gridlayout)

    def Update_StatusBox(self):
        #t = self.sr80.get_temperature()
        #t1,t2,st = self.Temperature_reached()
        #self.sr80_target.setText('%.2f'%self.bbtemp)
        #self.sr80_reached.setText('%.2f'%t)
        #self.sr80_status.setText('%s'%st)

        v80stat = self.v80.get_status()

        # dirty hack to send error email quickly
        if 'err' in v80stat['status'].lower():
            time.sleep(20)
            self.emailsent += 1
            if 'err' in v80stat['status'].lower() and self.emailsent>60:
                self.send_diag_email()
                #self.emailsent=0
            else: pass
        else: pass

        self.auto_modus.setText(self.actual_job)
        self.seq_modus.setText('%s'%self.run_seq)
        if self.conditions_ok:
            self.conds.setText('OK')
        else:
            self.conds.setText('Not OK')
        self.v80_status.setText(v80stat['status'])
        self.v80_detector.setText(v80stat['detector'])
        self.v80_datafile.setText(v80stat['datafile'])
        self.v80_scans.setText('%i/%i'%(v80stat['scans'],v80stat['restscans']))
        self.v80_pka.setText('%i'%self.pka)
        self.hutch_status.setText(self.hutchstatus['hutch'])
        self.hutch_remote.setText(self.hutchstatus['remote'])
        
        self.actual_line.setText('%d: %s'%(self.entry, self.sequence[self.entry]))

        #new_file = self.get_newmeasurement()
        #print ('New file', new_file)
        #if new_file != None:
        #    self._update_canvas(new_file)
        if self.v80.spectrumupdated:
            try:
                self.oldfile = self.newfile
            except Exception as e:
                print('Plotting old spectrum error:\n\t', e)
                self.oldfile = None
            self.newfile = self.get_newmeasurement()
            print(self.newfile)
            #
            if self.newfile != None:
                self._update_canvas()
            self.v80.spectrumupdated = False
        else:
            pass

    def _update_actual_line(self):
        self.actual_line.setText('%d: %s' % (self.entry, self.sequence[self.entry]))
        
    #def _update_canvas(self, file):
    #    #print('Plotting ', self.filename, self.new_measurement)
    #    #if not self.new_measurement:
    #    #    return();
    #    self._dynamic_ax1.clear()
    #    self._dynamic_ax2.clear()
    #    try:
    #        spectrum = self.fft(file)
    #        self._dynamic_ax1.set_title('Latest measurement ' + file)
    #        self._dynamic_ax1.plot(spectrum['ifg'], 'k-')
    #        self._dynamic_ax1.figure.canvas.draw()
    #        self._dynamic_ax2.plot(spectrum['wvn'], np.abs(spectrum['spectrum']), 'k-')
    #        self._dynamic_ax2.figure.canvas.draw()
    #    except Exception as e:
    #        print(e)
    #        print('%s %s'%('fft failed on ', self.newfile))

    def _update_canvas(self):
        #print('Plotting ', self.filename, self.new_measurement)
        #if not self.new_measurement:
        #    return();
        self._dynamic_ax1.clear()
        self._dynamic_ax2.clear()
        try:
            try:
                spectrum_old = self.fft(self.oldfile)
                c1 = spectrum_old['wvn']<3000
                self._dynamic_ax1.plot(spectrum_old['ifg'], 'b-', label=self.oldfile)
                self._dynamic_ax2.plot(spectrum_old['wvn'][c1], np.abs(spectrum_old['spectrum'][c1]), 'b-', label=self.oldfile)
            except:
                pass
            spectrum = self.fft(self.newfile)
            c2 = spectrum['wvn'] < 3000
            #self._dynamic_ax1.set_title('Latest measurement ' + file)
            self._dynamic_ax1.plot(spectrum['ifg'], 'k-', label=self.newfile)
            self._dynamic_ax1.legend(loc='upper center', fontsize=7)
            self._dynamic_ax1.figure.canvas.draw()
            self._dynamic_ax2.plot(spectrum['wvn'][c2], np.abs(spectrum['spectrum'][c2]), 'k-', label=self.newfile)
            self._dynamic_ax2.legend(loc='upper right', fontsize=7)
            self._dynamic_ax2.figure.canvas.draw()
        except Exception as e:
            print(e)
            print('%s %s'%('fft failed on ', self.newfile))

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    ex = nyaemgui() #NyaEM()
    sys.exit(app.exec_())
