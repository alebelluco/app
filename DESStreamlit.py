#!/usr/bin/env python
# coding: utf-8

# In[82]:


import simpy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import streamlit as st

st. set_page_config(layout="wide",page_title='DES Lavorazioni Meccaniche' )

st.set_option('deprecation.showPyplotGlobalUse', False)

col1, col2= st.columns([1,20])
with col1:
    #st.image('/Users/Alessandro/Desktop/Header3.png')
    #st.image('/Users/Alessandro/Desktop/logo/logoDMH.png')   
    st.image('https://github.com/alebelluco/app/blob/main/logoDMH.png?raw=True')

with col2:
    st.title('Discrete Event Simulation')
#st.header('Simulazione Isola 5 AD')
##st.markdown('')
st.markdown('')


#st.sidebar.image('/Users/Alessandro/Desktop/logo/logoDMH.png')

st.sidebar.title('Isola 5 AD')

#st.sidebar.header('Isola 5 AD')

#-------------------------------------------------------------------------------------------------------------------------


class Machine(object):
    
    def __init__(self, env, name, part, tempo_ciclo, carico_scarico, 
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0,
                 offset_cq2 = 0, periodo_cq2 = 0, tempo_ciclo_cq2 = 0,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0,                 
                ):
        
        self.env = env
        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        
        self.parts_made = 0        
        self.process = env.process(self.working(operatore)) #avvio l'istanza appena dopo averla creata
        
        
    def working(self, operatore): 
        while True:           
            with operatore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs)  
                    self.log.append('{} | {} | Inizio carico-scarico '.format(env.now-self.cs, self.name ))           
            yield self.env.timeout(self.tc)  #lavoro un pezzo  

            self.parts_made += 1 
            self.qc_count1 += 1 
            self.qc_count2 += 1
            self.qc_count3 += 1
            
            self.log.append('{} | {} | Avvio macchina '.format(env.now-self.tc, self.name)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))

            
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                env.process(CQ_1(self, env, operatore, self.tempo_ciclo_cq1))
                self.qc_count1=0
                
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                env.process(CQ_2(self, env, operatore, self.tempo_ciclo_cq2))
                self.qc_count2=0         
                
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                env.process(CQ_3(self, env, operatore, self.tempo_ciclo_cq3))
                self.qc_count3=0
                
            #self.log.append('{} | {} | Fine ciclo | Pezzo numero {}'.format(env.now, self.name, self.parts_made))
            self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
        print(self.parts_made)

def CQ_1(macchina, env, operatore, tc1):
    while True:
        macchina.log.append('{} | {} | Pezzo pronto per controllo qualità_1'.format(env.now, macchina.name ))          
        yield env.timeout(1) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with operatore.request(priority=1) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tc1) 
            macchina.log.append('{} | {} | Inizio controllo qualità_1'.format(env.now-tc1, macchina.name ))
            macchina.log.append('{} | {} | Fine controllo qualità_1'.format(env.now, macchina.name ))
        break
        
def CQ_2(macchina, env, operatore, tc2):
    while True:
        macchina.log.append('{} | {} | Pezzo pronto per controllo qualità_2'.format(env.now, macchina.name ))          
        yield env.timeout(1) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with operatore.request(priority=1) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tc2) 
            macchina.log.append('{} | {} | Inizio controllo qualità_2'.format(env.now-tc2, macchina.name ))
            macchina.log.append('{} | {} | Fine controllo qualità_2'.format(env.now, macchina.name ))
        break     
        
def CQ_3(macchina, env, operatore, tc3):
    while True:
        macchina.log.append('{} | {} | Pezzo pronto per controllo qualità_3'.format(env.now, macchina.name ))          
        yield env.timeout(1) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with operatore.request(priority=1) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tc3) 
            macchina.log.append('{} | {} | Inizio controllo qualità_3'.format(env.now-tc3, macchina.name ))
            macchina.log.append('{} | {} | Fine controllo qualità_3'.format(env.now, macchina.name ))
        break        



#------------------------------------------------------------------------------
#INSERIMENTO DATI STREAMLIT

path = st.sidebar.file_uploader('Caricare il file di input')
if path is not None:
    #input = pd.read_csv(path, sep=";")
    input = pd.read_excel(path)#,engine='openpyxl')
else:
    st.stop()

input.dropna(inplace=True)
input['Codice']=input['Codice'].astype(str)

st.subheader('Dati di input', divider='red')
st.write(input)

st.subheader('Configurazione isola', divider='grey')
st.image('/Users/Alessandro/Desktop/Isola5.png')

#st.divider()

#selected_time = st.selectbox('Scegliere la durata della simulazione',
#     [0,60,120,240,450])


st.sidebar.divider()
selected_time = st.sidebar.slider('Impostare tempo di simulazione', 0, 450, 240)

st.sidebar.divider()

if st.sidebar.button('Calcola'):
    stop=selected_time
else:
    st.stop()
#if selected_time is not 0:
 #   stop=selected_time
#else:
#    st.stop()

