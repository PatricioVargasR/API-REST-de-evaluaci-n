from fastapi import FastAPI, status, UploadFile, File, Query, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from pytube.exceptions import VideoUnavailable
from urllib.parse import urlparse, parse_qs
from fastapi.staticfiles import StaticFiles
from pytube.helpers import safe_filename
from pydantic import BaseModel, EmailStr
from uuid import uuid4 as uuid
from datetime import datetime
from pytube import YouTube
from typing import List
from io import BytesIO
from PIL import Image
import re
import os
import csv

app = FastAPI()

# Carpeta donde se guardarán los archivos
upload_folder = "static/images"


# Carpeta donde se guardarán los videos
upload_folder_video = "static/videos"

# Permitimos ver la carpeta donde se sube la imagen
app.mount("/static", StaticFiles(directory="static"), name="static")


class Post(BaseModel):
    id:str
    nombre: str
    primer_apellido: str
    segundo_apellido: str
    email: EmailStr
    telefono: int

class Update(BaseModel):
    nombre: str
    primer_apellido: str
    segundo_apellido: str
    email: EmailStr
    telefono: int
    
class VideoRequest(BaseModel):
    url: str
    calidad: str = None
    subtitulos: bool = None
    formato_subtitulos: str = None


@app.get("/", status_code=status.HTTP_200_OK, summary="Endpoint raíz")
def read_root():
    """
    # Endpoint raíz
    
    ## 1- Status Codes:
    * 200 - Código de confirmación
    * 201 - Código de confirmación de creación
    * 204 - Código de no contenido
    * 400 - Código mala solicitud
    * 404 - Código de no encontrado
    * 409 - Código de conflicto en la solicitud
    * 500 - Error interno del servidor
    """
    return {"Developed by":"Patricio de Jesús f:"}

@app.get("/contactos", status_code=status.HTTP_200_OK, summary="Endpoint para listar datos")
def get_contactos():
    """
    # Endpoint para obtener datos de la API

    ## 1.- Status Codes:
    * 200 - Código de confirmación
    """

    # Verificar si el archivo existe antes de intentar abrirlo
    if not os.path.exists('contactos.csv'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    datos = []
    with open('contactos.csv', 'r') as file:
        lector = csv.DictReader(file)
        for row in lector:
            datos.append(row) 
    
        if len(datos) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Datos no encontrados"
            )      
        return datos

@app.post("/contactos", status_code=status.HTTP_201_CREATED, summary="Endpoint para enviar datos")
def add_contactos(post: Post):
    """
    # Endpoint para enviar datos de la API

    ## 1.- Status Codes:
    * 201 - Código de confirmación de agregar nuevo elemento
    * 404 - Código de error en caso de que no exista el csv
    * 409 - Conflicto en la solicitud
    * 500 - Error interno en el servidor


    ## 2.- Data:
    * nombre: str
    * email: EmailStr
    """ 
    try:
        # Verificar si el archivo existe antes de intentar abrirlo
        if not os.path.exists('contactos.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo no encontrado",
            )

        registros = []
        id_conflict = False  # Bandera para verificar conflicto de ID

        with open('contactos.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['id'] == post.id:
                    id_conflict = True
                    break
                registros.append(row)

        if id_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,  # Conflict
                detail=f"El registro con ID {post.id} ya existe",
            )

        with open('contactos.csv', 'a', newline="") as file:
            fieldnames = ["id", "nombre", "primer_apellido", "segundo_apellido", "email", "telefono"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            row = post.model_dump()
            writer.writerow(row)
        
        return row, {"datetime": datetime.now()}
    
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo de contactos no encontrado")
    
    except HTTPException as he:
        raise he
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")
    

@app.get("/contactos/{nombre}", status_code=status.HTTP_200_OK, summary="Endpoint para listar datos")
def get_contactos_nombre(nombre: str):
    """
    # Endpoint para obtener datos específicos de la API

    ## 1.- Status Codes:
    * 200 - Código de confirmación
    * 400 - Tipo de dato incorrecto
    * 404 - Registro no encontrado
    * 500 - Error interno en el servidor
    """
    try:
        # Verificar si el archivo existe antes de intentar abrirlo
        if not os.path.exists('contactos.csv'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado",
            )

        if nombre.isnumeric():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Datos incorrectos: El nombre no debe ser un número",
            )
        
        registros = []

        with open('contactos.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['nombre'] == nombre:
                    registros.append(row)

        if not registros:
            # Si no se encontraron registros con el nombre especificado
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron registros con el nombre '{nombre}'"
            )
        return registros

    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo de contactos no encontrado")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")  

# @app.get("/contactos_query", status_code=status.HTTP_200_OK, summary="Endpoint para listar datos")
# def get_contactos_query(nombre: str = Query()):
#     """
#     # Endpoint para obtener datos específicos de la API

