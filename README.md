# NI9239_DAQ
Software per acquisizione, visualizzazione in tempo reale, ed elaborazione di segnali di tensione tramite moduli National Instruments NI9239.


Documentazione relativa al software di acquisizione dati in Python per un campionatore di segnali di tensione, il modulo NI9239, installato sul chassis compatibile (es.cDAQ9172), prodotti dalla National Instruments.
Il software è sviluppato in  Python.
L’interfaccia grafica (GUI) del software è stata sviluppata tramite PyQt5, un modulo di Python che permette di usare le librerie grafiche di Qt. Una delle caratteristiche principali di Qt è l’uso del meccanismo di Signal and Slot: un widget, che è un componente grafico dell’interfaccia utente di un programma, può emettere un segnale in seguito a un’azione eseguita dall’utente, per esempio un pulsante che viene cliccato; questo segnale viene poi connesso al rispettivo slot, cioè un metodo, che verrà eseguito.
Python supporta il multithreading, ovvero l’esecuzione in parallelo di più processi. Questa funzionalità è stata sfruttata per separare l’acquisizione dei dati dall’interazione dell’utente con l’interfaccia. E’ stato quindi creato un sotto-processo (thread) che viene eseguito indipendentemente dal resto del codice e che sfrutta il meccanismo di Signal and Slot per comunicare con il processo principale.
A queste librerie è stato affiancato l’uso di Qtdesigner, un tool di Qt che permette di creare rapidamente interfacce desktop tramite strumenti Drag and Drop, che possono poi essere convertite in codice Python attraverso un semplice comando eseguito da terminale.
Infine è stato usato il pacchetto nidaqmx, sviluppato dalla National Instruments (NI), una API (Application Programming Interface), implementata in Python, per l’interfacciamento con i dispositivi prodotti dall’azienda stessa e quindi permettere l’acquisizione o la generazione di segnali, in dipendenza dal dispositivo utilizzato.


Strumentazione

Il NI9239 è un modulo di input tensione Serie C a 4 canali, prodotto dalla National Instruments (NI), che permette di misurare segnali di tensione in ingresso per sistemi CompactDAQ o CompactRIO.
Il CompactDAQ è una piattaforma di acquisizione dati che include un set di hardware e software compatibili. Esso integra l’hardware per l’I/O dei dati con il software per consentire di raccogliere, elaborare e analizzare i dati delle misurazioni.
L’hardware è composto da due parti:
	Uno chassis, che controlla il trasferimento dei dati tra i moduli di I/O e il computer. Fornisce inoltre un clock per il timing e la sincronizzazione tra tutti i moduli nel sistema. Sono disponibili diverse tipologie di chassis: USB, Ethernet, Wireless.
I moduli Serie C, con input e output analogici, responsabili del condizionamento (come per esempio amplificazione, filtraggio) dei segnali.
Inoltre è stato implementato il controllo remoto congiunto di un generatore di funzioni (modello Agilent 33250A), in modo da generare forme d'onda note e verificare il corretto funzionamento dell'applicazione.


Software

Il software genera una finestra grafica con cui l’utente può interagire per svolgere diverse azioni:
	- Scegliere i canali da cui acquisire un segnale	
	- Definire un numero di valori di input da acquisire	
	- Indicare la frequenza di campionamento	
	- Selezionare la modalità di acquisizione dati (finita o continua)	
	- Avviare e terminare l’acquisizione	
	- Visualizzare i segnali acquisiti nel dominio del tempo e della frequenza in due grafici dedicati	
	- Selezionare la tipologia di FFT Windowing	
	- Aggiungere eventuali note	
	- Salvare i dati in formato immagine e testo	
	- Controllare da remoto il generatore di funzioni Agilent 33250A, necessario per testare il corretto funzionamento del programma di acquisizione.
                                                                                                                                 

![image](https://user-images.githubusercontent.com/35451816/115555223-8e946b00-a2af-11eb-9dbb-994cbd688c7b.png)




![image](https://user-images.githubusercontent.com/35451816/115566558-a0c7d680-a2ba-11eb-83d8-a9c759dee8d2.png)


![image](https://user-images.githubusercontent.com/35451816/115566146-49296b00-a2ba-11eb-8b38-eb6d786a9df5.png)



Riferimenti

https://nidaqmx-python.readthedocs.io/en/latest/#

https://github.com/ni/nidaqmx-python

https://www.ni.com/pdf/manuals/371747f.pdf

https://www.ni.com/pdf/manuals/375939a.pdf

https://www.ni.com/pdf/manuals/375939b_02.pdf

https://doc.qt.io/qtforpython/

https://github.com/PyQt5

https://zone.ni.com/reference/en-XX/help/370689M-01/daqmxtutorial/newconceptsinnidaqmx/