#st.divider()


#------------------------------------------------------------------------------

env = simpy.Environment()
operatore = simpy.PriorityResource(env, capacity=1)  

machines = [Machine(env, 
                    input.Macchina.iloc[0],
                    input.Codice.iloc[0], 
                    input.Tempo_ciclo.iloc[0],
                    input.Carico_scarico.iloc[0],
                    input.O_CQ1.iloc[0],
                    input.P_CQ1.iloc[0],
                    input.T_CQ1.iloc[0],
                    input.O_CQ2.iloc[0],
                    input.P_CQ2.iloc[0],
                    input.T_CQ2.iloc[0],
                    input.O_CQ3.iloc[0],
                    input.P_CQ3.iloc[0],
                    input.T_CQ3.iloc[0]), 
            Machine(env,
                    input.Macchina.iloc[1],
                    input.Codice.iloc[1], 
                    input.Tempo_ciclo.iloc[1],
                    input.Carico_scarico.iloc[1],
                    input.O_CQ1.iloc[1],
                    input.P_CQ1.iloc[1],
                    input.T_CQ1.iloc[1],
                    input.O_CQ2.iloc[1],
                    input.P_CQ2.iloc[1],
                    input.T_CQ2.iloc[1],
                    input.O_CQ3.iloc[1],
                    input.P_CQ3.iloc[1],
                    input.T_CQ3.iloc[1]), 

            Machine(env, 
                    input.Macchina.iloc[2],
                    input.Codice.iloc[2], 
                    input.Tempo_ciclo.iloc[2],
                    input.Carico_scarico.iloc[2],
                    input.O_CQ1.iloc[2],
                    input.P_CQ1.iloc[2],
                    input.T_CQ1.iloc[2],
                    input.O_CQ2.iloc[2],
                    input.P_CQ2.iloc[2],
                    input.T_CQ2.iloc[2],
                    input.O_CQ3.iloc[2],
                    input.P_CQ3.iloc[2],
                    input.T_CQ3.iloc[2])]

#stop=450
env.run(until=stop)


prog = 1
for machine in machines:
    frame = pd.DataFrame([item.split("|", 3) for item in machine.log])
    frame = frame.rename(columns={0:"Minuto",1:"Macchina",2:"Descrizione", 3:"Part"})   
    frame.Minuto = frame.Minuto.astype(float)
    #dal data frame unico estraggo: frame_prod (relativo solo a carico-scarico), frame_cq (relativo solo a controlli qualità), per calcolare la durata delle fasi
    frame_prod = frame[(frame['Descrizione'] == ' Inizio carico-scarico ') | (frame['Descrizione'] == ' Avvio macchina ') | (frame['Descrizione'] == ' Fine ciclo ')]
    #frame_prod = frame_prod.sort_values(by=['Minuto'])    
    frame_prod['Durata'] = frame_prod.Minuto.shift(-1) - frame_prod.Minuto
    frame_prod = frame_prod.replace({' Inizio carico-scarico ':'Carico-Scarico', ' Avvio macchina ':'Machining', ' Fine ciclo ':'Attesa operatore'})
    
    #aggiungo le colonne C, M, A per poter fare il grafico unico
    frame_prod['C{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Carico-Scarico',frame_prod.Durata,0)
    frame_prod['M{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Machining',frame_prod.Durata,0)
    frame_prod['A{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Attesa operatore',frame_prod.Durata,0)
    
    
    frame_cq = frame[(frame['Descrizione'] == ' Inizio controllo qualità_1') | (frame['Descrizione'] == ' Fine controllo qualità_1') | 
                     (frame['Descrizione'] == ' Inizio controllo qualità_2') | (frame['Descrizione'] == ' Fine controllo qualità_2') | 
                     (frame['Descrizione'] == ' Inizio controllo qualità_3') | (frame['Descrizione'] == ' Fine controllo qualità_3')]   
    
    #frame_cq = frame_cq.sort_values(by=['Minuto'])    
    frame_cq['Durata'] = frame_cq.Minuto.shift(-1) - frame_cq.Minuto
    frame_cq = frame_cq.replace({' Inizio controllo qualità_1':'CQ_tipo1', ' Inizio controllo qualità_2':'CQ_tipo2',' Inizio controllo qualità_3':'CQ_tipo3'})
    frame_cq = frame_cq[(frame_cq['Descrizione']=='CQ_tipo1') | (frame_cq['Descrizione']=='CQ_tipo2') | (frame_cq['Descrizione']=='CQ_tipo3')]
    #aggiungo le colonne CQ per poter fare il grafico unico
    frame_cq['CQ_M{}'.format(prog)]=np.where((frame_cq['Descrizione']=='CQ_tipo1') | (frame_cq['Descrizione']=='CQ_tipo2') | (frame_cq['Descrizione']=='CQ_tipo3'),frame_cq.Durata,0)
    
    frame.dropna(inplace=True)
    frame.reset_index(inplace=True)

    globals()['frame_prod{}'.format(prog)]=frame_prod
    globals()['frame_cq{}'.format(prog)]=frame_cq
    prog += 1 
