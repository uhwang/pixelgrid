'''
pxlgridgui.py

grapher paper generator

8/13/23
'''
import sys
import os
from collections import OrderedDict
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QProcess, QSize, QBasicTimer
from PyQt5.QtGui import QColor, QIcon, QPixmap, QIntValidator, QFont, QFontMetrics
from PyQt5.QtWidgets import ( QApplication, 
                              QWidget,
                              QStyleFactory, 
                              QDialog,
                              QLabel, 
                              QPushButton, 
                              QLineEdit,
                              QComboBox, 
                              QCheckBox, 
                              QRadioButton, 
                              QTableWidget, 
                              QTableWidgetItem, 
                              QTabWidget,
                              QProgressBar, 
                              QPlainTextEdit, 
                              QGridLayout, 
                              QVBoxLayout, 
                              QHBoxLayout, 
                              QFormLayout, 
                              QButtonGroup,
                              QFileDialog, 
                              QScrollArea,
                              QMessageBox,
                              QHeaderView,
                              QButtonGroup,
                              QGroupBox,
                              QTreeWidget,
                              QTreeWidgetItem,
                              QColorDialog,
                              QDoubleSpinBox)


import vgl
from math import fabs
from icons import icon_folder_open, icon_pxlgrid, icon_color_picker

def print_pixelgrid(dev, m_left, m_top, f_wid, f_hgt, lcol, lthk, lpat, pxl_size):
 
    limit = 10e-5
    unit_pixel = pxl_size * dev.frm.hgt()
    ex = m_left + int(f_wid/unit_pixel)*unit_pixel
    ey = m_top  + int(f_hgt/unit_pixel)*unit_pixel
    
    sy = m_top
    while sy <= ey:
        dev.lline(m_left, sy, ex, sy, lcol, lthk, lpat)
        sy += unit_pixel

    if sy != ey and fabs(sy-ey) < limit:
        dev.lline(m_left, ey, ex, ey, lcol, lthk, lpat)
        
    sx = m_left
    while sx <= ex:
        dev.lline(sx, m_top, sx, ey, lcol, lthk, lpat)
        sx += unit_pixel

    if sx != ex and fabs(sx-ex) < limit:
        dev.lline(ex, m_top, ex, ey, lcol, lthk, lpat)
        
    dev.close()