#     ## 1.- Status Codes:
#     * 200 - Código de confirmación
#     * 400 - Tipo de dato incorrecto
#     * 404 - Registro no encontrado
#     * 500 - Error interno en el servidor
#     """
#     try:
#         # Verificar si el archivo existe antes de intentar abrirlo
#         if not os.path.exists('contactos.csv'):
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Archivo no encontrado",
#             )

#         if nombre.isnumeric():
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Datos incorrectos: El nombre no debe ser un número",
#             )
        
#         registros = []

#         with open('contactos.csv', 'r') as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 if row['nombre'] == nombre:
#                     registros.append(row)

#         if not registros:
#             # Si no se encontraron registros con el nombre especificado
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"No se encontraron registros con el nombre '{nombre}'"
#             )
#         return registros

#     except FileNotFoundError:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo de contactos no encontrado")
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")  


@app.delete("/contactos/{id}", status_code=status.HTTP_204_NO_CONTENT, summary='Endpoint para eliminar un recurso')
def delete_contactos(id: str):
    """
    # Endpoint para eliminar un recurso de la API

    ## 1.- Status Codes:
    * 204 - No content
    * 404 - Archivo no encontrado
    * 400 - Bad Request
    * 500 - Error interno en el servidor
    """ 
    try:
        # Verificar si el archivo existe antes de intentar abrirlo
        if not os.path.exists('contactos.csv'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado",
            )

        if not id.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID no válido, debe ser un número",
            )

        registro = []
        registro_encontrado = False  # Bandera para verificar si se encontró un registro

        with open('contactos.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['id'] == id:
                    registro_encontrado = True
                else:
                    registro.append(row)

        if not registro_encontrado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro con ID {id} no encontrado",
            )

        with open('contactos.csv', 'w', newline='') as file:
            fieldnames = ["id", "nombre", "primer_apellido", "segundo_apellido", "email", "telefono"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for row in registro:
                writer.writerow(row)

        return {"id_item": id, "datetime": datetime.now()}
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo de contactos no encontrado")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")

@app.put("/contactos/{id}", status_code=status.HTTP_200_OK, summary='Endpoint para actualizar datos')
def update_contactos(id: str, update: Update):
    """
    # Endpoint para actualizar datos

    ## 1.- Status Codes:
    * 200 - OK
    * 400 - Bad Request
    * 404 - Archivo no encontrado
    * 500 - Error interno en el servidor

    ## 2.- Data:
    * nombre: str
    * primer_apellido: str
    * segundo_apellido: str
    * email: EmailStr
    * telefono: int 
    """

    try:
        # Verificar si el archivo existe antes de intentar abrirlo
        if not os.path.exists('contactos.csv'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado"
            )
        
        if not id.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID no válido, debe ser un número",
            )

        registros = []
        registro_actualizado = False

        with open('contactos.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['id'] == id:
                    registro_actualizado = True
                    row['nombre'] = update.nombre
                    row['primer_apellido'] = update.primer_apellido
                    row['segundo_apellido'] = update.segundo_apellido
                    row['email'] = update.email
                    row['telefono'] = update.telefono

                registros.append(row)

        if not registro_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro con ID {id} no encontrado",
            )

        with open('contactos.csv', 'w', newline='') as file:
            fieldnames = ["id", "nombre", "primer_apellido", "segundo_apellido", "email", "telefono"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(registros)

        return {"datetime": datetime.now()}
    
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo de contactos no encontrado")
    except HTTPException as he:
        raise he  
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")

@app.post("/subir_imagen", status_code=status.HTTP_201_CREATED, summary="Endpoint para subir imágenes")
async def crear_imagen(
    files: List[UploadFile] = File(...),
    cortar: str = Query(None),
    rotar: str = Query(None),
    redimensionar: str = Query(None)
):
    """
    # Endpoint para subir una imagen y aplicarle filtros

    ## 1.- Status Codes:
    * 201 - Archivo creado
    * 400 - Bad Request
    * 404 - Archivo no encontrado
    * 500 - Error interno en el servidor

    ## 2.- Data:
    * nombre: str
    * primer_apellido: str
    * segundo_apellido: str
    * email: EmailStr
    * telefono: int 
    """

    try:
        # Verifica si la carpeta existe, si no, la crea
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        for archivo in files:
            # Lee el archivo enviado
            image = Image.open(BytesIO(archivo.file.read()))

            # Variables para controlar errores en operaciones
            error_cortar = False
            error_rotar = False
            error_redimensionar = False

            # Si se asignó el parámetro para cortar
            if cortar:
                try:
                    izquierda, arriba, derecha, abajo = map(int, cortar.split(","))
                    image = image.crop((izquierda, arriba, derecha, abajo))
                except Exception:
                    error_cortar = True

            # Si se asignó el parámetro para rotar
            if rotar:
                try:
                    angulo = int(rotar)
                    image = image.rotate(angulo)
                except Exception:
                    error_rotar = True

            # Si se asignó el parámetro para redimensionar
            if redimensionar:
                try:
                    ancho, alto = map(int, redimensionar.split(","))
                    image = image.resize((ancho, alto))
                except Exception:
                    error_redimensionar = True

            if error_cortar or error_rotar or error_redimensionar:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Error en una o más operaciones de edición de la imagen",
                )

            # Cambiamos el nombre de la imagen
            nombre, extension = archivo.filename.split(".")
            nombre = str(uuid())

            image.save(os.path.join(upload_folder, f"{nombre}.{extension}"))

        return {"message": "Archivos subidos y editados correctamente", 
                "URL": f"{upload_folder}/{nombre}.{extension}"}

    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La carpeta de carga no existe.")
    
    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")

    
