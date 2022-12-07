import sqlite3
'''
Function has to get a id, by that id open database, read proper record, 
extract significant data from colums, asign them to variables
'''


class DatabaseReader:

    def __init__(self, filterID):

        self.filterID = filterID
        self._conn = None

        self._items = tuple()
        self._column = list()

        self.dataDic = None


    def exeFun(self):

        self._conn = sqlite3.connect("Filters.db")

        '''
        main connection and fetching data from table
        '''
        self._c = self._conn.cursor()

        self._c.execute("SELECT * FROM FiltersInfo WHERE FilterID = (:fID)", {'fID': self.filterID})
        self._items = self._c.fetchone()
        '''
        Getting names of columns from table
        '''
        self._cc = self._conn.cursor()
        cols = self._cc.execute("SELECT * FROM FiltersInfo")


        for columns in cols.description:

            self._column.append(columns[0])

        tuple(self._column)

        '''
        Comminitg actions and Closing database 
        '''
        self._conn.commit()
        self._conn.close()

        self.dataDic = dict(zip(self._column, self._items))

        #return  self.dataDic


'''
Only fopr testtig purposes
'''


# if __name__ == "__main__":

#     db = DatabaseReader('000004')
#     db.exeFun()

#     print(db.dataDic['Id'])




