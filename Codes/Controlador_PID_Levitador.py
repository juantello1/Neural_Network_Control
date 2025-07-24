import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
from matplotlib.widgets import TextBox

import numpy as np
import pandas as pd  
import serial
import time
import sys


def scale_output1(value, min_scaled, max_scaled, min_output, max_output):
    return np.interp(value, (min_scaled, max_scaled), (min_output, max_output))



ser = serial.Serial('COM4', 115200)  # Reemplaza 'COMX' con el puerto correcto
time.sleep(1)
# while True:  #comprueba la velocidad en la transmision de datos que envia y manda arduino
#     if ser.in_waiting > 0:
#         data = ser.readline().decode().strip()
#         if data:
#             print("Datos recibidos:", data)
    
#Modelo del sistema en FT
K=0.7164
theta1=0.195
tau=1.76
Ts = 0.3  # Periodo de muestreo
theta=theta1+ Ts/2


# Variables globales
setpoint = 0
T1 = 0.0  # Sensor de altura
H1 = 0.0  # Acción de control
w = 0.0   # Referencia
e = [0, 0, 0]  # Vector de error
u = [0, 0]  # Vector de control
tiempo=[0,0]
sp = [0, 0]
y = [0, 0]
eyy=[0,0]
t = 0          #Tiempo
uk2= 0
e1=0
e2=0
e3=0
k=[]
pwm=[0,0]

#COHENCOON PID
# kp=(1.35+((0.25)*(theta/tau)))*((tau)/(K*theta))*0.7
# Td=(0.5*theta)/(1.35+((0.25)*(theta/tau)))


#Controlador Cohencoon PI
# kp= ((tau/(K*theta)*((9/10)+(theta/12*tau))))
# Ti=((theta*(30*tau)+(3*theta))/(9*tau+20*theta))    
# Td=0  

#Zn PI
kp =0.9*tau/(K*theta)
Ti=3.3*theta
Td=0

#ZN PID
# kp =1.2*tau/(K*theta)
# Ti=2*theta
# Td=0.5*theta

#IAE PI
# kp=(1/K)*(0.984*(theta/tau)**(-0.986))
# Ti=(tau)/(0.608*(theta/tau)**(-0.707))
# Td=0
#IAE PID
# kp=(1/K)*(1.435*(theta/tau)**(-0.921))
# Ti=(tau)/(0.878*(theta/tau)**(-0.749))
# Td=(tau)*(0.482*(theta/tau)**(1.137))
print(kp,Ti,Td)


# Define the figure and axis
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.1, bottom=0.25)
ln1, = plt.plot([], [], 'r-', label='SetPoint')
ln2, = plt.plot([], [], 'b-', label='HIGH')
ln3, = plt.plot([], [], 'g-', label='PWM Output')

# Add sliders for setpoint
axcolor = 'lightgoldenrodyellow'
# Crear un eje para el TextBox en la interfaz
ax_textbox = plt.axes([0.7, 0.05, 0.1, 0.05], facecolor=axcolor)
setpoint_textbox = TextBox(ax_textbox, 'Setpoint', initial=str(setpoint))
def init():
    ax.set_xlim(0, 2000)
    ax.set_ylim(0, 100)#255
    return ln1, ln2, ln3

def update_setpoint(text):
    global setpoint
    try:
        setpoint = int(text)  # Convertir a entero
    except ValueError:
        print("Ingrese un número entero válido")
        
def save_to_excel():
    data = {
        'Time': tiempo,
        'Setpoint': sp,
        'High': y,
        'PWM': u
    }
    df = pd.DataFrame(data)
    df.to_excel('Levitator_control_data.xlsx', index=False)
    print("Data saved to Levitator_control_data.xlsx")

# Define a callback to save the data when the plot window is closed
def on_close(event):
    save_to_excel()
    ser.close()
    

def update(frame):
    global T1,y,tiempo,u,sp,eyy,setpoint,t,pwm
    while True:
        # Medir el tiempo de ejecución del control
        setpoint_textbox.on_submit(update_setpoint)        
        q0=(kp*((1+Ts/(2*Ti))))
        q1=(-kp)*((1-Ts/(2*Ti)))
        q2=int(((kp*Td)/Ts))
        
        print(q0,q1)
        # Leer datos desde Arduino
        line = ser.readline().decode().strip()  # Decodificar y limpiar la cadena
        #time.sleep(0.3)
        datos = line.split(',')
        T1 = round(float(datos[0]))
        T1=int(T1)
        y.append(T1)
        sp.append(setpoint)
        print(f"altura recibida: {T1}")
        
        # Medir el tiempo de ejecución del control neuronal
        control_start_time = time.time()
        #Lazo Cerrado de Control
        
        
        #=====================================================#
        #============         PROCESO REAL        ============#
        #=====================================================#
        yk= T1
        
        
        #=====================================================#
        #============       CALCULAR EL ERROR     ============#
        #=====================================================#
        ey=setpoint-yk
        print('error',ey)
        eyy.append(ey)
        
        e2 = eyy[t-1]
        print('error 1',e2)
        e3 = eyy[t-2]
        print('error 2',e3)
               
        #=====================================================#
        #===========   CALCULAR LA LEY DE CONTROL  ===========#
        #=====================================================#
        #bias= (y[k]-y[0])/kss
              
        
        uk= round((q0*ey) + (q1*e2) + q2*e3 +u[t-1] )
        u.append(uk)
         
    
        t+=1
        print(t)
        tiempo.append(t)
          
        
        H1= int(uk)
        #uk2=H1
        print(H1)
        
        print(uk)
        print(u[t-1])    
    
        # Enviar la señal de control a Arduino
        
        control=scale_output1(H1,0,1000,0,100)
        control=round(float(control))
        control=int(control)
        pwm.append(control)
        control=f"S{control}$"
        print(f"control: {control}")
        ser.write(control.encode())
        #time.sleep(0.3)
        print(f"control: {control}")
        sys.stdin.flush()
        # Medir el tiempo de finalización del control neuronal
        control_end_time = time.time()
        control_time = control_end_time - control_start_time
        print('Time taken for control = {} sec'.format(control_time))
        # Update plot data
        ln1.set_data(tiempo, sp)
        ln2.set_data(tiempo, y)
        ln3.set_data(tiempo, pwm)
   
        # ax.relim()
        ax.autoscale_view()
        return ln1, ln2, ln3
       
    
# Register the callback
fig.canvas.mpl_connect('close_event', on_close)

# Update the animation function to include slider updates
ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=1000)

# plt.xlabel('Time (s)')
# plt.ylabel('Value')
# plt.legend()
# plt.show()               
      