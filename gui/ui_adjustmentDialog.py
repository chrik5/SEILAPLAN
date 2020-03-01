# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/adjustmentDialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AdjustmentDialogUI(object):
    def setupUi(self, AdjustmentDialogUI):
        AdjustmentDialogUI.setObjectName("AdjustmentDialogUI")
        AdjustmentDialogUI.resize(591, 459)
        AdjustmentDialogUI.setFocusPolicy(QtCore.Qt.ClickFocus)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/SeilaplanPlugin/gui/icons/icon_app.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AdjustmentDialogUI.setWindowIcon(icon)
        self.gridLayout_2 = QtWidgets.QGridLayout(AdjustmentDialogUI)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.recalcStatus_ico = QtWidgets.QLabel(AdjustmentDialogUI)
        self.recalcStatus_ico.setText("")
        self.recalcStatus_ico.setPixmap(QtGui.QPixmap(":/plugins/SeilaplanPlugin/gui/icons/icon_reload.png"))
        self.recalcStatus_ico.setObjectName("recalcStatus_ico")
        self.horizontalLayout_3.addWidget(self.recalcStatus_ico)
        self.recalcStatus_txt = QtWidgets.QLabel(AdjustmentDialogUI)
        self.recalcStatus_txt.setObjectName("recalcStatus_txt")
        self.horizontalLayout_3.addWidget(self.recalcStatus_txt)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.label_18 = QtWidgets.QLabel(AdjustmentDialogUI)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.gridLayout_2.addWidget(self.label_18, 5, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnBackToStart = QtWidgets.QPushButton(AdjustmentDialogUI)
        self.btnBackToStart.setAutoDefault(False)
        self.btnBackToStart.setObjectName("btnBackToStart")
        self.horizontalLayout_2.addWidget(self.btnBackToStart)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.btnClose = QtWidgets.QPushButton(AdjustmentDialogUI)
        self.btnClose.setAutoDefault(False)
        self.btnClose.setObjectName("btnClose")
        self.horizontalLayout_2.addWidget(self.btnClose)
        self.btnSave = QtWidgets.QPushButton(AdjustmentDialogUI)
        self.btnSave.setAutoDefault(False)
        self.btnSave.setObjectName("btnSave")
        self.horizontalLayout_2.addWidget(self.btnSave)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 8, 0, 1, 1)
        self.plotLayout = QtWidgets.QVBoxLayout()
        self.plotLayout.setSpacing(0)
        self.plotLayout.setObjectName("plotLayout")
        self.gridLayout_2.addLayout(self.plotLayout, 4, 0, 1, 1)
        self.tabLayout = QtWidgets.QVBoxLayout()
        self.tabLayout.setObjectName("tabLayout")
        self.tabWidget = QtWidgets.QTabWidget(AdjustmentDialogUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setBaseSize(QtCore.QSize(0, 0))
        self.tabWidget.setObjectName("tabWidget")
        self.tabPoles = QtWidgets.QWidget()
        self.tabPoles.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.tabPoles.setObjectName("tabPoles")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tabPoles)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_17 = QtWidgets.QLabel(self.tabPoles)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.verticalLayout_5.addWidget(self.label_17)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        self.poleGrid = QtWidgets.QHBoxLayout()
        self.poleGrid.setObjectName("poleGrid")
        self.poleVGrid = QtWidgets.QVBoxLayout()
        self.poleVGrid.setObjectName("poleVGrid")
        self.poleHgridHeader = QtWidgets.QHBoxLayout()
        self.poleHgridHeader.setObjectName("poleHgridHeader")
        spacerItem2 = QtWidgets.QSpacerItem(35, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.poleHgridHeader.addItem(spacerItem2)
        self.label_19 = QtWidgets.QLabel(self.tabPoles)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy)
        self.label_19.setMinimumSize(QtCore.QSize(20, 0))
        self.label_19.setMaximumSize(QtCore.QSize(20, 16777215))
        self.label_19.setObjectName("label_19")
        self.poleHgridHeader.addWidget(self.label_19)
        self.label_31 = QtWidgets.QLabel(self.tabPoles)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_31.sizePolicy().hasHeightForWidth())
        self.label_31.setSizePolicy(sizePolicy)
        self.label_31.setMinimumSize(QtCore.QSize(200, 30))
        self.label_31.setLineWidth(1)
        self.label_31.setIndent(2)
        self.label_31.setObjectName("label_31")
        self.poleHgridHeader.addWidget(self.label_31)
        self.label_35 = QtWidgets.QLabel(self.tabPoles)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_35.sizePolicy().hasHeightForWidth())
        self.label_35.setSizePolicy(sizePolicy)
        self.label_35.setMinimumSize(QtCore.QSize(95, 30))
        self.label_35.setIndent(2)
        self.label_35.setObjectName("label_35")
        self.poleHgridHeader.addWidget(self.label_35)
        self.label_30 = QtWidgets.QLabel(self.tabPoles)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_30.sizePolicy().hasHeightForWidth())
        self.label_30.setSizePolicy(sizePolicy)
        self.label_30.setMinimumSize(QtCore.QSize(95, 30))
        self.label_30.setIndent(2)
        self.label_30.setObjectName("label_30")
        self.poleHgridHeader.addWidget(self.label_30)
        self.label_36 = QtWidgets.QLabel(self.tabPoles)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_36.sizePolicy().hasHeightForWidth())
        self.label_36.setSizePolicy(sizePolicy)
        self.label_36.setMinimumSize(QtCore.QSize(60, 30))
        self.label_36.setIndent(2)
        self.label_36.setObjectName("label_36")
        self.poleHgridHeader.addWidget(self.label_36)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.poleHgridHeader.addItem(spacerItem3)
        self.poleVGrid.addLayout(self.poleHgridHeader)
        self.poleGrid.addLayout(self.poleVGrid)
        self.verticalLayout_6.addLayout(self.poleGrid)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem4)
        self.tabWidget.addTab(self.tabPoles, "")
        self.tabCableline = QtWidgets.QWidget()
        self.tabCableline.setObjectName("tabCableline")
        self.gridLayout = QtWidgets.QGridLayout(self.tabCableline)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_14 = QtWidgets.QLabel(self.tabCableline)
        self.label_14.setObjectName("label_14")
        self.gridLayout_3.addWidget(self.label_14, 5, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.tabCableline)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.tabCableline)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 0, 2, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.tabCableline)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 5, 0, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem5, 0, 3, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.tabCableline)
        self.label_11.setObjectName("label_11")
        self.gridLayout_3.addWidget(self.label_11, 2, 2, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.tabCableline)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 6, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.tabCableline)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 1, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.tabCableline)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 2, 0, 1, 1)
        self.fieldqZ = QtWidgets.QLineEdit(self.tabCableline)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fieldqZ.sizePolicy().hasHeightForWidth())
        self.fieldqZ.setSizePolicy(sizePolicy)
        self.fieldqZ.setMinimumSize(QtCore.QSize(80, 0))
        self.fieldqZ.setMaximumSize(QtCore.QSize(80, 16777215))
        self.fieldqZ.setObjectName("fieldqZ")
        self.gridLayout_3.addWidget(self.fieldqZ, 4, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.tabCableline)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 1, 2, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.tabCableline)
        self.label_13.setObjectName("label_13")
        self.gridLayout_3.addWidget(self.label_13, 4, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.tabCableline)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 7, 0, 1, 1)
        self.fieldqT = QtWidgets.QLineEdit(self.tabCableline)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fieldqT.sizePolicy().hasHeightForWidth())
        self.fieldqT.setSizePolicy(sizePolicy)
        self.fieldqT.setMinimumSize(QtCore.QSize(80, 0))
        self.fieldqT.setMaximumSize(QtCore.QSize(80, 16777215))
        self.fieldqT.setObjectName("fieldqT")
        self.gridLayout_3.addWidget(self.fieldqT, 1, 1, 1, 1)
        self.fieldBabstMin = QtWidgets.QLineEdit(self.tabCableline)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fieldBabstMin.sizePolicy().hasHeightForWidth())
        self.fieldBabstMin.setSizePolicy(sizePolicy)
        self.fieldBabstMin.setMinimumSize(QtCore.QSize(80, 0))
        self.fieldBabstMin.setMaximumSize(QtCore.QSize(80, 16777215))
        self.fieldBabstMin.setObjectName("fieldBabstMin")
        self.gridLayout_3.addWidget(self.fieldBabstMin, 7, 1, 1, 1)
        self.fieldA = QtWidgets.QLineEdit(self.tabCableline)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fieldA.sizePolicy().hasHeightForWidth())
        self.fieldA.setSizePolicy(sizePolicy)
        self.fieldA.setMinimumSize(QtCore.QSize(80, 0))
        self.fieldA.setMaximumSize(QtCore.QSize(80, 16777215))
        self.fieldA.setObjectName("fieldA")
        self.gridLayout_3.addWidget(self.fieldA, 2, 1, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.tabCableline)
        self.label_15.setObjectName("label_15")
        self.gridLayout_3.addWidget(self.label_15, 6, 2, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.tabCableline)
        self.label_22.setObjectName("label_22")
        self.gridLayout_3.addWidget(self.label_22, 7, 2, 1, 1)
        self.fieldqR = QtWidgets.QLineEdit(self.tabCableline)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fieldqR.sizePolicy().hasHeightForWidth())
        self.fieldqR.setSizePolicy(sizePolicy)
        self.fieldqR.setMinimumSize(QtCore.QSize(80, 0))
        self.fieldqR.setMaximumSize(QtCore.QSize(80, 16777215))
        self.fieldqR.setObjectName("fieldqR")
        self.gridLayout_3.addWidget(self.fieldqR, 5, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.tabCableline)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 4, 0, 1, 1)
        self.fieldQ = QtWidgets.QLineEdit(self.tabCableline)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fieldQ.sizePolicy().hasHeightForWidth())
        self.fieldQ.setSizePolicy(sizePolicy)
        self.fieldQ.setMinimumSize(QtCore.QSize(80, 0))
        self.fieldQ.setMaximumSize(QtCore.QSize(80, 16777215))
        self.fieldQ.setObjectName("fieldQ")
        self.gridLayout_3.addWidget(self.fieldQ, 0, 1, 1, 1)
        self.fieldVorsp = QtWidgets.QLineEdit(self.tabCableline)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fieldVorsp.sizePolicy().hasHeightForWidth())
        self.fieldVorsp.setSizePolicy(sizePolicy)
        self.fieldVorsp.setMinimumSize(QtCore.QSize(80, 0))
        self.fieldVorsp.setMaximumSize(QtCore.QSize(80, 16777215))
        self.fieldVorsp.setObjectName("fieldVorsp")
        self.gridLayout_3.addWidget(self.fieldVorsp, 6, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.tabCableline)
        self.label_12.setObjectName("label_12")
        self.gridLayout_3.addWidget(self.label_12, 3, 0, 1, 1)
        self.fieldMBK = QtWidgets.QLineEdit(self.tabCableline)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fieldMBK.sizePolicy().hasHeightForWidth())
        self.fieldMBK.setSizePolicy(sizePolicy)
        self.fieldMBK.setMinimumSize(QtCore.QSize(80, 0))
        self.fieldMBK.setMaximumSize(QtCore.QSize(80, 16777215))
        self.fieldMBK.setObjectName("fieldMBK")
        self.gridLayout_3.addWidget(self.fieldMBK, 3, 1, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.tabCableline)
        self.label_23.setObjectName("label_23")
        self.gridLayout_3.addWidget(self.label_23, 3, 2, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem6, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tabCableline, "")
        self.tabThreshold = QtWidgets.QWidget()
        self.tabThreshold.setObjectName("tabThreshold")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.tabThreshold)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.label_21 = QtWidgets.QLabel(self.tabThreshold)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_21.setFont(font)
        self.label_21.setObjectName("label_21")
        self.verticalLayout_12.addWidget(self.label_21)
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableThresholds = QtWidgets.QTableView(self.tabThreshold)
        self.tableThresholds.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableThresholds.sizePolicy().hasHeightForWidth())
        self.tableThresholds.setSizePolicy(sizePolicy)
        self.tableThresholds.setMinimumSize(QtCore.QSize(0, 240))
        self.tableThresholds.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Switzerland))
        self.tableThresholds.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tableThresholds.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.tableThresholds.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.tableThresholds.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.tableThresholds.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableThresholds.setAutoScroll(True)
        self.tableThresholds.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableThresholds.setProperty("showDropIndicator", False)
        self.tableThresholds.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableThresholds.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableThresholds.setWordWrap(True)
        self.tableThresholds.setCornerButtonEnabled(False)
        self.tableThresholds.setObjectName("tableThresholds")
        self.tableThresholds.horizontalHeader().setHighlightSections(False)
        self.tableThresholds.horizontalHeader().setStretchLastSection(True)
        self.tableThresholds.verticalHeader().setVisible(False)
        self.tableThresholds.verticalHeader().setMinimumSectionSize(40)
        self.horizontalLayout.addWidget(self.tableThresholds)
        spacerItem7 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem7)
        self.verticalLayout_11.addLayout(self.horizontalLayout)
        self.label_20 = QtWidgets.QLabel(self.tabThreshold)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_20.setFont(font)
        self.label_20.setObjectName("label_20")
        self.verticalLayout_11.addWidget(self.label_20)
        spacerItem8 = QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_11.addItem(spacerItem8)
        self.verticalLayout_12.addLayout(self.verticalLayout_11)
        self.tabWidget.addTab(self.tabThreshold, "")
        self.tabComment = QtWidgets.QWidget()
        self.tabComment.setObjectName("tabComment")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tabComment)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_16 = QtWidgets.QLabel(self.tabComment)
        self.label_16.setObjectName("label_16")
        self.verticalLayout_3.addWidget(self.label_16)
        self.fieldComment = QtWidgets.QPlainTextEdit(self.tabComment)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fieldComment.sizePolicy().hasHeightForWidth())
        self.fieldComment.setSizePolicy(sizePolicy)
        self.fieldComment.setMaximumSize(QtCore.QSize(16777215, 120))
        self.fieldComment.setObjectName("fieldComment")
        self.verticalLayout_3.addWidget(self.fieldComment)
        spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem9)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.tabWidget.addTab(self.tabComment, "")
        self.tabLayout.addWidget(self.tabWidget)
        self.gridLayout_2.addLayout(self.tabLayout, 6, 0, 1, 1)

        self.retranslateUi(AdjustmentDialogUI)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(AdjustmentDialogUI)

    def retranslateUi(self, AdjustmentDialogUI):
        _translate = QtCore.QCoreApplication.translate
        AdjustmentDialogUI.setWindowTitle(_translate("AdjustmentDialogUI", "Manuelle Anpassung"))
        self.recalcStatus_txt.setText(_translate("AdjustmentDialogUI", "Neuberechnung..."))
        self.label_18.setText(_translate("AdjustmentDialogUI", "Manuelle Anpassung der Seillinie"))
        self.btnBackToStart.setToolTip(_translate("AdjustmentDialogUI", "Manuelle Anpassungen verwerfen und zurueck zum Startfenster wechseln"))
        self.btnBackToStart.setText(_translate("AdjustmentDialogUI", "zurueck zum Startfenster"))
        self.btnClose.setToolTip(_translate("AdjustmentDialogUI", "Plugin beenden"))
        self.btnClose.setText(_translate("AdjustmentDialogUI", "Schliessen"))
        self.btnSave.setToolTip(_translate("AdjustmentDialogUI", "Ergebnisse speichern"))
        self.btnSave.setText(_translate("AdjustmentDialogUI", "Speichern"))
        self.label_17.setText(_translate("AdjustmentDialogUI", "Feinjustierung der Stuetzen"))
        self.label_19.setText(_translate("AdjustmentDialogUI", "Nr."))
        self.label_31.setText(_translate("AdjustmentDialogUI", "Stuetzenbezeichnung"))
        self.label_35.setText(_translate("AdjustmentDialogUI", "Horiz.distanz"))
        self.label_30.setText(_translate("AdjustmentDialogUI", "Stuetzenhoehe"))
        self.label_36.setText(_translate("AdjustmentDialogUI", "Neigung"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPoles), _translate("AdjustmentDialogUI", "Stuetzen"))
        self.label_14.setText(_translate("AdjustmentDialogUI", "kN/m"))
        self.label_2.setText(_translate("AdjustmentDialogUI", "Gewicht der Last inkl. Laufwagen"))
        self.label_3.setText(_translate("AdjustmentDialogUI", "kN"))
        self.label_9.setText(_translate("AdjustmentDialogUI", "Gewicht Rueckholseil"))
        self.label_11.setText(_translate("AdjustmentDialogUI", "mm2"))
        self.label_10.setText(_translate("AdjustmentDialogUI", "Vorspannung Tragseil"))
        self.label_4.setText(_translate("AdjustmentDialogUI", "Gewicht Tragseil"))
        self.label_6.setText(_translate("AdjustmentDialogUI", "Querschnittsflaeche Tragseil"))
        self.label_5.setText(_translate("AdjustmentDialogUI", "kN/m"))
        self.label_13.setText(_translate("AdjustmentDialogUI", "kN/m"))
        self.label.setText(_translate("AdjustmentDialogUI", "Minimaler Abstand Tragseil - Boden"))
        self.label_15.setText(_translate("AdjustmentDialogUI", "kN"))
        self.label_22.setText(_translate("AdjustmentDialogUI", "m"))
        self.label_8.setText(_translate("AdjustmentDialogUI", "Gewicht Zugseil"))
        self.label_12.setText(_translate("AdjustmentDialogUI", "Mindestbruchkraft Tragseil"))
        self.label_23.setText(_translate("AdjustmentDialogUI", "kN"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCableline), _translate("AdjustmentDialogUI", "Tragsystem"))
        self.label_21.setText(_translate("AdjustmentDialogUI", "Kennwerte und Maximalwerte"))
        self.label_20.setText(_translate("AdjustmentDialogUI", "Klick auf Zeile markiert Position der Grenzwert-Ueberschreitung im Diagramm."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabThreshold), _translate("AdjustmentDialogUI", "Kennwerte"))
        self.label_16.setText(_translate("AdjustmentDialogUI", "Bemerkungstext, welcher im technischen Bericht ergaenzt wird"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabComment), _translate("AdjustmentDialogUI", "Bemerkungen"))


from . import resources_rc
