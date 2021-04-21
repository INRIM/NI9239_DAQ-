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



Classi implementate

Classe Ui_MainWindow()
E’ la classe principale che contiene il codice per la creazione dell’interfaccia grafica, tutte le connessioni tra i widget e le funzioni da eseguire, e i metodi principali che permettono l’acquisizione e l’elaborazione dei dati.

Classe WindowChannel(QWidget)
E’ la classe usata per creare e personalizzare la finestra grafica per i canali di acquisizione. Nel layout di questa interfaccia vengono aggiunte tante checkBox quanti sono i canali disponibili e un pushButton “Enter” che permette di memorizzare in una lista (impostata come variabile globale) le caselle selezionate dall’utente e rendere l’informazione visibile alla classe della GUI principale.

Classe WorkerThread(QThread)
Questa classe contiene il codice che si vuole eseguire in modo indipendente dal resto del programma, realizza quindi l’acquisizione dei dati in modalità continua. 
Si crea il segnale che il thread invia alla GUI ogni volta che viene eseguita una lettura:
update_acquisition = pyqtSignal(list);
La funzione pyqtSignal(), che fa parte della documentazione di PyQt5, permette di creare un segnale e di settare il valore che viene emesso, in questo caso una lista.
Si procede poi allo sviluppo del codice per l’acquisizione dei dati, definendolo all’interno del metodo run(). 

Classe AgilentAWG()
Questa classe definisce tutti i metodi per poter comunicare da remoto con il generatore di funzioni Agilent 33250A. 

Metodi implementati

Metodo pressedAddChannel()
Questo metodo viene eseguito quando l’utente preme il pulsante Add Channels.
Viene generata una nuova finestra (Available Channels), chiamando la classe WindowChannel(), contenente tutti i canali disponibili nel sistema per permettere all’utente di selezionare quelli da cui vuole acquisire dati. 

Metodo pressedStart()
E’ lo slot che viene chiamato ogni volta che l’utente preme il pulsante START.
Viene creata una variabile globale di tipo lista contenente i canali che sono stati selezionati dall’utente, in modo da essere visibile a tutto il programma e permettere l’acquisizione ed elaborazione dei dati. 
Successivamente vengono eseguiti dei controlli su ciò che l’utente inserisce.
Il primo è un controllo sulla frequenza di campionamento inserita. Il range di valori che sono ammessi dal NI 9239 va da un minimo di 1.613 kS/s a un massimo di 50 kS/s, e le frequenze di campionamento accettate dallo strumento vengono calcolate attraverso la formula:

                                                                    f_s = (f_M  ÷ 256)/n

dove:	f_s rappresenta la frequenza di campionamento, f_M la frequenza del clock interno, che nel NI9239 ha il valore di 12.8 MHz, n è un numero intero che varia tra 1 e 31.
Si accede al valore inserito dall’utente attraverso il comando spinBox.value() e si controlla che questo sia valido, altrimenti viene automaticamente corretto con quello accettabile più vicino e l’utente viene avvisato dell’errore tramite il popup show_popupSampleRate().
Viene anche controllato il numero di campioni inserito dall’utente, se è inferiore a 1000 viene corretto di default.
Successivamente si controlla che l’utente abbia selezionato almeno un canale di acquisizione. In caso contrario viene generato un altro popup, con il metodo show_popupNoChannel(), per chiedere all’utente di selezionare un canale.
Dopo questi controlli si procede all’acquisizione di dati, che può avvenire in modalità finita o continua. Si controlla il valore nella comboBox con comboBox.currentText(), se il testo corrisponde a “Finite” viene chiamato il metodo finiteAcquisition(), altrimenti quello continuousAcquisition().

