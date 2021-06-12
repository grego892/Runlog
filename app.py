from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt5 import uic, QtCore
import sys, csv
from ftplib import FTP
import xml.etree.ElementTree as ET



class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("main.ui", self)
        global date
        self.setWindowTitle('OpX Connect')
        self.pushButton.clicked.connect(self.chgStn)
        self.comboBox.clear()
        self.comboBox.addItems(sta_list)      
        self.dateEdit.setDate(QtCore.QDate.currentDate())
        self.show()
        
    def chgStn(self):
        global date
        date = self.dateEdit.date()
        chgStn2(self.comboBox.currentText())    
        
    def populateTable(self, data):
        numrows = len(data)  # 6 rows in your example
        numcols = len(data[0])  # 3 columns in your example
        
    
        # Set colums and rows in QTableWidget
        self.tableWidget.setColumnCount(numcols)
        self.tableWidget.setRowCount(numrows)
    
        # Loops to add values into QTableWidget
        for row in range(numrows):
            for column in range(numcols):
                self.tableWidget.setItem(row, column, QTableWidgetItem(data[row][column]))
        self.tableWidget.resizeColumnsToContents()

def getSta():
        ftp = FTP()
        ftp.connect('10.68.10.50', 2121)
        ftp.login('BSIClient', 'StudioX')   
        with FTP('10.68.10.50', user='******', passwd='******') as ftp:
            with open(r'.\data\FileServer Settings.xml', 'wb') as local_file:  # Open local file for writing
                response = ftp.retrbinary('RETR FileServer Settings.xml', local_file.write)
                print (response)
                response = ftp.sendcmd("QUIT");
                print (response);
        global sta_list
        tree = ET.parse('.\data\FileServer Settings.xml')
        root = tree.getroot()
        
        sta_list = []
        for each in root.findall('.//TStationsItem'):
            station = each.find('.//Station')
            sta_list.append(station.text)
        return sta_list

def chgStn2(chosenText):
    print ('Chosen text is: ' + chosenText)
    ftp = FTP()
    ftp.connect('10.68.10.50', 2121)
    ftp.login('BSIClient', 'StudioX')  
    response = ftp.sendcmd('FEAT');
    print(response);        
    response = ftp.sendcmd('TYPE I');
    print(response);         
    response = ftp.sendcmd('SYST');
    print(response);         
    response = ftp.sendcmd('TYPE I');
    print(response);       
    response = ftp.sendcmd('ALLFILES ' + chosenText);
    print(response);        
    response = ftp.sendcmd('INCLUDELOGS ' + chosenText);
    print(response);        
    with open(r'.\data\AllFiles.txt', 'wb') as fp:
        response = ftp.retrbinary('RETR AllFiles.txt', fp.write)       
    
    # Parse the AllFiles.txt
    searchfile = open(r'.\data\AllFiles.txt', "r")
    for line in searchfile:
        if "RUNLOGS" in line: runLogPath = line.split(',')[1].lstrip()
    searchfile.close()
    print (runLogPath)
    response = ftp.cwd(runLogPath)
    print (response)
    
    # Get date from calendar
    runlogFilename = (date.toString('yyMMdd') + '.log')
    print (runlogFilename)

    # Get Runlog from server
    with open(r'.\data\%s' % runlogFilename, 'wb') as local_file:  # Open local file for writing
        response = ftp.retrbinary('RETR ' + runlogFilename, local_file.write)
        print (response)
    response = ftp.sendcmd("QUIT");
    print (response);

    # Parse log file into LIST
    with open('.\data\%s' % runlogFilename, "r") as f:
        reader = csv.reader(f)
        data = list(reader)

    # From LIST to TABLE
    window.populateTable(data)

station_list = getSta()


app = QApplication(sys.argv)
window = UI()
app.exec_()




