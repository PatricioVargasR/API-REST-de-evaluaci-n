# API-REST-de-evaluación
1. Con base en los conceptos y practicas desarrolladas en laboratorio desarrollar una API REST en python utilizando FastAPI con las siguientes características:

1.1 Crear un archivo contactos.csv con los siguientes campos (id_contacto,nombre,primer_apellido,segundo_apellido,email,telefono), agregar 2 registros de prueba.
1.2 Programar el endpoint GET http://localhost:8000/contactos que devuelva en formato JSON la lista de todos los contactos almacenados en contactos.csv
1.3 Programar el endpoint POST http://localhost:8000/contactos que permita insertar un nuevo registro en contactos.csv
1.4 Programar el endpoint PUT/PATCH http://localhost:8000/contactos que permita actualizar los datos de un contacto buscandolo por el id_contacto.
1.5 Programar el endpoint DELETE http://localhost:8000/contactos que permita borrar un contacto de contactos.csv por el id_contacto.
1.6 Programar el endpoint GET http://localhost:8000/contactos?nombre=Dejah que permita buscar contactos que contengan el nombre buscado.

1.7 Programar el endpoint POST http://localhost:8000/imagenes que pemita recibir una imagen y guardarla en el sistema.
1.7.1 Implementar en el endpoint anterior la posibilidad de seleccionar y aplicar 3 efectos a la imagen enviada, ejemplos:
  a) http://localhost:8000/imagenes?crop=0,0,100,100
  b) http://localhost:8000/imagenes?fliph=True
  c) http://localhost:8000/imagenes?colorize=True

1.8 Programar un endpoint que ofrezca un servicio al usuario, por ejemplo generador de MD5, generar números aleatorios, generar o leer códigos QR, etc., se valora la originalidad y complejidad del desarrollo.

Nota: Todos los endpoints deben contener description, abstract y manejo de errores con status_code especificos.