@app.post("/descargar_videos", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Endpoint para descargar videos")
async def descargar_videos(
    youtube_url: str,
    calidad_video: str = Query(None),
    descargar_subtitulos: bool = Query(False),
    descargar_videos: bool = Query(True),
    formato_subtitulos: str = Query(None)
):
    """
    # Endpoint para descargar videos de youtube con y sin subtitulos

    ## 1.- Status Codes:
    * 201 - Archivo creado
    * 400 - Bad Request
    * 404 - Archivo no encontrado
    * 500 - Error interno en el servidor

    ## 2.- Data:
    * youtube_url: str
    * calidad_video: str
    * descargar_subtitulos: bool
    * formato_subtitulo: str
    """

    patron = r'(https?://)?(www\.)?youtube\.com/watch\?v=([A-Za-z0-9_-]+)'
    formatos = ["txt", "vtt", "str"]
    calidad = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p"]
    coincidencia = re.match(patron, youtube_url)      

    if not coincidencia:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No es una URL correcta",
        )
    
    if not descargar_videos and not descargar_subtitulos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se debe elegir al menos una opción",
        )
    
    try:
        
        if descargar_subtitulos and descargar_videos:
            if not formato_subtitulos or not calidad_video:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se especificó un parámetro"
                )
            if calidad_video not in calidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Calidad de video invalida",
                )
            if formato_subtitulos not in formatos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El formato no es correcto",
                )      
            
        yt = YouTube(youtube_url)

        response = {}

        if descargar_subtitulos:
            if not formato_subtitulos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El formato de subtitulos no se especificó",
                )
            if formato_subtitulos not in formatos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El formato no es correcto",
                )                
            try:
                parsed_url = urlparse(youtube_url)
                query_parameters = parse_qs(parsed_url.query)
                video_id = query_parameters.get('v', [])[0]
                srt = YouTubeTranscriptApi.get_transcript(video_id, languages=['es'])

                output_filename = os.path.join(upload_folder_video, f"{safe_filename(yt.title)}.{formato_subtitulos}")

                with open(output_filename, "w", encoding='utf-8') as f:
                    if formato_subtitulos == "srt":
                        for i, entry in enumerate(srt, start=1):
                            f.write(f"{i}\n")
                            try:
                                f.write(f"{entry['start']} --> {entry['start'] + entry['duration']}\n")
                                f.write(f"{entry['text']}\n\n")
                            except KeyError as e:
                                response["message"] = f"Error al escribir entrada VTT: {e}"
                    elif formato_subtitulos == "txt":
                        for entry in srt:
                            try:
                                f.write(f"{entry['text']} ")
                            except KeyError as e:
                                response["message"] = f"Error al escribir entrada VTT: {e}"
                    elif formato_subtitulos == "vtt":
                        f.write("WEBVTT\n\n")
                        for entry in srt:
                            try:
                                f.write(f"{entry['start']:.3f} --> {entry['start'] + entry['duration']:.3f}\n")
                                f.write(f"{entry['text']}\n\n")
                            except KeyError as e:                     
                                response["message"] = f"Error al escribir entrada VTT: {e}"

                response["URL-Subtitulo"] = output_filename

            except Exception as e:
                response["message-error"] = f"Ocurrió un error {e}"

        if descargar_videos:
            if not calidad_video:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La calidad del video no se especificó",
                )
            if calidad_video not in calidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Calidad de video invalida",
                )
                
            video_stream = yt.streams.filter(res=calidad_video).first()
            
            if video_stream:
                carpeta_salida = upload_folder_video
                video_stream.download(carpeta_salida)
                response["message"] = "Video descargado correctamente"
                response["URL-Video"] = f"{carpeta_salida}/{safe_filename(yt.title)}.mp4"
        
        return response

    except VideoUnavailable as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El video no está disponible o no existe.")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