Metodo finiteAcquisition()
In questa modalità si richiede che l’utente inserisca il numero N di campioni che desidera acquisire.
Successivamente si procede con l’acquisizione dei dati, che può avvenire attraverso uno o più canali contemporaneamente. 
Si crea quindi un Task, usando le funzioni appropriate del pacchetto nidaqmx.
Un Task è una collezione di uno o più canali virtuali per cui vengono definiti timing, triggering ed altre proprietà; rappresenta l’acquisizione o la generazione di un segnale. 
Un canale virtuale è una serie di impostazioni di proprietà come nome, canale fisico, connessioni input terminale, tipologia di misurazione o generazione.
Dopo aver creato un task bisogna procedere con la configurazione del canale e del timing.
Si configura il canale con la funzione task.ai_channels.add_ai_voltage_chan(), che definisce un canale di input analogico per misure di tensione, e alla quale bisogna passare il nome del canale virtuale e i valori di massimo e minimo misurabili.
Viene poi configurato il timing del task con task.timing.cfg_samp_clk_timing(), che richiede come parametri la frequenza di campionamento, il source terminal del Sample Clock (questo parametro se non specificato viene settato di default con il clock interno), il fronte di acquisizione (di default acquisisce sul fronte di salita del clock), la modalità di acquisizione (continuous o finite) e il numero di campioni per canale.
Successivamente vengono acquisiti i dati attraverso la funzione task.read(), che ha come parametri il numero di campioni per canale e il timeout (cioè la quantità di tempo, in secondi, da aspettare affinchè i samples siano disponibili, di default viene settato a 10 s), e ritorna i valori acquisiti sotto forma di lista.
Poiché è possibile acquisire simultaneamente dati da più canali, al task saranno aggiunti tutti quelli che sono stati selezionati dall’utente.
Per rendere l’acquisizione visibile all’utente nel grafico del dominio del tempo, questa viene mostrata su schermo con il comando graphWidget.plot(lista).
Essendo richiesta anche la visualizzazione nel dominio della frequenza, bisogna determinare la trasformata di Fourier discreta dei valori acquisiti nel dominio del tempo. Questo viene effettuato tramite una chiamata al metodo fourierTransform().
Esempio di acquisizione dati in modalità finita in figura, da un solo canale di input analogico.

