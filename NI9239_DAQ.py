# .copyright : (c) 2021 Istituto Nazionale di Ricerca Metrologica
# .license : MIT License (https://opensource.org/licenses/MIT)

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QWidget, QBoxLayout, QCheckBox, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal
import pyqtgraph as pg
from scipy.fftpack import fft, fftfreq
import math
import nidaqmx
import nidaqmx.constants
import os
import csv
import sys
import pyvisa as visa
import numpy as np
    

#PARAMETRI DEL GENERATORE DI FUNZIONI AGILENT AWG33250A (AWG) - utilizzato per testare il modulo NI9239 da remoto
MAX_AMP = 1 # ampiezza massima in volt
MAX_OFFSET = 1 # offset massimo in volt
MAX_FREQ = 1000 # frequenza del segnale sinusoidale in hertz
AWG_GPIB_ADDRESS = 10 # indirizzo GPIB, visibile su NI MAX


# CLASSE DELLA FINESTRA PRINCIPALE, realizzata cn PyQt5
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 200)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.graphTimeWidget = PlotWidget(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphTimeWidget.sizePolicy().hasHeightForWidth())
        self.graphTimeWidget.setSizePolicy(sizePolicy)
        self.graphTimeWidget.setObjectName("graphTimeWidget")
        self.verticalLayout.addWidget(self.graphTimeWidget)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.graphFrequencyWidget = PlotWidget(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphFrequencyWidget.sizePolicy().hasHeightForWidth())
        self.graphFrequencyWidget.setSizePolicy(sizePolicy)
        self.graphFrequencyWidget.setObjectName("graphFrequencyWidget")
        self.verticalLayout.addWidget(self.graphFrequencyWidget)
        self.gridLayout.addWidget(self.frame_2, 0, 2, 1, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.labelWindowing = QtWidgets.QLabel(self.frame)
        self.labelWindowing.setObjectName("labelWindowing")
        self.gridLayout_2.addWidget(self.labelWindowing, 23, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 80, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 1, 0, 1, 2)
        self.buttonGeneratore = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonGeneratore.sizePolicy().hasHeightForWidth())
        self.buttonGeneratore.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.buttonGeneratore.setFont(font)
        self.buttonGeneratore.setObjectName("buttonGeneratore")
        self.gridLayout_2.addWidget(self.buttonGeneratore, 30, 0, 1, 1)
        self.buttonChannel = QtWidgets.QPushButton(self.frame)
        self.buttonChannel.setObjectName("buttonChannel")
        self.gridLayout_2.addWidget(self.buttonChannel, 4, 1, 1, 1)
        self.labelsamplesToRead = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelsamplesToRead.sizePolicy().hasHeightForWidth())
        self.labelsamplesToRead.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelsamplesToRead.setFont(font)
        self.labelsamplesToRead.setObjectName("labelsamplesToRead")
        self.gridLayout_2.addWidget(self.labelsamplesToRead, 17, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 80, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem2, 22, 0, 1, 2)
        self.buttonStart = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonStart.sizePolicy().hasHeightForWidth())
        self.buttonStart.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.buttonStart.setFont(font)
        self.buttonStart.setObjectName("buttonStart")
        self.gridLayout_2.addWidget(self.buttonStart, 0, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem3, 16, 1, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(20, 80, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem4, 14, 0, 1, 2)
        self.buttonSaveFile = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonSaveFile.sizePolicy().hasHeightForWidth())
        self.buttonSaveFile.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.buttonSaveFile.setFont(font)
        self.buttonSaveFile.setObjectName("buttonSaveFile")
        self.gridLayout_2.addWidget(self.buttonSaveFile, 51, 1, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem5, 18, 1, 1, 1)
        self.spinBoxSamples = QtWidgets.QSpinBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxSamples.sizePolicy().hasHeightForWidth())
        self.spinBoxSamples.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.spinBoxSamples.setFont(font)
        self.spinBoxSamples.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.spinBoxSamples.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.spinBoxSamples.setFrame(True)
        self.spinBoxSamples.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBoxSamples.setMaximum(10000000)
        self.spinBoxSamples.setObjectName("spinBoxSamples")
        self.gridLayout_2.addWidget(self.spinBoxSamples, 17, 1, 1, 1)
        self.labelRate = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelRate.sizePolicy().hasHeightForWidth())
        self.labelRate.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelRate.setFont(font)
        self.labelRate.setObjectName("labelRate")
        self.gridLayout_2.addWidget(self.labelRate, 21, 0, 1, 1)
        self.comboBoxAcqMode = QtWidgets.QComboBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxAcqMode.sizePolicy().hasHeightForWidth())
        self.comboBoxAcqMode.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.comboBoxAcqMode.setFont(font)
        self.comboBoxAcqMode.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContentsOnFirstShow)
        self.comboBoxAcqMode.setObjectName("comboBoxAcqMode")
        self.comboBoxAcqMode.addItem("")
        self.comboBoxAcqMode.addItem("")
        self.gridLayout_2.addWidget(self.comboBoxAcqMode, 15, 1, 1, 1)
        self.comboBoxWindowing = QtWidgets.QComboBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxWindowing.sizePolicy().hasHeightForWidth())
        self.comboBoxWindowing.setSizePolicy(sizePolicy)
        self.comboBoxWindowing.setObjectName("comboBoxWindowing")
        self.comboBoxWindowing.addItem("")
        self.comboBoxWindowing.addItem("")
        self.comboBoxWindowing.addItem("")
        self.comboBoxWindowing.addItem("")
        self.gridLayout_2.addWidget(self.comboBoxWindowing, 23, 1, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(20, 80, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem6, 44, 0, 1, 2)
        self.labelOffset = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelOffset.sizePolicy().hasHeightForWidth())
        self.labelOffset.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelOffset.setFont(font)
        self.labelOffset.setObjectName("labelOffset")
        self.gridLayout_2.addWidget(self.labelOffset, 43, 0, 1, 1)
        self.spinBoxAmplitude = QtWidgets.QSpinBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxAmplitude.sizePolicy().hasHeightForWidth())
        self.spinBoxAmplitude.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.spinBoxAmplitude.setFont(font)
        self.spinBoxAmplitude.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBoxAmplitude.setMaximum(1000000)
        self.spinBoxAmplitude.setObjectName("spinBoxAmplitude")
        self.gridLayout_2.addWidget(self.spinBoxAmplitude, 37, 1, 1, 1)
        self.labelNote = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelNote.sizePolicy().hasHeightForWidth())
        self.labelNote.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelNote.setFont(font)
        self.labelNote.setObjectName("labelNote")
        self.gridLayout_2.addWidget(self.labelNote, 48, 0, 1, 1)
        self.labelMode = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelMode.sizePolicy().hasHeightForWidth())
        self.labelMode.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelMode.setFont(font)
        self.labelMode.setObjectName("labelMode")
        self.gridLayout_2.addWidget(self.labelMode, 15, 0, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem7, 38, 0, 1, 2)
        self.spinBoxFreqGen = QtWidgets.QSpinBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxFreqGen.sizePolicy().hasHeightForWidth())
        self.spinBoxFreqGen.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.spinBoxFreqGen.setFont(font)
        self.spinBoxFreqGen.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.spinBoxFreqGen.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBoxFreqGen.setMaximum(1000000)
        self.spinBoxFreqGen.setObjectName("spinBoxFreqGen")
        self.gridLayout_2.addWidget(self.spinBoxFreqGen, 40, 1, 1, 1)
        self.spinBoxOffset = QtWidgets.QSpinBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxOffset.sizePolicy().hasHeightForWidth())
        self.spinBoxOffset.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.spinBoxOffset.setFont(font)
        self.spinBoxOffset.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBoxOffset.setMaximum(1000)
        self.spinBoxOffset.setObjectName("spinBoxOffset")
        self.gridLayout_2.addWidget(self.spinBoxOffset, 43, 1, 1, 1)
        self.labelCh = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCh.sizePolicy().hasHeightForWidth())
        self.labelCh.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelCh.setFont(font)
        self.labelCh.setObjectName("labelCh")
        self.gridLayout_2.addWidget(self.labelCh, 4, 0, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem8, 41, 0, 1, 2)
        self.spinBoxRate = QtWidgets.QDoubleSpinBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxRate.sizePolicy().hasHeightForWidth())
        self.spinBoxRate.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.spinBoxRate.setFont(font)
        self.spinBoxRate.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.spinBoxRate.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.spinBoxRate.setFrame(True)
        self.spinBoxRate.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBoxRate.setDecimals(3)
        self.spinBoxRate.setObjectName("spinBoxRate")
        self.gridLayout_2.addWidget(self.spinBoxRate, 21, 1, 1, 1)
        spacerItem9 = QtWidgets.QSpacerItem(20, 80, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem9, 27, 0, 1, 2)
        self.labelFrequencyGen = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelFrequencyGen.setFont(font)
        self.labelFrequencyGen.setObjectName("labelFrequencyGen")
        self.gridLayout_2.addWidget(self.labelFrequencyGen, 40, 0, 1, 1)
        spacerItem10 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem10, 50, 0, 1, 2)
        self.textEdit = QtWidgets.QTextEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout_2.addWidget(self.textEdit, 49, 0, 1, 2)
        spacerItem11 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem11, 36, 0, 1, 2)
        self.labelAmplitude = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelAmplitude.sizePolicy().hasHeightForWidth())
        self.labelAmplitude.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.labelAmplitude.setFont(font)
        self.labelAmplitude.setObjectName("labelAmplitude")
        self.gridLayout_2.addWidget(self.labelAmplitude, 37, 0, 1, 1)
        spacerItem12 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem12, 29, 0, 1, 1)
        self.buttonAWG = QtWidgets.QPushButton(self.frame)
        self.buttonAWG.setObjectName("buttonAWG")
        self.gridLayout_2.addWidget(self.buttonAWG, 28, 1, 1, 1)
        self.buttonSaveGraph = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonSaveGraph.sizePolicy().hasHeightForWidth())
        self.buttonSaveGraph.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.buttonSaveGraph.setFont(font)
        self.buttonSaveGraph.setObjectName("buttonSaveGraph")
        self.gridLayout_2.addWidget(self.buttonSaveGraph, 51, 0, 1, 1)
        spacerItem13 = QtWidgets.QSpacerItem(20, 80, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem13, 24, 0, 1, 2)
        self.gridLayout.addWidget(self.frame, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1525, 31))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        MainWindow.show()
        
        app.aboutToQuit.connect(self.closeEvent)   #quando viene chiusa la GUI cliccando la x sulla finestra, connetto il segnale a closeEvent in modo da eliminare anche l'oggetto Agilent se è stato creato e terminare eventualmente l'acquisizione
        
    # DISPOSITIVI DISPONIBILI NEL SISTEMA E NOME DEI VARI CANALI DEI MODULI NI9239
        
        sys = nidaqmx.system.System() #creo oggetto System
        list_devices = sys.devices.device_names # nomi dei devices disponibili
        print(list_devices)
        print("\n")
 
        global ai_channels_list     #variabile globale così è visibile anche alla classe WindowChannel, che la usa per determinare il numero di checkBoxes da creare
        ai_channels_list = np.array([]) # inizializzo array vuoto che conterrà l'elenco dei canali ai disponibili

        for dev_name in list_devices:
            dev = nidaqmx.system.Device(dev_name)

            if not(dev.dev_is_simulated): #se non è un dispositivo simulato
                #dev.ai_physical_chans.channel_names # canali analog input disponibili per ogni device in list_devices
                ai_channels_list = np.append(ai_channels_list, dev.ai_physical_chans.channel_names) # riempio array
    
    # VALORI DI DEFAULT DEGLI SPIN BOX PER FREQUENZA DI CAMPIONAMENTO E NUMERO DI CAMPIONI
        self.spinBoxRate.setValue(50)           #frequenza di default è settata al valore di 50kS/s
        self.spinBoxSamples.setValue(1000)      #i valori di input sono di default 1000
     
    #VALORI DI DEFAULT DELLA PARTE DI GUI RIGUARDANTE IL GENERATORE DI FUNZIONI
        self.spinBoxAmplitude.setValue(1)       #l'ampiezza della funzione generata dal generatore di funzione è di default 1
        self.spinBoxFreqGen.setValue(50)        #la frequenza della funzione generata dal generatore di funzione è di default 50
        
        #gli spinBox relativi al generatore di funzioni sono settati in sola lettura di default, quando l'utente preme initialize AWG vengono attivati, e quindi accettano un input
        self.spinBoxAmplitude.setReadOnly(True)
        self.spinBoxFreqGen.setReadOnly(True)
        self.spinBoxOffset.setReadOnly(True)
       
        self.buttonGeneratore.setEnabled(False)     #di default questo pulsante è disabilitato, si abilita solo quando l'utente clicca initialize AWG
    
    # COLORE DI DEFAULT DEL PULSANTE START -> VERDE
        self.buttonStart.setStyleSheet("background-color: green")
            
    # PERSONALIZZAZIONE GRAFICI NELLA GUI, con colore di sfondo, griglia, nomi degli assi e aggiunta di legenda
        styles = {'color':(0,0,0), 'font-size':'10px'}
        
        # grafico dominio del tempo
        self.graphTimeWidget.setBackground('w')
        self.graphTimeWidget.setTitle("Time Domain", color = (0,0,0), width = 10)
        self.graphTimeWidget.setLabel('left', 'Voltage (V)', **styles)
        self.graphTimeWidget.setLabel('bottom', 'Time (s)', **styles)
        self.graphTimeWidget.showGrid(x=True, y=True)
        self.graphTimeWidget.addLegend((900, 10), labelTextColor=(0,0,0))
        
        # grafico dominio della frequenza
        self.graphFrequencyWidget.setBackground('w')
        self.graphFrequencyWidget.setTitle("Frequency Domain", color = (0,0,0), width = 10)
        self.graphFrequencyWidget.setLabel('left', 'Magnitude (dBV)', **styles)
        self.graphFrequencyWidget.setLabel('bottom', 'Frequency (Hz)', **styles)
        self.graphFrequencyWidget.showGrid(x=True, y=True)
        self.graphFrequencyWidget.addLegend((900, 10), labelTextColor=(0,0,0))
        
    # FLAG e VARIABILI
        
        # #flag per eventuale trigger, di default il trigger è disattivato
        # self.triggerON = False
        #Variabile per seconda finestra grafica contenente i canali da aggiungere
        self.window_channels = None     #setto a None perchè non è ancora stata creata 
        
        #flag per sapere se è stato creato un oggetto della classe Agilent
        self.awg_created = False
        
        #flag per sapere se l'utente ha premuto il pulsante per selezionare i canali
        self.isAddChannel_clicked = False
      
        #Flag per sapere se pulsante START è stato premuto, controllo su pressedSave 
        self.is_started = False
        
        #Vettore contente colori utilizzabili per disegnare i grafici graphTimeWidget e graphFrequencyWidget
        self.colors = ['r', 'b','g', 'k', (32,178,170), (153,50,204), (255,255,0), (128,0,0)] 
        
        #Vettore self.f_s contiene i valori di Sample Rate ammissibili dallo strumento, la formula è stata ricavata dal manuale del NI9239
        f_m = 12.8e6           #fm è la frequenza del master timebase interno del modulo, valore preso dal manuale
        self.fs_ok = []  #lista che contiene le frequenze di campionamento ammissibili dallo strumento
        for n in range(1,32):   #nella formula n varia da 1 a 31, siccome nella funzione range il valore finale è escluso inserisco da 1 a 32
            f_s =((f_m/256)/n)/1000   #calcolo frequenza e divido per mille per averlo in kS/s
            f_s = round(f_s, 3)    #arrotondo a 3 cifre decimali
            self.fs_ok.append(f_s)    #inserisco frequenza nella lista
            
        
    # CREAZIONE DELLA CARTELLA Saved_data DOVE SARANNO SALVATI I DATI ACQUISITI (formato immagine e testo)
    
        path = os.getcwd()          #acquisisco il path della directory corrente
        self.directory_path = path + "\Saved_data"   #aggiungo al path il nome della cartella da creare
        
        #controllo se la cartella con questo nome è già stata creata o meno
        if os.path.exists(self.directory_path):      #se la cartella già esiste non faccio nulla
            pass
        else:
            os.makedirs(self.directory_path)     #altrimenti la creo
        
    # COLLEGAMENTI PER AZIONI FATTE DA UTENTE CLICCANDO I BOTTONI

        # Collegamento azione quando si preme un pulsante, vengono connessi i segnali emessi da ogni pulsante ai relativi slot
        self.buttonStart.clicked.connect(self.pressedStart)
        self.buttonSaveGraph.clicked.connect(self.pressedSaveGraph)
        self.buttonSaveFile.clicked.connect(self.pressedSaveFile)
        self.buttonAWG.clicked.connect(self.pressedInitializeAWG)
        self.buttonGeneratore.clicked.connect(self.pressedStartGen)
        self.buttonChannel.clicked.connect(self.pressedAddChannel)
        
        # PER EVENTUALE TRIGGER
        # self.buttonTrigger.clicked.connect(self.pressedStartTrigger)
    
        
    # POPUP CHE VENGONO MOSTRATI IN CASO DI ERRORE, WARNING, CHIUSURA PROGRAMMA, SALVATAGGIO CORRETTO
    #per ogni popup si crea un QMessageBox, si setta titolo, icona, pulsante predefinito e relativo messaggio da mostrare all'utente
    
    # popup per errore nel caso l'utente non abbia selezionato alcun canale
    def show_popupNoChannel(self):
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("No channel selected")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec_()
        
    # popoup che viene mostrato se non si è ancora iniziata l'acquisizione di dati e si tenta di salvare
    def show_popupNoAcquisition(self):
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("Nothing to save\nPress 'START' to start the acquisition")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec_()
    
    # popup che viene mostrato se il savataggio di immagine o file testo è andato a buon fine
    def show_popupSaved(self):
        msg = QMessageBox()
        msg.setWindowTitle("Information")
        msg.setText("File successfully saved")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec_()
    
    #popup che viene mostrato se la frequenza inserita non è consentita dallo strumento
    def show_popupSampleRate(self):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        # msg.setText("La frequenza inserita non è consentita dallo strumento.\n E' stata automaticamente sostituita con quella ammissibile più vicina")
        msg.setText("Entered Rate value is not supported.\nIt has been changed with the nearest available one")
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec_()


    # FUNZIONI PER PULSANTI
    
    #APRE NUOVA FINESTRA PER CREAZIONE DELLE CHECKBOX DEI CANALI
    def pressedAddChannel(self, MainWindow):
        self.isAddChannel_clicked = True    #diventa True il flag per sapere se pulsante è stato premuto
        
        if self.window_channels is None:    #se la finestra ancora non esiste la creo, altrimenti la mostro e basta
            self.window_channels = WindowChannel()   #creo la finestra per i canali disponibili
         
        self.window_channels.showNormal()   #mostra finestra
        
        
    #AVVIA ACQUISIZIONE DATI
    def pressedStart(self, MainWindow):
    
        
        global active_channels     #lista che contiene i canali attualmente attivi, è una variabile globale così da essere visibile anche alla classe thread
        
        if self.isAddChannel_clicked == False:    #se utente non ha cliccato add Channels, viene mostrato popup per avvertire di scegliere i canali da cui vuole acquisire i dati      
            self.show_popupNoChannel()
            return

        active_channels = checked_ch  #memorizzo le checkBox selezionate nella lista active_channels
        
        if len(active_channels) == 0:   #se l'utente non ha selezionato nessun canale lo si avvisa
            self.show_popupNoChannel()
            return
        else:
            self.is_started = True   #se premo start e sono stati selezionati dei canali allora setto il flag a True
        
        global sample_rate      #variabili globali per rendere visibili frequenza di campionamento e numero di input alla classe WorkerThread
        global n_input
        
        #controllo che l'utente abbia inserito dei valori di Sample Rate consentiti dallo strumento, quindi valuto che coincida con uno dei valori contenuti in f_s sennò l'utente viene avvisato dell'errore e viene mostrato pop_up di errore
        sample_rate = 0  
        for i in self.fs_ok:              #controllo che il valore di sample_rate inserito dall'utente è uguale a uno di quelli inseri, se si il valore viene assegnato alla variabile sample_rate 
            if self.spinBoxRate.value() == i:
                sample_rate = i*1000
                break
        
        if sample_rate == 0:        #se il valore sample_rate è rimasto a 0 vuol dire che il valore inserito dall'utente non è ammesso dallo strumento, quindi viene sostituto con quello ammissibile più vicino e si lancia un messaggio di errore per avvertire l'utente
            
            dist_min=100000             #algoritmo per il calcolo del valore ammissibile più vicino a quello scritto dall'utente
            for i in self.fs_ok:
                dist = self.spinBoxRate.value() - i
                if dist < 0.000 and i == 50:
                    dist = i - self.spinBoxRate.value()
                if dist < dist_min and dist > 0.000:
                    dist_min = dist
                    sample_rate = i*1000
                    
            if dist < 0.000:         #se l'ultima distanza calcolata nel for è inferiore a 0 vuol dire che è stato inserito un numero inferiore al minimo, allora sostituisco col minimo che è l'ultimo elemento della lista self.fs_ok
                sample_rate = self.fs_ok[len(self.fs_ok)-1]*1000
            
            self.spinBoxRate.setValue(sample_rate/1000)         #setto automaticamente il valore nello spinBox
            self.show_popupSampleRate()     #mostro popup pr avvertire l'utente che aveva inserito una frequenza non ammissibile dallo strumento

        #controllo su valore di input inseriti da utente
        if self.spinBoxSamples.value() < 1000:      #se il numero di input che inserisce l'utente è inferiore a mille, viene settato automaticamente a 1000
            self.spinBoxSamples.setValue(1000)
        
        #i valori inseriti dall'utente per frequenza e input vengono salvati nelle rispettive variabili   
        n_input = self.spinBoxSamples.value()
        
        #creo lista contente i secondi di acquisizione
        self.time = []
        for i in range(0, n_input):
            dist_temporale = 1/sample_rate * i   #calcolo distanza temporale tra i due punti
            self.time.append(dist_temporale) #inserisco il valore nella lista time
            
        #reset dei grafici in modo da avere un grafico "pulito" per ogni acquisizione
        self.graphTimeWidget.clear()
        self.graphFrequencyWidget.clear()
        
        #controllo del valore inserito nella comboBox ovvero se Finite o Continuous per sapere la modalità di acquisizione selezionata dall'utente
        if self.comboBoxAcqMode.currentText() == "Finite":         #Acquisition mode = FINITE -> viene chiamato il relativo metodo
            self.finiteAcquisition()
            
        if self.comboBoxAcqMode.currentText() == "Continuous":     #Acquisition Mode = CONTINUOUS -> viene chiamato il relativo metodo
            self.continuousAcquisition()
    
    
    # PULSANTE PER AVVIARE IL GENERATORE DI FUNZIONI
    def pressedInitializeAWG(self, MainWindow):
        self.awg_created = True #setto a true perchè viene creato oggetto agilent
        self.buttonAWG.setEnabled(False)  #dopo che è stato premuto il pulsante initialize AWG, lo disabilito così non si crea un ulteriore oggetto agilent
        self.buttonGeneratore.setEnabled(True)      #abilito il pulsante per far partire il generatore di funzioni
        self.buttonGeneratore.setStyleSheet("background-color: green")    #setto di default lo sfondo verde
        self.spinBoxAmplitude.setReadOnly(False)   #abilito in scrittura lo spinBox per ampiezza
        self.spinBoxFreqGen.setReadOnly(False)     #abilito in scrittura lo spinBox per frequenza
        self.spinBoxOffset.setReadOnly(False)      #abilito in scrittura lo spinBox per offset
        
        self.wg = AgilentAWG()   #creo oggetto agilent
        

    # PULSANTE START PER CONTROLLARE IL GENERATORE DI FUNZIONI DA REMOTO
    def pressedStartGen(self, MainWindow):
       
        """********************* PARAMETRI SINUSOIDE ************************"""
  
        frequency = self.spinBoxFreqGen.value()
        amplitude = self.spinBoxAmplitude.value()
        offset = self.spinBoxOffset.value()
        
        """******************************************************************"""
       
        
        voltage_pp = 2*amplitude # peak to peak voltage
        # correggo i valori impostati se maggiori alle costanti definite all'inizio
        if np.abs(amplitude) > MAX_AMP: amplitude = MAX_AMP
        if np.abs(offset) > MAX_OFFSET: offset = 1*np.sign(MAX_OFFSET)
        if np.abs(frequency) > MAX_FREQ: frequency = MAX_FREQ
        
        # setto l'impedenza d'uscita dell'AWG 
        self.wg.write('OUTP:LOAD INF')
            
        
        # carico i parametri impostati sullo strumento
        self.wg.write('FREQ %.3f' % frequency) # frequenza sinusoide
        self.wg.write('VOLT %.3f' % voltage_pp) # tensione picco-picco
        self.wg.write('VOLT:OFFS %.3f' % offset) # offset
        
        
        # chiedo allo strumento se sta generando o no. Converto risultato in booleano
        # True: sta generando
        # False: non sta generando
        is_generating = bool(int(self.wg.query('OUTP?'))) 
        
        # se sta generando -> spengo
        if is_generating:
            self.wg.write('OUTP OFF')
            print("OUTPUT OFF")
            self.buttonGeneratore.setStyleSheet("background-color: green")
            self.buttonGeneratore.setText("START GEN")
        
        # se non sta generando -> accendo
        else:
            self.wg.write('OUTP ON')
            print("OUTPUT ON")
            self.buttonGeneratore.setStyleSheet("background-color: red")
            self.buttonGeneratore.setText("STOP GEN")

    
   #SALVA SU UN FILE FORMATO .png I DUE GRAFICI CHE VENGONO VISUALIZZATI SULL'INTERFACCIA
    def pressedSaveGraph(self, MainWindow):
        
        if self.is_started == True:      #controllo che sia stato premuto start, cioè si sia effettuata un acquisizione, per evitare di salvare un file vuoto
            
            #comando per spostarsi all'interno della cartella Saved_data (chdir sta infatti per CHange DIRectory)
            os.chdir(self.directory_path)    #in questo modo i file salvati saranno nella rispettiva cartella 
            
            text, ok = QInputDialog.getText(None, 'Save Graphs','Enter file name (with no extension):')   #viene creata una finestra di dialogo per permettere all'utente di inserire il nome del file su cui salvare i dati
            if ok and text != '':    #se ha premuto ok, e se ha inserito il nome, allora si salva la stringa inserita dall'utente nella variabile nomeFile
                nomeFile = text
            else:
                return
            
            #controllo se il file con questo nome esiste già nella cartella, se si aggiungo un numero progressivo al nome per non sovrascriverlo
            i=0
            nameTime = nomeFile + '_time_' + str(i) + '.png'  #inizializzo con 0 il primo salvato
            nameFreq = nomeFile + '_freq_' + str(i) + '.png'
            
            for file in os.listdir():       #ciclo su tutta la lista di file presenti nella cartella, e incremento i fino a che non trovo un numero non ancora usato
                
                #nome del file per grafico tempo e frequenza
                if os.path.isfile(nameTime) and os.path.isfile(nameFreq):  #dato che sono salvati sempre entrambi faccio controllo insieme
                    i = i + 1
                    nameTime = nomeFile + '_time_' + str(i) + '.png'
                    nameFreq = nomeFile + '_freq_' + str(i) + '.png'
                    
            #stampa immagine grafico nel dominio del tempo
            exporter_T = pg.exporters.ImageExporter(self.graphTimeWidget.plotItem)
            exporter_T.export(nameTime)
            
            #stampa immagine grafico nel dominio della frequenza
            exporter_F = pg.exporters.ImageExporter(self.graphFrequencyWidget.plotItem)
            exporter_F.export(nameFreq)
           
            self.show_popupSaved()      #se il salvataggio è andato a buon fine viene mostrato un popup per avvisare l'utente
        
        else:
            self.show_popupNoAcquisition()       #popup mostrato se l'utente cerca di salvare prima di acquisire dati
            
    
    #SALVA SU DUE FILE FORMATO .csv, un file per il dominio del tempo e uno per quello della frequenza 
    def pressedSaveFile(self, MainWindow):      
        
        if self.is_started == True:     #controllo che sia stato premuto start, cioè si sia effettuata un acquisizione, per evitare di salvare un file vuoto
            
            #comando per spostarsi all'interno della cartella Saved_data (chdir sta infatti per CHange DIRectory)
            os.chdir(self.directory_path)    #in questo modo i file salvati saranno nella rispettiva cartella 
            
            text, ok = QInputDialog.getText(None, 'Save File','Enter file name (with no extension):')      #viene creata una finestra di dialogo per permettere all'utente di inserire il nome del file su cui salvare i dati
            if ok and text != '':       #se ha premuto ok, e se ha inserito il nome, allora si salva la stringa inserita dall'utente nella variabile nomeFile
                nomeFile = text
            else:
                return
            
            #controllo se il file con questo nome esiste già nella cartella, se si aggiungo un numero progressivo al nome per non sovrascriverlo
            i=0
            nameTime = nomeFile + '_time_' + str(i) + '.csv'  #inizializzo con 0 il primo salvato
            nameFreq = nomeFile + '_freq_' + str(i) + '.csv'
            
            for file in os.listdir():       #ciclo su tutta la lista di file presenti nella cartella, e incremento i fino a che non trovo un numero non ancora usato
                
                #nome del file per grafico tempo e frequenza
                if os.path.isfile(nameTime) and os.path.isfile(nameFreq):  #dato che sono salvati sempre entrambi faccio controllo insieme
                    i = i + 1
                    nameTime = nomeFile + '_time_' + str(i) + '.csv'
                    nameFreq = nomeFile + '_freq_' + str(i) + '.csv'
            
            
            testo = self.textEdit.toPlainText()     #se l'utente inserisce delle note, questo comando permette di prendere il testo scritto nell'apposita finestra sull'interfaccia e salvarlo in una variabile
               
            # SALVATAGGIO DATI NEL DOMINIO DEL TEMPO
            with open(nameTime, 'w', newline='') as filetime:    # apertura del file, viene aggiunto il suffisso '_time' al nome digitato dall'utente
                thewriter = csv.writer(filetime, delimiter =',')    #creazione dell'oggetto writer che permette la scrittura sul file
                
                if testo != '':                 #se l'utente ha aggiunto delle note vengono salvate nel file
                    thewriter.writerow(['NOTE: ' + testo])
                
                # scritta del "titolo" del file, quindi l'intestazione delle colonne
                titolo = 'Time_(s)'
                for channel in active_channels:
                    titolo += ' Voltage_(V)_' + channel
                
                line = titolo.split(' ')
                thewriter.writerow(line)
                
                spazio = ' '       #questo spazio serve poi per creare la stringa riga e poi spezzarla quando incontra un carattere di spaziatura
                
                #scrittura dei dati acquisiti dallo strumento
                if len(active_channels) == 1:          #se solo un canale, ho una sola lista non serve doppio ciclo
                    i=0
                    while i < n_input:
                        riga = str(self.time[i])
                        riga += spazio + str(self.data[i])
                    
                        line = riga.split(' ')
                        thewriter.writerow(line)
                        i=i+1
                
                if len(active_channels) > 1:       #ho una lista di liste, quindi servono due cicli annidati
                    i=0    #questo indice serve per scorrere gli elementi di ciascuna lista
                    while i < n_input:
                        riga = str(self.time[i])
                        j=0     #indice che serve per scorrere il numero di canali (self.data e sel.active_channels hanno la stessa lunghezza)
                        while j < len(self.data):
                            riga += spazio + str(self.data[j][i])       #considero l'elemento i-esimo della lista j-esima e lo aggiungo alla riga
                            j = j + 1   #incremeno j per passare a canale successivo
                       
                        line = riga.split(' ')      
                        thewriter.writerow(line)        #scrivo nella riga tutti gli elementi relativi al tempo i-esimo
                        i=i+1  #incremento i per passare a istante successivo
                
                
                 # SALVATAGGIO DATI NEL DOMINIO DELLA FREQUENZA
            with open(nameFreq, 'w', newline='') as filefreq:     # apertura del file, viene aggiunto il suffisso '_freq' al nome digitato dall'utente
                thewriter = csv.writer(filefreq, delimiter =',')        #creazione dell'oggetto writer che permette la scrittura sul file
                
                if testo != '':             #se l'utente ha aggiunto delle note vengono salvate nel file
                    thewriter.writerow(['NOTE: ' + testo])
                    
                # scritta del "titolo" del file, quindi l'intestazione delle colonne 
                titolo = 'Frequency_(Hz)'
                for channel in active_channels:
                   titolo += ' Magnitude_(dBV)_' + channel
        
                line = titolo.split(' ')
                thewriter.writerow(line)

                spazio = ' '           #questo spazio serve poi per creare la stringa riga e poi spezzarla quando incontra un carattere di spaziatura
                
                #scrittura dei valori ottenuti calcolando la trasformata di Fourier dei dati acquisiti
                if len(active_channels) == 1:          #se solo un canale, ho una sola lista non serve doppio ciclo
                    i=0
                    while i < len(self.x_Fourier_CH):
                        riga = str(self.x_Fourier_CH[i])        #valore relativo alla frequenza calcolata
                        riga += spazio + str(self.data_dBV[0][i])      #aggiungo valore convertito in dBV
                    
                        line = riga.split(' ')
                        thewriter.writerow(line)
                        i=i+1
                    
                if len(active_channels) > 1:       #ho una lista di liste, quindi servono due cicli annidati
                    i=0    #questo indice serve per scorrere gli elementi di ciascuna lista
                    while i < len(self.x_Fourier_CH):       #per determinare la lunghezza di una lista considero
                        riga = str(self.x_Fourier_CH[i])
                        j=0     #indice che serve per scorrere il numero di canali (self.data_dBV e self.active_channels hanno la stessa lunghezza)
                        while j < len(self.data_dBV):   
                            riga += spazio + str(self.data_dBV[j][i])       #considero l'elemento i-esimo della lista j-esima e lo aggiungo alla riga
                            j = j + 1   #incremeno j per passare a canale successivo
                       
                        line = riga.split(' ')      
                        thewriter.writerow(line)        #scrivo nella riga tutti gli elementi relativi alla frequenza i-esima
                        i=i+1  #incremento i per passare a frequenza successiva
                        
            self.show_popupSaved()            #se il salvataggio è andato a buon fine viene mostrato un popup per avvisare l'utente
        
        else:
            self.show_popupNoAcquisition()      #popup mostrato se l'utente cerca di salvare prima di acquisire dati
        
   
    # FUNZIONE PER CALCOLO TRASFORMATA DI FOURIER
    
    def fourierTransform(self):
        
        #viene creata una lista di liste, il cui numero di liste varia a seconda di quanti canali attivi ci sono
        self.data_dBV = [[] for i in range(len(active_channels))]      #lista di liste che serve per tenere traccia di tutti i dati di cui si è effettuata la fft e la conversione in dBV
        
        xf = fftfreq(n_input, 1/sample_rate)        #calcolo delle frequenze, vale per tutti i canali in quanto le frequenze sono le stesse, e per entrambe le modalità di acquisizione
        self.x_Fourier_CH = xf[:n_input//2]
        
        if len(active_channels) == 1:  #se ho solo un canale attivo non ho bisogno di ciclare sui canali

            #calcolo della trasformata di Fourier dei dati acquisiti nel dominio del tempo
            # windowing, windows correction factors -> https://community.sw.siemens.com/s/article/window-correction-factors
            
            # rettangolare o uniforme (come non farlo)
            if self.comboBoxWindowing.currentText() == "Rectangular":
                window, ampl_corr = np.ones(len(self.data)), 1.0
            
            # hanning
            if self.comboBoxWindowing.currentText() == "Hanning":
                window, ampl_corr = np.hanning(len(self.data)), 2.0

            # hamming
            if self.comboBoxWindowing.currentText() == "Hamming":
                window, ampl_corr = np.hamming(len(self.data)), 1.85

            # blackman
            if self.comboBoxWindowing.currentText() == "Blackman":
                window, ampl_corr = np.blackman(len(self.data)), 2.80
            
            yf = ampl_corr * fft(np.multiply(self.data, window))                     
            self.y_Fourier_CH = 2*abs(yf[:n_input//2]/n_input)
            
            #conversione in dBV del valore calcolato nella riga precedente, e inserisco il valore nella lista data_dBV
            i=0
            while i < len(self.y_Fourier_CH):
                self.data_dBV[0].append(20*math.log10(self.y_Fourier_CH[i]))
                i = i + 1
                
            #visualizzazione a video del grafico della trasformata, nel dominio delle frequenze
            self.graphFrequencyWidget.plot(self.x_Fourier_CH, self.data_dBV[0], pen=pg.mkPen(color='r'),  name = active_channels[0]) 
                 
        #con più di un canale attivo serve un doppio ciclo, uno esterno per ciclare sulla lista di un determinato canale, e un altro interno per ciclare sugli elementi della lista e calcolarne la trasformata
        if len(active_channels) > 1:  #se ho più canali ciclo su questi per stampare a video i rispettivi grafici
            
            i = 0       #indice che scorre sul numero di canali, perchè ho una lista per ogni canale
            while i < len(self.data):   #per la lista letta in ogni canale devo calcolare la trasformata dei valori acquisiti
                j=0     #indice che scorre sugli elementi della lista di un canale
                #calcolo della trasformata di Fourier dei dati acquisiti nel dominio del tempo, per un canale alla volta
                # windowing, windows correction factors -> https://community.sw.siemens.com/s/article/window-correction-factors
                
                # rettangolare o uniforme (come non farlo)
                if self.comboBoxWindowing.currentText() == "Rectangular":
                    window, ampl_corr = np.ones(len(self.data[i])), 1.0
                
                # hanning
                if self.comboBoxWindowing.currentText() == "Hanning":
                    window, ampl_corr = np.hanning(len(self.data[i])), 2.0
    
                # hamming
                if self.comboBoxWindowing.currentText() == "Hamming":
                    window, ampl_corr = np.hamming(len(self.data[i])), 1.85
    
                # blackman
                if self.comboBoxWindowing.currentText() == "Blackman":
                    window, ampl_corr = np.blackman(len(self.data[i])), 2.80
                
                yf = ampl_corr * fft(np.multiply(self.data[i], window))                                                     
                self.y_Fourier_CH = 2*abs(yf[:n_input//2]/n_input)
                    
                #conversione in dBV del valore calcolato nella riga precedente, ciclo su ogni elemento della lista quindi serve l'indice j per ciclare sui valori di y_Fourier_CH
                while j < len(self.y_Fourier_CH):
                    self.y_Fourier_CH[j] = 20*math.log10(self.y_Fourier_CH[j])  #conversione in dBV del valore calcolato
                    self.data_dBV[i].append(self.y_Fourier_CH[j])   #inserzione del valore convertito in dBV, nella lista di liste
                    j = j + 1       #incremento di j per passare all'elemento successivo della lista
                
                #visualizzazione a video del grafico della trasformata, nel dominio delle frequenze
                self.graphFrequencyWidget.plot(self.x_Fourier_CH, self.data_dBV[i], pen=pg.mkPen(color=self.colors[i]),  name = active_channels[i]) 
                i = i + 1       #incremento i per ripetere il calcolo sui valori acquisiti nel canale successivo
        

    #FUNZIONI DI ACQUISIZIONE IN MODALITA' FINITA E CONTINUA
    
    def finiteAcquisition(self):
        
        with nidaqmx.Task() as task:   #creazione del task per leggere i valori
                
            #aggiunta dei canali che sono stati selezionati dall'utente  
            for channel in active_channels:
                task.ai_channels.add_ai_voltage_chan(channel)
  
            task.timing.cfg_samp_clk_timing(sample_rate, samps_per_chan = n_input)    #configurazione del clock
            
            self.data = task.read(number_of_samples_per_channel = n_input)      #lettura, ritorna una lista contente i valori acquisiti, nel caso di più canali da acquisire contemporaneamente, ritorna una lista di liste
        
        if len(active_channels) == 1:  #se ho solo un canale attivo non ho bisogno di ciclare
            self.graphTimeWidget.plot(self.time, self.data, pen=pg.mkPen(color='r'), name = active_channels[0])  #stampa sull'interfaccia del grafico
        
        if len(active_channels) > 1:   #se ho più canali ciclo su questi per stampare a video i rispettivi grafici
            
            i = 0
            while i < len(active_channels):
                self.graphTimeWidget.plot(self.time, self.data[i], pen = pg.mkPen(color = self.colors[i]), name = active_channels[i]) #in questo caso per l'oggetto penna ciclo sul vettore self.colors in modo da avere un colore diverso per ogni grafico
                i = i + 1

        self.fourierTransform()     #chiamo la funzione per calcolare la transformata di Fourier
        
        
    #in questa modalità il pulsante START ha due funzioni, avvia e termina l'esecuzione, quindi è necessario fare un controllo sul testo presentato sul pulsante
    def continuousAcquisition(self):
            
        #se il pulsante presenta la scritta "STOP" bisogna terminare l'acquisizione
        if self.buttonStart.text() == "STOP":
            self.worker.requestInterruption()                   #viene fatta richiesta di interruzione al thread, che interrompe il ciclo e non avendo altre operazioni da eseguire, termina inviando un segnale alla classe principale
            self.worker.finished.connect(self.evt_finished)     #il segnale finished emesso dal thread quando finisce la sua esecuzione viene connesso al relativo slot
        
        #se il pulsante presenta la scritta "START" si inizia l'acquisizione
        if self.buttonStart.text() == "START":
            #si cambia la grafica del pulsante, mettendo sfondo rosso con scritta "STOP"
            self.buttonStart.setStyleSheet("background-color: red")
            self.buttonStart.setText("STOP")
        
            self.worker = WorkerThread()        #viene creato il thread da eseguire per acquisire i dati
            self.worker.start()                 #si avvia il thread
            self.worker.update_acquisition.connect(self.evt_update)     #ogni volta che il thread termina un'iterazione invia il segnale update_acqusition che viene connesso al relativo slot
    
    
    #slot che viene eseguito quando il thread termina la sua esecuzione
    def evt_finished(self):
        #viene cambiata la grafica del pulsante, rimettendo sfondo verde e scritta "START", così l'utente può nuovamente acquisire dati
        self.buttonStart.setStyleSheet("background-color: green")
        self.buttonStart.setText("START")


    #slot che viene eseguito ogni volta che il thread termina un'iterazione, mostra i dati acquisiti sul grafico e salva i valori nelle rispettive liste di dati
    def evt_update(self, val):          #val è la lista contenente la lista "data" emessa dal segnale update_acquisition all'interno del thread
        
        self.graphTimeWidget.clear()        #reset dei due grafici sull'interfaccia per evitare che i grafici si sovrappongano
        self.graphFrequencyWidget.clear()
        
        self.data = val    #salvataggio dei dati emessi dal thread in una variabile temporanea in modo che possano essere visti ed elaborati dal metodo "fourierTransform", sarà una lista se ho solo un canale, una lista di liste se più canali
        
        if len(active_channels) == 1:
            self.graphTimeWidget.plot(self.time, self.data,  pen=pg.mkPen(color='r'), name = active_channels[0]) #viene mostrato a video "data" perchè contine gli n_input acquisiti durante un'iterazione
        
        if len(active_channels) > 1:
            i=0     #indice per ciclare sui canali attivi
            while i < len(active_channels):        #per ogni canale salvo la lista "data" acquisita nel thread
                self.graphTimeWidget.plot(self.time, self.data[i], pen = pg.mkPen(color = self.colors[i]), name = active_channels[i]) #in questo caso per l'oggetto penna ciclo sul vettore self.colors in modo da avere un colore diverso per ogni grafico
                i = i + 1
        
        self.fourierTransform()     #chiamata al metodo che calcola la trasformata di Fourier, viene fatta in questo slot per poter visualizzare anche il grafico nel dominio della frequenza in modo continuo


    
    #FUNZIONE CHIAMATA QUANDO UTENTE CLICCA SULLA X DELLA MAINWINDOW
    def closeEvent(self):
        
        #eliminazione oggetto awg ed eventuale stop del generatore se l'utente si è dimenticato
        if self.awg_created == True:   #se l'oggetto awg è stato creato lo elimino
            if self.buttonGeneratore.text() ==  "STOP GEN":  #se l'utente si è dimenticato di premere si stoppa in automatico il generatore di funzioni
                self.wg.write('OUTP OFF')
                print("OUTPUT OFF")
            self.wg.close()    #elimino oggetto awg
            
        #eventuale stop dell'acquisizione in modalità continua se utente si dimentica di premere stop
        if self.comboBoxAcqMode.currentText() == "Continuous" and self.buttonStart.text() == "STOP":
            self.worker.requestInterruption()              #viene fatta richiesta di interruzione al thread, che interrompe il ciclo e non avendo altre operazioni da eseguire, termina inviando un segnale alla classe principale
 
    
    # TRADUZIONE NOMI SULLA GUI (Fatta da Qtdesigner)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.labelWindowing.setText(_translate("MainWindow", "FFT Windowing"))
        self.buttonGeneratore.setText(_translate("MainWindow", "START GEN"))
        self.buttonChannel.setText(_translate("MainWindow", "Add Channels"))
        self.labelsamplesToRead.setText(_translate("MainWindow", "Samples To Read"))
        self.buttonStart.setText(_translate("MainWindow", "START"))
        self.buttonSaveFile.setText(_translate("MainWindow", "SAVE TEXTFILE"))
        self.labelRate.setText(_translate("MainWindow", "Rate (kS/s)"))
        self.comboBoxAcqMode.setItemText(0, _translate("MainWindow", "Finite"))
        self.comboBoxAcqMode.setItemText(1, _translate("MainWindow", "Continuous"))
        self.comboBoxWindowing.setItemText(0, _translate("MainWindow", "Rectangular"))
        self.comboBoxWindowing.setItemText(1, _translate("MainWindow", "Hanning"))
        self.comboBoxWindowing.setItemText(2, _translate("MainWindow", "Hamming"))
        self.comboBoxWindowing.setItemText(3, _translate("MainWindow", "Blackman"))
        self.labelOffset.setText(_translate("MainWindow", "Offset (V)"))
        self.labelNote.setText(_translate("MainWindow", "Note"))
        self.labelMode.setText(_translate("MainWindow", "Acquisition Mode"))
        self.labelCh.setText(_translate("MainWindow", "Channels"))
        self.labelFrequencyGen.setText(_translate("MainWindow", "Frequency (Hz)"))
        self.labelAmplitude.setText(_translate("MainWindow", "Amplitude (V)"))
        
        self.buttonAWG.setText(_translate("MainWindow", "Initialize AWG"))
        self.buttonSaveGraph.setText(_translate("MainWindow", "SAVE GRAPH"))
        
        # # PER EVENTUALE TRIGGER
        # self.labelTriggerLevel.setText(_translate("MainWindow", "Trigger Level"))
        # self.buttonTrigger.setText(_translate("MainWindow", "START TRIGGER"))


#CLASSE GENERALE CHE PERMETTE DI RIDEFINIRE METODO closeEvent E CHIUDERE DALLA FINESTRA PRINCIPALE TUTTE LE ALTRE FINESTRE APERTE
class MyWindow(QtGui.QMainWindow):
    def closeEvent(self, event):
        app.closeAllWindows()
    
    
#CLASSE DELLA FINESTRA PER AGGIUNTA DEI CANALI
class WindowChannel(QWidget):
    
    def __init__(self):
        super(). __init__()
        self.setWindowTitle("Available Channels")
        self.resize(500, 600)
        self.layout = QBoxLayout(QBoxLayout.TopToBottom)
        
        for channel in ai_channels_list:         #aggiunta delle checkBox al layout, vengono create tante checkboxes quanti sono i canali disponibili nel sistema
            self.ch = QCheckBox(channel, self)
            self.ch.setEnabled(True)
            font = QtGui.QFont()
            font.setPointSize(14)
            font.setKerning(True)
            self.ch.setFont(font)
            self.layout.addWidget(self.ch, 0)
            
        self.button = QPushButton("Enter", self)    #aggiungo bottone al layout per confermare quali checkboxes sono state selezionate 
        self.button.resize(150,60)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setKerning(True)
        self.button.setFont(font)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)   #setto il layout
        
        global checked_ch    #lista globale che contiene i canali selezionati per aggiungerli nella lista quando l'utente preme start
        checked_ch = []
        self.button.clicked.connect(self.buttonClicked)   #collegameto slot per quando utente preme enter

    def buttonClicked(self):    #quando viene cliccato bottone enter si memorizzano nella lista checked_ch le checkBox che sono state selezionate dall'utente
     
        for i in range(self.layout.count()):
            chBox = self.layout.itemAt(i).widget()
            if chBox.isChecked() == True and chBox.text() not in checked_ch:    #se canale è selezionato e non è presente nella lista lo aggiungo
                    checked_ch.append(chBox.text())  
            if chBox.isChecked() == False and chBox.text() in checked_ch:       #se canale prima era stato selezionato, quindi era presente nella lista, e viene poi deselezionato, lo rimuovo
                checked_ch.remove(chBox.text()) 
        self.showMinimized()   #dopo aver premuto enter riduco a icona la finestra dei canali
        
        
#THREAD creato nella modalità di acquisizione continua, per permettere all'utente di interagire con l'interfaccia mentre vengono generati i dati
class WorkerThread(QThread):
    update_acquisition = pyqtSignal(list)       #creo segnale apposito che il thread emette quando finisce un'iterazione del ciclo while, 
                                                #è un segnale che emette un valore di tipo lista
    
    def run(self):
        with nidaqmx.Task() as task:        #creazione del task per leggere i valori
            #aggiunta dei canali che sono stati selezionati dall'utente
            for channel in active_channels:
                task.ai_channels.add_ai_voltage_chan(channel)
            
            task.timing.cfg_samp_clk_timing(sample_rate, sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan = n_input)  #configurazione del clock, il valore samps_per_chan serve a determinare la grandezza del buffer
            
            #questo ciclo termina quando l'utente preme il pulsante STOP, quindi quando viene fatta richiesta di interruzione con self.worker.requestInterruption() nel metodo continuousAcquisition
            while not self.isInterruptionRequested():
                data = task.read(number_of_samples_per_channel = n_input)   #lettura dati, ritorna una lista contente i dati acquisiti se c'è solo un canale da leggere, una lista di liste se sono attivi più canali
                self.update_acquisition.emit(data)  #emissione segnale verso la GUI che lo connette al relativo slot per elaborare i dati acquisiti


#CLASSE DEL GENERATORE DI FUNZIONI
class AgilentAWG(object):
    """
    Classe per comunicare con l'AWG Agilent Arbitrary Waveform Generator 33250A
      
    """
    
    """inizializzazione"""
    def __init__(self, dev = u'GPIB0::%i::INSTR' % AWG_GPIB_ADDRESS):

        self.rm = visa.ResourceManager()
        #use self.rm.list_resources() to find resources
        self.ag = self.rm.open_resource(dev)

        self.ag.write('*IDN?')
        print(self.ag.read())
        

    def close(self):
        self.ag.close()
    
    def write(self, txt):
        """
        scrive i comandi in modalità testo
        """
        self.ag.write(txt)  

    def read(self):
        """Legge i dati"""
        return self.ag.read()
    
    def query(self, txt):
        """Scrive e legge i dati"""
        return self.ag.query(txt)
    
    
if __name__ == "__main__":
    
    app=0   #evita il crash del kernel alla chiusura della GUI
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWindow()  #definisco MainWindow con la classe MyWindow() per ridefinire cos' il metodo closeEvent() della finestra principale
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    #MainWindow.showMaximized()
    app.exec_()

