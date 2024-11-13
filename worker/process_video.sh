#!/bin/bash
# Script para procesar un video con un logo, recortarlo y ajustar la relación de aspecto.

# $1 = ruta del video original
# $2 = ruta del logo
# $3 = directorio de salida

# Crear el directorio de salida si no existe
# mkdir -p "$3"

# Crear un archivo temporal para la concatenación
# echo "file '$2'" > concat_list.txt
# echo "file '$1'" >> concat_list.txt
# echo "file '$2'" >> concat_list.txt

# Concatenar el logo, el video y nuevamente el logo
# ffmpeg -f concat -safe 0 -i concat_list.txt -c copy "$3/temp_concat.mp4"

# Recortar el video concatenado a los primeros 20 segundos
# ffmpeg -ss 0 -t 20 -i "$3/temp_concat.mp4" -c copy "$3/temp_trimmed.mp4"

# Ajustar la relación de aspecto a 16:9
# ffmpeg -i "$3/temp_trimmed.mp4" -vf "scale=iw:ih,setsar=1,pad=w=ceil(iw/2)*2:h=ceil(ih/2)*2,scale=1280:720" -c:a copy "$3/processed_video.mp4"

# Limpiar archivos temporales
# rm "$3/temp_concat.mp4"
# rm "$3/temp_trimmed.mp4"
# rm concat_list.txt

