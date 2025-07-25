
// Definiciones componentes de la tarjeta
//#define senT1 A0  //TMP36
#define actH1 3   //TIP31C

#include <TimerOne.h>
#include "levitador_lib.h"

float filtro=0;
float acum  = 0.0;
float duracion;
float distancia;
float T1,H1=0.0;
int Trig=10;
int Echo=9;
int senT1;
// **** Interfaz Gráfica *****
// 0: Usa el Serial Plotter;
// 1: Usa la interfaz de Matlab
bool Matlab = false;
int w=0;
unsigned long lastTime = 0;  
const int sampleTime = 50;  // Reducimos el tiempo de muestreo a 50ms (20 Hz)




void setup() {

  
  //Configuramos el puerto serial
  Serial.begin(115200);
  analogWrite(actH1,0);
  pinMode(Echo, INPUT);
  pinMode(Trig, OUTPUT);
}

void loop() {
  if (millis() - lastTime >= sampleTime) {  
    lastTime = millis();}
  String dato,degC;
  int i,ini,fin;
  

  digitalWrite(Trig,LOW);   //  Apagar
  delayMicroseconds(4);
  digitalWrite(Trig,HIGH);   // Encender
  delayMicroseconds(10);
  digitalWrite(Trig,LOW);   //  Apagar    
                            // Envia 8 Pulsos de 40Khz
 
  T1 = TempRead(senT1);

   //********* Recibir datos por puerto serial  ***************
    if (Serial.available()){
      //leemos el dato enviado
      dato=Serial.readString();
      //Busco el valor del escalon en los datos recibidos
      for(i=0;i<10;i++){
        if(dato[i]=='S'){
          ini=i+1;
          i=10;
        }
       }
       for(i=ini;i<10;i++){
        if(dato[i]=='$'){
          fin=i;
          i=10;
        }
       }
       // salvo en degC el caracter con el escalon
      degC=dato.substring(ini, fin);
      H1 = degC.toDouble();  // Convert character string to integers
     

      analogWrite(actH1,map(H1, 0,100, 45,200));
     
    }

   

    //********* Enviar Datos por Puerto Serial *******************
 //Usar el Serial Plotter
    //Serial.println("Distancia(mm),velocidad(%)");
    Serial.print(T1);
    Serial.print(",");
    Serial.println(H1);
 


  
}
