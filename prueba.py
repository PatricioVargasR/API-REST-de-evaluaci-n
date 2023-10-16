import os
from urllib.parse import urlparse, parse_qs
import re
from fastapi import FastAPI, status, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from pytube.helpers import safe_filename
from pytube.exceptions import VideoUnavailable

app = FastAPI()

# Carpeta donde se guardarán los archivos
upload_folder = "static/images"

# Carpeta donde se guardarán los videos
upload_folder_video = "static/videos"

# Permitimos ver la carpeta donde se sube la imagen
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        yt = YouTube(youtube_url)

        response = {}
        formatos = ["txt", "vtt", "str"]
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