![image](https://user-images.githubusercontent.com/35451816/115566558-a0c7d680-a2ba-11eb-83d8-a9c759dee8d2.png)


Metodo continuousAcquisition()
In questa modalità è l’utente a scegliere quando terminare l’acquisizione dei dati, per questo motivo lo stesso pulsante ha una duplice funzione: avviamento e terminazione.
Poiché l’acquisizione in continua richiede che l’interfaccia sia utilizzabile dall’utente mentre i dati vengono letti dallo strumento, è necessaria la creazione di un Thread, che consiste in un flusso separato di esecuzione. 
In PyQt5 si possono realizzare i thread con la classe QThread, che fornisce delle funzioni per gestire il meccanismo di Signal and Slot, in modo che l’oggetto possa comunicare con la classe principale attraverso dei segnali. 
Come prima operazione viene quindi effettuato un controllo sul testo che presenta il pulsante:
	Scritta “START”: inizialmente si setta una nuova grafica per cui il pulsante appare rosso e mostra la scritta “STOP”. Poi si crea l’oggetto Thread con l’istruzione worker=WorkerThread(), che chiama la classe che si occupa di gestire il codice indipendente dal resto del programma. Poi si avvia l’esecuzione del thread con worker.start(), e si connette il segnale di aggiornamento del thread con il rispettivo slot attraverso il comando worker.update_acquisition.connect(evt_update).
	Scritta “STOP”: si vuole terminare l’acquisizione dei dati quindi si effettua una richiesta di interruzione del thread con la funzione definita dalla classe QThread requestInterruption(). Quando il thread finisce l’esecuzione invia un segnale (finished) alla GUI che lo connette al relativo slot con l’istruzione worker.finished.connect(evt_finished).

Metodo evt_update()
Questo metodo viene chiamato ogni volta che il thread emette il segnale di aggiornamento.
Elabora i dati acquisiti durante un’iterazione e si occupa di stamparli a video, nel grafico che li rappresenta nel dominio del tempo. Successivamente chiama il metodo fourierTranform() che si occupa di mostrare a video, in modo continuo, la trasformata di Fourier dei valori letti dallo strumento.

Metodo evt_finished()
E’ lo slot collegato al segnale che emette il thread quando l’acquisizione dei dati viene terminata dall’utente. Viene modificata la grafica del pulsante, che torna alle impostazioni di default, quindi sfondo verde e scritta “START”, per permettere all’utente di eseguire una nuova acquisizione.

Metodo run()
E’ definito all’interno della classe WorkerThread(QThread) e contiene il codice per realizzare l’acquisizione in modalità continua dei dati.
Viene chiamato in seguito all’istruzione, dalla classe della finestra principale, worker.start().
Come per la modalità finita anche in questo caso si crea un Task usando il pacchetto nidaqmx. Eseguendo un controllo sui canali selezionati dall’utente, si procede alla loro configurazione e ad aggiungerli al task; poi viene configurato il clock con l’istruzione:
task.timing.cfg_sam_clk_timing(sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan = n_input).
In questo caso, avendo impostato sample_mode in modalità continua, il parametro samps_per_chan viene usato per determinare la dimensione del buffer.
La lettura dei canali avviene all’interno di un ciclo che viene interrotto quando l’utente clicca il pulsante STOP, attivando quindi la richiesta di interruzione. 
Il codice è il seguente:
while not isInterruptionRequested():
                data=task.read(number_of_samples_per_channel = n_input)
                update_acquisition.emit(data) 
isInterruptionRequested() è una funzione che ritorna un valore booleano, in questo caso ritorna True quando viene chiamata la funzione requestInterruption().
All’interno del ciclo while avviene la lettura dei canali, e viene emesso il segnale di aggiornamento che ritorna la lista di valori letti al programma principale, il quale lo collega al relativo slot per permettere di gestire i dati appena acquisiti. 

Metodo fourierTransform()
Questo metodo realizza il calcolo della trasformata discreta di Fourier dei dati acquisiti dallo strumento e mostra il relativo grafico sull’interfaccia.
E’ stato realizzato l’algoritmo della FFT (Fast Fourier Transform) che è ottimizzato per calcolare la trasformata discreta di Fourier. Per calcolarla si è fatto uso di SciPy, una libreria di algoritmi e strumenti matematici per Python, che contiene moduli per l’ottimizzazione, per l’algebra lineare, l’integrazione, FFT, elaborazione dei segnali. In particolare per il calcolo della trasformata sono stati importati da scipy.fftpack i moduli fft e fftfreq. 
Alla funzione fft() si passa la sequenza di valori di cui si vuole calcolare la trasformata e si ottiene un array contente la DFT (Discrete Fourier Transform).
Invece fftfreq() ha come parametri il numero di elementi della sequenza (n) e l’inverso della frequenza di acquisizione (ovvero il periodo), e ritorna un array di lunghezza n contenente i campioni di frequenza. 
E’ stato inoltre implementata una window (finestra) per il segnale, ovvero una funzione matematica che vale zero al di fuori di un certo intervallo, e che serve per pesare in modo diverso i dati acquisiti nel dominio del tempo. Applicare una finestra provoca una distorsione sull’ampiezza e sull’energia del segnale, quindi servono dei fattori di correzione, per i due parametri, che variano a seconda della tipologia di window utilizzata. Non è possibile però correggere contemporaneamente questi due valori e in questo caso è stato applicato solo il fattore di correzione per l’ampiezza. L’utente può scegliere dall’interfaccia grafica tra quattro tipologie di window:

	Rectangular: fattore di correzione per l’ampiezza = 1
	
	Hanning: fattore di correzione per l’ampiezza = 2
	
	Hamming: fattore di correzione per l’ampiezza = 1.85
	
	Blackman: fattore di correzione per l’ampiezza = 2.80

Metodo pressedInitializeAWG()
Questo metodo permette la creazione dell’oggetto della classe Agilent rendendo così possibile il controllo del generatore di funzioni.
Quando l’utente clicca il pulsante “Initialize AWG” si crea l’oggetto chiamando la rispettiva classe, viene abilitato il pulsante START GEN e sono attivati in modalità scrittura gli spinBox per ampiezza, frequenza e offset della sinusoide da generare.
Successivamente il pulsante viene disabilitato, in quanto non è necessario generare un altro oggetto della classe.

Metodo pressedStartGen()
Questo metodo permette di avviare e terminare il generatore di funzioni. 
Inizialmente memorizza in opportune variabili i valori inseriti dall’utente per ampiezza, frequenza e offset della sinusoide.
Se il pulsante mostra la scritta “START GEN”, cliccandolo il generatore di funzioni inizia a generare la sinusoide, se invece presenta “STOP GEN” allora la termina.
In figura è mostrato un esempio di acquisizione dati in modalità finita costituita da un solo canale di input analogico, dopo aver impostato una sinusoide di ampiezza 1 V, frequenza 50 Hz e offset 0 V, e successivamente attivato il generatore di funzioni.

![image](https://user-images.githubusercontent.com/35451816/115566146-49296b00-a2ba-11eb-8b38-eb6d786a9df5.png)



Metodo pressedSaveGraph()
E’ lo slot che viene eseguito quando l’utente preme il pulsante SAVE GRAPH.
Permette di salvare i grafici ottenuti in due file formato immagine (.png), il cui nome è chiesto all’utente tramite una finestra di dialogo e a cui sono aggiunti i due suffissi “_time” e “_freq” rispettivamente per il grafico nel dominio del tempo e della frequenza.
Al fine di evitare che venga salvata un’immagine vuota, si effettua un controllo per verificare che l’utente abbia schiacciato START e che quindi si siano acquisiti dei dati. Se ha esito negativo viene mostrato un popup, show_popupNoAcquisition(), così da avvertire che si sta tentando di fare un salvataggio senza avere ancora acquisito nulla.
Se il salvataggio invece è andato a buon fine viene visualizzato un popup, show_popupSaved(), per informare sull’operazione avvenuta con successo.

Metodo pressedSaveFile()
Questo slot viene eseguito in seguito a un click sul pulsante SAVE FILE.
Permette di salvare i dati ottenuti in formato .csv (Comma Separated Values) che permette l’importazione ed esportazione di una tabella di dati.
Si salvano i valori letti dallo strumento, la relativa trasformata di Fourier ed eventuali annotazioni aggiunte dall’utente nell’opportuna casella di testo. 
Viene nuovamente chiesto all’utente il nome del file da salvare, e vengono poi aggiunti due suffissi, in modo da generare due file separati: in uno il suffisso “_time” e vengono salvati i dati letti nel dominio del tempo e nell’altro, con il suffisso “_freq”, quelli ottenuti nel dominio della frequenza. 
Se l’utente ha aggiunto delle note nel rispettivo box, queste vengono salvate, prima della tabella contenente i dati, in entrambi i file.
Anche questo metodo richiama le funzioni show_popupNoAcquisition() e show_popupSaved(), per gli eventuali controlli.


Metodo closeEvent()
Questo metodo è definito all’interno della classe QtGUI.QCloseEvent, la quale contiene i paramenti che vengono chiamati quando l’utente chiude l’interfaccia grafica. Serve per gestire i segnali che vengono emessi nella chiusura, e la sua implementazione di default si occupa di chiudere la finestra. Viene reimplementato in modo tale che, oltre alla chiusura, si effettuino: la distruzione dell’oggetto Agilent (se precedentemente creato), lo spegnimento del generatore di funzioni e la terminazione di un’eventuale acquisizione in modalità continua se l’utente si dimentica di premere i rispettivi pulsanti di “STOP”.
Viene chiamato catturando il segnale aboutToQuit, emesso quando l’utente clicca il pulsante con la “X” per chiudere l’interfaccia:   aboutToQuit.connect(closeEvent()).
 
Metodi per i popup
Per generare i popup è stata usata la classe di Qt QMessageBox che fornisce una finestra di dialogo per informare o fare domande all’utente. Un message box mostra un testo primario che ha la funzionalità di ‘allarme’, un testo informativo per spiegare il problema o porre una domanda e si può scegliere di aggiungere anche un testo dettagliato per fornire ulteriori dati se necessario. Può anche mostrare un’icona e dei pulsanti per l’utente.
Le icone predefinite che possono essere visualizzate sono: Question, Information, Warning e Critical e per settarle bisogna usare la funzione setIcon(), in quanto di default il messageBox non ne mostrerebbe alcuna.
I popup visualizzati nel programma sono:
	show_popupNoChannel(): ha un’icona di Warning e serve per avvisare l’utente della mancata selezione di un canale di acquisizione.
	show_popupNoAcquisition(): presenta un’icona di Warning per segnalare all’utente che sta cercando di salvare un’immagine o un file senza ancora avere acquisito dei dati.
	show_popupSaved(): ha un’icona di Information per informare che il salvataggio è andato a buon fine.
	show_popupSampleRate(): ha un’icona del tipo Critical e avverte l’utente che il valore di frequenza di campionamento inserito non è accettato dallo strumento.



Riferimenti

https://nidaqmx-python.readthedocs.io/en/latest/#

https://github.com/ni/nidaqmx-python

https://www.ni.com/pdf/manuals/371747f.pdf

https://www.ni.com/pdf/manuals/375939a.pdf

https://www.ni.com/pdf/manuals/375939b_02.pdf

https://doc.qt.io/qtforpython/

https://github.com/PyQt5

https://community.sw.siemens.com/s/article/window-correction-factors

https://zone.ni.com/reference/en-XX/help/370689M-01/daqmxtutorial/newconceptsinnidaqmx/






