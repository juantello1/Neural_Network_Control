
"""
# Neural_Network_Controller.py
# This script implements a neural network controller for a system using data from an Arduino.   
@author: jmtm
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd  
import random
import serial
import time
import sys


def scale_output(value, min_scaled, max_scaled, min_output, max_output):
    return np.interp(value, (min_scaled, max_scaled), (min_output, max_output))

puerto = 'COM4'  
velocidad = 112500  
arduino = serial.Serial(puerto, velocidad)
# Transfer Function----------------------
# k = 0.7164
# tao=1.76
# delta = 0.3 #intervalos de la simulacion

#inicializacion de variables--------------------
t = 0
z = [0, 0]
y = 0
tt = [0, 0]
uu = [0, 0]
nnu = [0,0]
xe2 = 0
xe3 = 0
eyy = [0,0]
alfa = [0.8]
uc = 0
uu = [0, 0]
alfaa=0.8

# # Random wji
we11 = random.random()
we12 = random.random()
we13 = random.random()

we21 = random.random()
we22 = random.random()
we23 = random.random()

we31 = random.random()
we32 = random.random()
we33 = random.random()

# # Random for vj
ve1 = random.random()
ve2 = random.random()
ve3 = random.random()


emin=-64
emax=64
w = int(input("Input the Setpoint (en cm): "))

try:
    while True:
        if t>=400: 
            w=50
        if t>=800:
            w=15
        if t>=1200:
            w=40
        # Line Read
        linea = arduino.readline().decode().strip()
        time.sleep(0.5)

        datos = linea.split(',') 

       # Procesar los datos
        T1 = round(float(datos[0]))
        T1=int(T1)
  
        
       #setpoint=datos[1]
        print("Distancia:", T1)
        print("Setpoint:", w)
        print('tiempo=',t)
        #Control neuronal------------------------------------------------------
         
        z.append(T1)
        t=t+1
        uu.append(w)
        tt.append(t)
        # Time Execution 
        control_start_time = time.time()

        #Control
        ey_1  = w -T1
        ey=ey_1/100
        print('error normal',ey_1)

        print('el error escalizado',ey)
        eyy.append(ey)
        
        xe1 = ey 
        xe2 = eyy[t-1]
        xe3 = eyy[t-2]
        he1 = (we11*xe1)+(we21*xe2)+(we31*xe3)
       # he1 = np.clip(he1, -80, 80)
        he1 = 1/(1+np.exp(-he1))
        
        he2 = (we12*xe1)+(we22*xe2)+(we32*xe3)
       # he2 = np.clip(he1, -80, 80)
        he2 = 1/(1+np.exp(-he2))

        he3 = (we13*xe1)+(we23*xe2)+(we33*xe3)
        #he3= np.clip(he1, -80, 80)
        he3 = 1/(1+np.exp(-he3))

        uc = (ve1*he1)+(ve2*he2)+(ve3*he3)
        uc = 1/(1+np.exp(-uc))
      
        
        print('salida al arduino',uc)
        control =scale_output(uc, 0, 1, 0, 64)
        control=scale_output(control,0,64,0,100)
        control=round(float(control))
        control=int(control)
        nnu.append(control)
        #control=int(control)*100
        control=f"S{control}$"
        arduino.write(control.encode())
        time.sleep(0.01)
        print('arduino write',control)
        #Actualizacion de pesos 
        s = ey*uc*(1-uc)

        ve1 = ve1+(alfaa*s*he1)
        #ve1.append(ve1a)
        ve2 = ve2+(alfaa*s*he2)
        #ve2.append(ve2a)
        ve3 = ve3+(alfaa*s*he3)
        #ve3.append(ve3a)

        s1 = s*ve1*he1*(1-he1)
        s2 = s*ve1*he2*(1-he2)
        s3 = s*ve1*he3*(1-he3)

        we11 =  we11+(alfaa*s1*xe1)
        #we11.append(we11a)
        we12 =  we12+(alfaa*s2*xe2)
        #we12.append(we12a)
        we13 =  we13+(alfaa*s3*xe3)
        #we13.append(we13a)

        we21 =  we21+(alfaa*s1*xe1)
        #we21.append(we21a)
        we22 =  we22+(alfaa*s2*xe2)
        #we22.append(we22a)
        we23 =  we23+(alfaa*s3*xe3)
        #we23.append(we23a)

        we31 =  we31+(alfaa*s1*xe1)
        #we31.append(we31a)
        we32 =  we32+(alfaa*s2*xe2)
        #we32.append(we32a)
        we33 =  we33+(alfaa*s3*xe3)
        #we33.append(we33a)

        alfaa = 0.5 + (0.98 * np.abs(ey))
        print('tasa de apren',alfaa)
        #alfaa = 7
        alfa.append(alfaa)
        # Medir el tiempo de finalización del control neuronal
        control_end_time = time.time()
        control_time = control_end_time - control_start_time
        print('Time taken for control = {} sec'.format(control_time))
    
        print("Distancia:", T1)
        print("Setpoint:", w)
        sys.stdin.flush()


except KeyboardInterrupt:
    arduino.close() 
# Crear un DataFrame de pandas con los datos
data = {'Entrada': uu, 'Salida': z,'pwm':nnu}
df = pd.DataFrame(data)

# Guardar el DataFrame en un archivo Excel
excel_file = 'neuronal_prueba_moneda.xlsx'
df.to_excel(excel_file, index=False)

# Imprimir mensaje de confirmación
print(f"Datos guardados en '{excel_file}'")
print(we11,we12,we13,we21,we22,we23,we31,we32,we33,ve1,ve2,ve3)

# Crear el gráfico
tt = tt[:len(z)]
fig, axs = plt.subplots(2)
plt.figure(1)
axs[0].plot(tt, z, color="black", label="Output")
axs[0].plot(tt, uu, color="blue", label="Set-Point")
axs[0].plot(tt, eyy, color="green", label="Error")
axs[1].plot(tt, nnu, color="blue", label="Control")
plt.tight_layout()
# Configurar el estilo del texto
font_style = {
    'family': 'serif',  
    'weight': 'bold',   
    'size': 12           
}

# Agregar título y etiquetas de ejes con estilo personalizado
axs[0].set_title("Controlador RNA-Autoajustable", fontdict=font_style)
axs[0].set_xlabel("Tiempo", fontdict=font_style)
axs[0].set_ylabel("Altura (cm)", fontdict=font_style)
axs[1].set_xlabel("Tiempo", fontdict=font_style)
axs[1].set_ylabel("PWM(%)", fontdict=font_style)

# Configurar el tamaño de la fuente de la leyenda
axs[0].legend(fontsize=14)
axs[1].legend(fontsize=14)

# Agregar una cuadrícula
axs[0].grid(True)
axs[1].grid(True)

# Mostrar el gráfico
plt.show()
    
#agregar vectores a excel
# data={'Salida':z,'Setpoint':uu,'Error':eyy,'Control':nnu}
# df= pd.DataFrame(data)
