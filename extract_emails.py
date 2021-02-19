#Importar librerias necesarias
import string
import hashlib
import sys
import imaplib
import email
import MySQLdb
from email.header import Header, decode_header, make_header
import mysql.connector

#Conectar con el servidor de correo
HOST     = 'imap.gmail.com'
USERNAME = 'm3rl12021@gmail.com'
PASSWORD = ''

#Conectar con la base de datos.
mydb = MySQLdb.connect(host='localhost',
                       user='root',
                       passwd='',
                       db='ok')

#Definir Variables
cur = mydb.cursor()
m = imaplib.IMAP4_SSL(HOST, 993)
m.login(USERNAME, PASSWORD)
m.select('INBOX')

#Empezamos a leer los mensajes del correo
result, data = m.uid('search', None, "ALL")
if result == 'OK':
#Empezamos un recorrido por el buzon.
    for num in data[0].split()[:10]:
        result, data = m.uid('fetch', num, '(RFC822)')
        if result == 'OK':
            #Obtenemos todo el mensaje
            email_message_raw = email.message_from_bytes(data[0][1])

            #Leemos los datos que vamos a insertar en la base de datos, de, fecha y asunto
            email_from = str(make_header(
                decode_header(email_message_raw['From'])))

            email_fecha = str(make_header(
                decode_header(email_message_raw['Date'])))

            email_asunto = str(make_header(
                decode_header(email_message_raw['Subject'])))

            #inicializamos variable que contiene los 3 datos, de, fecha y asunto.
            unique_id = email_from + email_asunto + email_fecha #+ cuerpo_del_email_SIN_fecha
            #Sacamos hash md5 para identificar cada correo en BD y asi evitar que no hayan registros repetidos
            unique_id = (hashlib.md5(unique_id.encode())).hexdigest()
            #En el siguiente condicional, filtramos los correos que tengan en su contenido la palabra risk.
            if 'risk' in str(email_message_raw).lower().split():
                #Insertamos las variable en nuestra BD, aclarando que el parametro ignore, evita que el registro no sea duplicado.
                sql = ("INSERT IGNORE INTO merli(hid, nombre, fecha, asunto) VALUES(%s, %s, %s,%s)",(unique_id, email_from, email_fecha, email_asunto)) 
                #ejecutamos el query
                cur.execute(*sql)
                mydb.commit()

# Close server connection
m.close()
m.logout()
