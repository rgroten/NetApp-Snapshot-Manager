'''
Created on Jul 9, 2015

@author: rgroten
'''

import pyodbc
import NaFunctions


class RFCChecker:
    connection = None
    cursor = None
    rfcResource = None


    def __init__(self, rfcNumber):
        self.openDbConn()
        self.__queryRFCResource(rfcNumber)
        self.closeDbConn()


    def __queryRFCResource(self, rfcNumber):
        try:
            self.cursor.execute(
            """
            select r.RFCID, r.Title, s.Name 
                from tblRFC r, tblStatus s
            where r.StatusID = s.StatusID
                and r.RFCID = ?  
            """, rfcNumber)
            self.rfcResource = self.cursor.fetchone()

            if not self.rfcResource:
                raise Exception("Invalid RFC Number")

        except Exception as e:
            print str(e)
            raise 
        return self.rfcResource


    def isRFCScheduled(self):
        if (self.rfcResource[2] == "Scheduled"):
            return True
        else:
            return False


    def openDbConn(self):
        server=NaFunctions.getConfigOption("Server", "RFCDBCONN")
        db=NaFunctions.getConfigOption("DB", "RFCDBCONN")
        uid=NaFunctions.getConfigOption("User", "RFCDBCONN")
        password=NaFunctions.getConfigOption("Password", "RFCDBCONN")
        driver=NaFunctions.getConfigOption("Driver", "RFCDBCONN")

        self.connection = pyodbc.connect(driver=driver, server=server, database=db, uid=uid, password=password)
        self.cursor = self.connection.cursor()


    def closeDbConn(self):
        try:
            self.cursor.close()
            self.connection.close()
        except:
            return