# Projekt-dyplomowy  
Aplikacja do testowania filtrów analogowych napisana w oparciu o Pythona oraz bibliotekę firmy NI, za pomocą fizycznej karty DAQ. 
Wykorzystane moduły:  
nidaqmx  
PyQt5  
numpy  
matplotlib  
queue  
math  
scipy  
datetime  
csv  
xlsxwriter  
nptdms  
sqlite3  
openCV  
pyzbar  
json  
  

Instrukcja obsługi aplikacji: wybór fizycznej karty (na podstawie nazwy z NI MAX), wybór fizycznych kanałów, wybór filtra, start testu, po otrzymaniu wyników - 
zapis do plików, reset. Po zresetowaniu aplikacji nalezy ponownie zatwierdzić DAQ klikając "Set Values". Inaczej wszystkie inne przyciski pozostaną wyszarzone.  
Aplikację uruchamia się poprzez wywołanie pliku MainWindow.py. 
