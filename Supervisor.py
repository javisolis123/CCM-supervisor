# import necessary packages
 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import time
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, Float, DateTime, update, Date, Time, exc
from sqlalchemy.sql import select
from sqlalchemy.sql import text as sa_text
import numpy as np
import math



from template import html, html2
def ArmarMensaje(cabecer, cuerpo, footer):
    MensajeTotal = cabecer + cuerpo + footer
    return MensajeTotal

def EnviarEmail(mensaje,asunto, listaDestinos):
    # create message object instance
    msg = MIMEMultipart()
    # setup the parameters of the message
    password = "javiersolis12"
    msg['From'] = "ccmcomteco@gmail.com"
    listaDestinos = ["javier.solis.guardia1@gmail.com", "ccmcomteco@gmail.com"]
    msg['To'] = ','.join(listaDestinos)
    msg['Subject'] = asunto
    # add in the message body
    msg.attach(MIMEText(mensaje, 'html'))
    #create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    # Login Credentials for sending the mail
    server.login(msg['From'], password)    
    # send the message via the server.
    server.sendmail(msg['From'], listaDestinos, msg.as_string())
    server.quit()
    print ("successfully sent email to %s:" % (msg['To']))

def estaVacia(tabla):
    respuesta = 0
    for i in tabla:
        if i.estado == 'activo':
            respuesta = 1
            break
    return respuesta

def listarEmails(tabla):
    lista = []
    for i in tabla:
        lista.append(i.email)
    return lista
    

metadata = MetaData()
alarmas = Table('alarmas', metadata,
                Column('id', Integer, primary_key = True),
                Column('codigo', String()),
                Column('descripcion', String()),
                Column('hora_inicial', Time()),
                Column('fec_inicial', Date()),
                Column('estado', String()),
                Column('estado_email', String())
                )
tecnicos = Table('tecnicos', metadata,
                Column('id', Integer, primary_key = True),
                Column('nombre', String(50)),
                Column('apellido', String(50)),
                Column('num_carnet', String(10)),
                Column('email', String(50)),
                Column('num_cel', String(8))
                )

#Estructura de la talbla ahora
ahora = Table('ahora', metadata,
              Column('id', Integer, primary_key=True),
              Column('temperatura', Float()),
              Column('humedad', Float()),
              Column('canal1', Float()),
              Column('canal2', Float()),
              Column('canal3', Float()),
              Column('canal4', Float()),
              Column('tempGabinete', Float()),
              Column('hora', Time()),
              )

configuracion = Table('configuracion', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('tipo', Integer),
                      Column('frec', Integer),
                      Column('potmax', Float()),
                      Column('potmin', Integer()),
                      Column('tempmax', Integer()),
                      Column('tempmin', Integer()),
                      Column('checkbox', String(15)),
                      Column('ip', String(15))
                      )

regresion = Table('regresion', metadata,
                Column('id', Integer, primary_key = True),
                Column('x1', Float()),
                Column('x2', Float()),
                Column('y', Float()),
                Column('xx', Float()),
                Column('x1y', Float()),
                Column('x2y', Float()),
                Column('x1x2', Float()),
                Column('x2x2', Float()),
                Column('yy', Float())
                )

if __name__ == '__main__':
    while(True):
        tam = 0
        #Se crea un objeto con la conexion a la base de datos de MariaDB
        engine = create_engine('mysql+pymysql://javi:javiersolis12@localhost/tuti')
        connection = engine.connect()
        #Seleccionamos todas las alarmas que esten activas
        query_alarmas_select = select([alarmas]).where(alarmas.c.estado == 'activo')
        res_query_alarmas_select = connection.execute(query_alarmas_select).fetchall()
        #Seleccionamos todos los datos de los técnicos registrados
        query_tecnicos_select = select([tecnicos])
        res_query_tecnicos_select = connection.execute(query_tecnicos_select).fetchall()
        query_configuracion = select([configuracion])
        confi_actual = connection.execute(query_configuracion).fetchone()
        aux = estaVacia(res_query_alarmas_select)
        if (int(time.strftime("%S")) % 5 == 0):
            #Si el query de alarmas no esta vacio
            if(len(res_query_alarmas_select) > 0):
                for i in res_query_alarmas_select:
                    #Envia emails a todos los técnicos registrados
                    if i.estado_email == 'no enviado':
                        cuerpo = "Codigo: " + i.codigo + "   Descripción: " + i.descripcion
                        mensaje = ArmarMensaje(html,cuerpo,html2)
                        lista1 = listarEmails(res_query_tecnicos_select)
                        EnviarEmail(mensaje, 'Alarmas', lista1)
                        query_alarmas_update = update(alarmas).where(alarmas.c.id == i.id).values(estado_email = 'enviado')
                        connection.execute(query_alarmas_update)
        query_alarmas1 = select([alarmas])
        alms = connection.execute(query_alarmas1).fetchall()
        if ( int(time.strftime("%M")) % int(confi_actual.frec) == 0 and int(time.strftime("%S")) == 0 and aux == 0):
            query_select_ahora = select([ahora])
            datosActuales = connection.execute(query_select_ahora).fetchone()
            query_insert_regresion = regresion.insert().values(
                x1 = datosActuales.temperatura,
                x2 = datosActuales.humedad,
                y = datosActuales.canal1,
                xx = (datosActuales.temperatura * datosActuales.temperatura),
                x1y = (datosActuales.temperatura * datosActuales.canal1),
                x2y = (datosActuales.humedad * datosActuales.canal1),
                x1x2 = (datosActuales.temperatura * datosActuales.humedad),
                x2x2 = (datosActuales.humedad * datosActuales.humedad),
                yy = (datosActuales.canal1 * datosActuales.canal1)
            )
            connection.execute(query_insert_regresion)
            print("Se inserto un nuevo dato en regresion")
            time.sleep(1)