class QPixelGrid(QWidget):
    def __init__(self):
        super(QPixelGrid, self).__init__()
        self.initUI()

    def initUI(self):
        self.form_layout = QFormLayout()
        #grid_save = QGridLayout()
        paper = QGridLayout()
        
        paper.addWidget(QLabel("Save"), 0,0)
        self.save_folder = QLineEdit(os.getcwd())
        paper.addWidget(self.save_folder, 0,1)
        self.save_folder_btn = QPushButton()
        self.save_folder_btn.setIcon(QIcon(QPixmap(icon_folder_open.table)))
        self.save_folder_btn.setIconSize(QSize(16,16))
        self.save_folder_btn.setToolTip("Change download folder")
        self.save_folder_btn.clicked.connect(self.get_new_save_folder)
        paper.addWidget(self.save_folder_btn, 0,2)

        self.save_file = QLineEdit("pixelgrid")
        paper.addWidget(QLabel("File"), 1,0)
        paper.addWidget(self.save_file, 1,1)

        paper.addWidget(QLabel("Paper"), 2, 0)
        self.paper_type = QComboBox()
        self.paper_type.addItems(["LETTER", "A4"])
        paper.addWidget(self.paper_type, 2, 1)
        
        paper.addWidget(QLabel("Left")  , 3, 0)
        paper.addWidget(QLabel("Top")   , 4, 0)
        paper.addWidget(QLabel("Right") , 5, 0)
        paper.addWidget(QLabel("Bottom"), 6, 0)
        
        self.paper_margin_left   = QDoubleSpinBox(minimum=0.0, value=0.5, suffix=' inch')
        self.paper_margin_top    = QDoubleSpinBox(minimum=0.0, value=0.5, suffix=' inch')
        self.paper_margin_right  = QDoubleSpinBox(minimum=0.0, value=0.5, suffix=' inch')
        self.paper_margin_bottom = QDoubleSpinBox(minimum=0.0, value=0.5, suffix=' inch')

        self.paper_margin_left  .setSingleStep(0.1)
        self.paper_margin_top   .setSingleStep(0.1)
        self.paper_margin_right .setSingleStep(0.1)
        self.paper_margin_bottom.setSingleStep(0.1)

        paper.addWidget(self.paper_margin_left  , 3, 1)
        paper.addWidget(self.paper_margin_top   , 4, 1)
        paper.addWidget(self.paper_margin_right , 5, 1)
        paper.addWidget(self.paper_margin_bottom, 6, 1)
        
        paper.addWidget(QLabel("Pxl size"), 7,0)
        self.pixel_size = QDoubleSpinBox(minimum=0.001, value=0.012, suffix=' %')
        self.pixel_size.setDecimals(3)
        self.pixel_size.setSingleStep(0.001)
        self.pixel_size.setValue(0.012)
        paper.addWidget(self.pixel_size, 7,1)
        
        paper.addWidget(QLabel("LThk"), 8,0)
        self.line_thickness = QDoubleSpinBox(minimum=0.001, value=0.003, suffix=' %')
        self.line_thickness.setSingleStep(0.001)
        self.line_thickness.setDecimals(3)
        paper.addWidget(self.line_thickness, 8,1)
        
        paper.addWidget(QLabel("LCol"), 9,0)
        self.line_color = QLineEdit("0,0,0")
        paper.addWidget(self.line_color, 9,1)
        
        self.line_color_picker = QPushButton('', self)
        self.line_color_picker.setIcon(QIcon(QPixmap(icon_color_picker.table)))
        self.line_color_picker.setIconSize(QSize(16,16))
        self.line_color_picker.clicked.connect(self.pick_line_color)
        paper.addWidget(self.line_color_picker, 9,2)
        
        line_type = QGridLayout()
        line_type.addWidget(QLabel("Pattern"), 0,0)
        line_type.addWidget(QLabel("Length"), 0,1)
        
        self.line_pattern = QComboBox()
        self.line_pattern.addItems(vgl.get_pattern_names())
        line_type.addWidget(self.line_pattern, 1,0)
        
        self.pattern_length = QDoubleSpinBox(minimum=0.01, value=0.04, suffix=' %')
        self.pattern_length.setSingleStep(0.01)
        self.save_folder_btn.setToolTip("Percentage of a frame height")
        line_type.addWidget(self.pattern_length, 1,1)
        
        self.dev_checker = OrderedDict()
        self.dev_check_list = OrderedDict(zip(vgl.devutil._dev_list,
                              [True for _ in vgl.devutil._dev_list]))
                              
        dev_layout = QGridLayout()
        ncol = 3
        row = 0
        for i, dev_name in enumerate(vgl.devutil._dev_list):
            checker = QCheckBox(dev_name, self)
            checker.setChecked(self.dev_check_list[dev_name])
            self.dev_checker[dev_name] = checker
            col = i % ncol
            row = row+1 if i != 0 and i%ncol == 0 else row
            dev_layout.addWidget(checker, row, col)
        
        self.select_vector_dev_btn = QPushButton("Vect")
        self.select_vector_dev_btn.clicked.connect(self.select_vector_dev)
        
        self.select_image_dev_btn  = QPushButton("Img")
        self.select_image_dev_btn.clicked.connect(self.select_image_dev)
        
        self.select_all_dev_btn    = QPushButton("All")
        self.select_all_dev_btn.clicked.connect(self.select_all_dev)
        
        dev_btn = QHBoxLayout()
        dev_btn.addWidget(self.select_vector_dev_btn)
        dev_btn.addWidget(self.select_image_dev_btn)
        dev_btn.addWidget(self.select_all_dev_btn)
        t_widget = QWidget()
        t_widget.setLayout(dev_btn)
        t_widget.setFixedWidth(200)
        
        self.create_btn = QPushButton("Create")
        self.create_btn.clicked.connect(self.create_pixelgrid)
        option = QHBoxLayout()
        option.addWidget(self.create_btn)
        
        self.form_layout.addRow(paper)
        self.form_layout.addRow(line_type)
        self.form_layout.addRow(dev_layout)
        self.form_layout.addRow(t_widget)
        self.form_layout.addRow(option)
        
        self.setLayout(self.form_layout)
        self.setWindowTitle("Pixel grid_save")
        self.setWindowIcon(QIcon(QPixmap(icon_pxlgrid.table)))
        self.show()

    def select_all_dev(self):
        for i, dev_name in enumerate(vgl.devutil._dev_list):
            self.dev_checker[dev_name].setChecked(True)
            self.dev_check_list[dev_name] = True
    
    def select_vector_dev(self):
        for i, dev_name in enumerate(vgl.devutil._dev_list):
            if dev_name == vgl.devutil._dev_emf or\
               dev_name == vgl.devutil._dev_wmf or\
               dev_name == vgl.devutil._dev_pdf or\
               dev_name == vgl.devutil._dev_svg or\
               dev_name == vgl.devutil._dev_ppt:
                self.dev_checker[dev_name].setChecked(True)
                self.dev_check_list[dev_name] = True
            else:
                self.dev_checker[dev_name].setChecked(False)
                self.dev_check_list[dev_name] = False
    
    def select_image_dev(self):
         for i, dev_name in enumerate(vgl.devutil._dev_list):
            if dev_name == vgl.devutil._dev_img:
                self.dev_checker[dev_name].setChecked(True)
                self.dev_check_list[dev_name] = True
            else:
                self.dev_checker[dev_name].setChecked(False)
                self.dev_check_list[dev_name] = False
                
    def get_new_save_folder(self):
        startingDir = os.getcwd() 
        path = QFileDialog.getExistingDirectory(None, 'Save folder', startingDir, 
        QFileDialog.ShowDirsOnly)
        if not path: return
        self.save_folder.setText(path)
        os.chdir(path)
    
    def exit_pixelgrid(self):
        pass
        
    def pick_line_color(self):
        lc = self.line_color.text().split(',')
        col = QColorDialog.getColor(QColor(int(lc[0]), int(lc[1]), int(lc[2])))
        
        if col.isValid():
            r,g,b,a = col.getRgb()
            self.line_color.setText("%d,%d,%d"%(r,g,b))
            
    def create_pixelgrid(self):
    
        fn = self.save_file.text()
        m_left   = self.paper_margin_left.value()
        m_top    = self.paper_margin_top.value()
        m_right  = self.paper_margin_right.value()
        m_bottom = self.paper_margin_bottom.value()
        
        # w(in)   h(in)     w(mm)       h(mm)        
        p_size = vgl.get_paper_size(self.paper_type.currentText())
        p_wid, p_hgt = p_size[0], p_size[1]
        f_wid = p_wid-m_left-m_right
        f_hgt = p_hgt-m_top-m_bottom
       
        fmm = vgl.FrameManager()
        frm = fmm.create(m_left,m_top,f_wid,f_hgt, vgl.Data(-1,1,-1,1))
        gbbox= fmm.get_gbbox()
        pxl_size = self.pixel_size.value()
        
        lc = self.line_color.text().split(',')
        lcol = vgl.color.Color(int(lc[0]), int(lc[1]), int(lc[2]))
        lthk = self.line_thickness.value()
        lpat_= self.line_pattern.currentText()
        lpat = vgl.linepat._PAT_SOLID\
               if lpat_ == vgl.linepat._PAT_SOLID\
               else vgl.linepat.LinePattern(self.pattern_length.value(), lpat_)
        
        for key, value in self.dev_checker.items():
            self.dev_check_list[key] = value.isChecked()
        
        for key, value in self.dev_check_list.items():
            #print(key, value)
            if key == vgl.devutil._dev_img and value:
                dev = vgl.DeviceIMG("%s.png"%fn, gbbox, 300)
                dev.set_device(frm)
                print_pixelgrid(dev, m_left, m_top, f_wid, f_hgt, lcol, lthk, lpat, pxl_size)
            if key == vgl.devutil._dev_wmf and value:
                dev = vgl.DeviceWMF("%s.wmf"%fn, gbbox)  
                dev.set_device(frm)
                print_pixelgrid(dev, m_left, m_top, f_wid, f_hgt, lcol, lthk, lpat, pxl_size)
            if key == vgl.devutil._dev_emf and value:
                dev = vgl.DeviceEMF("%s.emf"%fn, gbbox) 
                dev.set_device(frm)
                print_pixelgrid(dev, m_left, m_top, f_wid, f_hgt, lcol, lthk, lpat, pxl_size)
            if key == vgl.devutil._dev_pdf and value:
                dev = vgl.DevicePDF("%s.pdf"%fn, gbbox)  
                dev.set_device(frm)
                print_pixelgrid(dev, m_left, m_top, f_wid, f_hgt, lcol, lthk, lpat, pxl_size)
            if key == vgl.devutil._dev_svg and value:
                dev = vgl.DeviceSVG("%s.svg"%fn, gbbox, 300)    
                dev.set_device(frm)
                print_pixelgrid(dev, m_left, m_top, f_wid, f_hgt, lcol, lthk, lpat, pxl_size)
            if key == vgl.devutil._dev_ppt and value:
                dev = vgl.DevicePPT("%s.ppt"%fn, gbbox)  
                dev.set_device(frm)
                print_pixelgrid(dev, m_left, m_top, f_wid, f_hgt, lcol, lthk, lpat, pxl_size)
  
def main():
    
    app = QApplication(sys.argv)

    # --- PyQt4 Only
    #app.setStyle(QStyleFactory.create(u'Motif'))
    #app.setStyle(QStyleFactory.create(u'CDE'))
    #app.setStyle(QStyleFactory.create(u'Plastique'))
    #app.setStyle(QStyleFactory.create(u'Cleanlooks'))
    # --- PyQt4 Only
    
    app.setStyle(QStyleFactory.create("Fusion"))
    ydl= QPixelGrid()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()    

    

