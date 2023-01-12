import sqlite3

'''
Klasa obsługująca funkcjonalnośĆ połączenia 
oraz obłsugi bazy danych na podstawie biblioteki 
sqlite3
'''
class DatabaseReader:

    '''
    Konstruktor klasy przyjmujący ID 
    konkretngo filtra
    Zdefiniowane są także kontenery pamięci 
    do obsługi danych z bazy 
    '''
    def __init__(self, filterID):

        self.filterID = filterID
        self._conn = None

        self._items = tuple()
        self._column = list()

        self.dataDic = None


    '''
    metoda obsługująca połączenie z utowrzoną bazą 
    '''
    def exeFun(self):

        self._conn = sqlite3.connect("Filters.db")

        '''
        otwarcie głownego połączenia oraz 
        odczyt danych z bazy
        '''
        self._c = self._conn.cursor()

        '''
        zdefiniowane zapytanie SQL wyszukujące fitra (rekordu) w bazie 
        na podstawie jego ID 
        '''
        self._c.execute("SELECT * FROM FiltersInfo WHERE FilterID = (:fID)", {'fID': self.filterID})
        self._items = self._c.fetchone()
        
        '''
        Kolejne zapytanie SQL wydobywające nazwy kolumn tabeli w bazie 

        '''
        self._cc = self._conn.cursor()
        cols = self._cc.execute("SELECT * FROM FiltersInfo")

        for columns in cols.description:

            self._column.append(columns[0])

        tuple(self._column)

        '''
        Metody wykonujące powyższe zapytania do bazy 
        oraz zamykające połączneie 
        '''
        self._conn.commit()
        self._conn.close()

        '''
        Organizacja odczytanych danych z bazy dotyczące
        filtra w typ danych dict tworzący pary 
        key:value
        '''
        if self._column and self._items is None: 
            
            return 0 

        else: 

            self.dataDic = dict(zip(self._column, self._items))

        




