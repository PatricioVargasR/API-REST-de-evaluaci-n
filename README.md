# API REST de Evaluación

## Descripción
En base a los conceptos y prácticas desarrollados en laboratorio, se ha desarrollado una API REST en Python utilizando FastAPI con las siguientes características:

1. **Crear un archivo contactos.csv** con los siguientes campos (id_contacto, nombre, primer_apellido, segundo_apellido, email, telefono) y agregar 2 registros de prueba.

2. **Endpoint GET /contactos**
   - URL: `http://localhost:8000/contactos`
   - Descripción: Devuelve en formato JSON la lista de todos los contactos almacenados en contactos.csv.

3. **Endpoint POST /contactos**
   - URL: `http://localhost:8000/contactos`
   - Descripción: Permite insertar un nuevo registro en contactos.csv.

4. **Endpoint PUT/PATCH /contactos**
   - URL: `http://localhost:8000/contactos`
   - Descripción: Permite actualizar los datos de un contacto buscándolo por el id_contacto.

5. **Endpoint DELETE /contactos**
   - URL: `http://localhost:8000/contactos`
   - Descripción: Permite borrar un contacto de contactos.csv por el id_contacto.

6. **Endpoint GET /contactos?nombre=Dejah**
   - URL: `http://localhost:8000/contactos?nombre=Dejah`
   - Descripción: Permite buscar contactos que contengan el nombre buscado.

7. **Endpoint POST /imagenes**
   - URL: `http://localhost:8000/imagenes`
   - Descripción: Permite recibir una imagen y guardarla en el sistema.
   - Implementa la posibilidad de seleccionar y aplicar 3 efectos a la imagen enviada, ejemplos:
     - a) `http://localhost:8000/imagenes?crop=0,0,100,100`
     - b) `http://localhost:8000/imagenes?fliph=True`
     - c) `http://localhost:8000/imagenes?colorize=True`

8. **Endpoint Personalizado**
   - Descripción: Ofrece un servicio al usuario, como generador de MD5, generación de números aleatorios, generación o lectura de códigos QR, etc. Se valora la originalidad y complejidad del desarrollo.

**Nota:** Todos los endpoints deben contener una descripción, resumen (abstract) y manejo de errores con códigos de estado específicos.
