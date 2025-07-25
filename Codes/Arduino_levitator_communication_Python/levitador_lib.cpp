

#include "levitador_lib.h"
const int Trigger = 10;
const int Echo = 9;

float TempRead(int sen)
{
  pinMode(Trigger, OUTPUT);
  pinMode(Echo, INPUT);
  digitalWrite(Trigger, LOW);
  int S1;
  long t; //Tiempo de regreso
  long d; //Distancia en centímetros
  int med;
 
  digitalWrite(Trigger, HIGH);
  delayMicroseconds(10); //Se envía un pulso de 10us
  digitalWrite(Trigger, LOW);
 
  t = pulseIn(Echo, HIGH);
  d = t/59; //Se obtiene la distancia en centímetros
  //med=(((d-2.0)/(100.0-2.0))*(-60.0))+60.0;
 // med=(((d-2.0)/(100.0-2.0))*(-66.0))+66.0;
  med= 64-d;
  if(d>=64){
    med=0;
  }
   /*if(d<=7){
    med=0;
  }*/
  //med= d;
  S1 = med;
  return(S1);
}

//Sensor analalogo sharp
/*float TempRead(int sen)
{
 float S1,aux;
  int i,S2;
  Filtro de promedio movil en la lectura ADC
  /*aux=0;
  for(i=0;i<100;i++){
    aux = (((aux + 12902.0*pow(float(analogRead(sen)),-1.027))));
    //aux = aux + (((28940.1*pow(float(analogRead(sen)),-1.16))));
  
    //delay(2); 
  }  
  S1 = aux/100.0;

  S2=((S1-65.5)/(10.0-65.5))*100;
  if (S2<0){
    S2=0;
    }
 
  //S1 = (S1);//para invertir la medida con una escalizacion
  return(S2);
}*/