#-----------------------------------------------------------------------------------------------------------------------------
# Aggiungere o togliere i dataframe in base alle macchine   
gantt = pd.concat([frame_prod1,frame_prod2,frame_cq1,frame_cq2,frame_prod3,frame_cq3])    

gantt = gantt.sort_values(by=['Macchina','Minuto'])
gantt = gantt.fillna(0)
gantt.reset_index(inplace=True)

Carico_scarico = gantt.C1.sum()+gantt.C2.sum()+gantt.C3.sum()
Controllo_qualità = gantt.CQ_M1.sum()+gantt.CQ_M2.sum()+gantt.CQ_M3.sum()
Saturazione_op = np.round((Carico_scarico+Controllo_qualità)/stop,2)*100
Tempo_passivo = stop - Carico_scarico - Controllo_qualità


for i in range(len(machines)):
    colonna = 'M{}'.format(i+1)
    globals()['Uptime_{}'.format(machines[i].name)] = np.round(gantt[colonna].sum()/stop,2)*100    

grafico = gantt[['Descrizione','Minuto','C1','M1','C2','M2','C3','M3','CQ_M1','CQ_M2','CQ_M3']][gantt['Descrizione']!='Attesa operatore']
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(20,13))

y_pos = np.arange(0,len(grafico),step=1)
ax.barh(y_pos, grafico.Minuto, color='black')
ax.barh(y_pos, grafico.C1, left=grafico.Minuto, color='red')
ax.barh(y_pos, grafico.C2, left=grafico.Minuto, color='red')
ax.barh(y_pos, grafico.C3, left=grafico.Minuto, color='red')
ax.barh(y_pos, grafico.M1, left=grafico.Minuto, color='grey')
ax.barh(y_pos, grafico.M2, left=grafico.Minuto, color='grey')
ax.barh(y_pos, grafico.M3, left=grafico.Minuto, color='grey')
ax.barh(y_pos, grafico.CQ_M1, left=grafico.Minuto, color='red')
ax.barh(y_pos, grafico.CQ_M2, left=grafico.Minuto, color='red')
ax.barh(y_pos, grafico.CQ_M3, left=grafico.Minuto, color='red')

ax.invert_yaxis()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(True)
ax.grid('on', linewidth=0.2)
ax.tick_params(right=False, left=False, axis='y', color='r', length=16,grid_color='none')
ax.tick_params(axis='x', color='black', length=4, direction='in', width=4,labelcolor='w', grid_color='grey',labelsize=10)
ax.tick_params(axis='y', color='black', length=4, direction='in', width=4,labelcolor='w')
plt.xticks(np.arange(0,stop,step=(stop/10)))
plt.yticks(np.arange(0,len(grafico),step=20))

grafico['x_pos']=grafico.Minuto+grafico.C1+grafico.C2+grafico.C3+grafico.M1+grafico.M2+grafico.M3+grafico.CQ_M1+grafico.CQ_M2+grafico.CQ_M3

for i in range(len(grafico)):
    x_pos = grafico.x_pos.iloc[i]+0.3
    if grafico.Descrizione.iloc[i]!='Machining' and grafico.Descrizione.iloc[i]!='Carico-Scarico' :
        ax.text(x_pos, i, grafico.Descrizione.iloc[i], fontsize=5, fontname='Avenir',backgroundcolor='black')

st.subheader('Output simulazione', divider='red')

col1, col2, col3 = st.columns(3)
with col1:
   st.markdown(machines[0].name)
   st.write (frame_prod1[['Minuto','Macchina','Descrizione','Durata']])
with col2:
   st.markdown(machines[1].name)
   st.write (frame_prod2[['Minuto','Macchina','Descrizione','Durata']])
with col3:
   st.markdown(machines[2].name)
   st.write (frame_prod3[['Minuto','Macchina','Descrizione','Durata']])


col1, col2 = st.columns([2,1])
with col1:
   st.subheader('Gantt', divider='red')
   st.pyplot(fig)

with col2:
    st.subheader('Risultato simulazione',divider='red')
    for macchina in machines: 
        testo = ' {} | Codice{} | Output: {} pcs'.format(macchina.name,macchina.part,macchina.parts_made)
        valore = globals()['Uptime_{}'.format(macchina.name)]
        testo2 = 'Uptime_{} : {}%'.format(macchina.name,valore)
        testo3 = 'Codice *{}* | :red[Ta={}]'.format(macchina.part,np.round(stop/macchina.parts_made/3,2))
        st.write(testo)
        st.write(testo2)
        st.write(testo3)
        st.write('--------------------------------------')
    st.write('Saturazione operatore: {}%'.format(Saturazione_op))


img = io.BytesIO()
fig.set_size_inches(30,20)
fig.savefig(img, format='png', dpi=300)
st.download_button(label="Download high-res", data=img, file_name='Gantt.png')

#st.header('Sviluppare dowload report in PDF')


