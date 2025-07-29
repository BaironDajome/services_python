import os
import subprocess
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .converter import convert_txt_to_laz


class ConvertTxtAPIView(APIView):
    def post(self, request, bahia):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        input_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

        with open(input_path, "wb+") as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

        output_path = input_path.replace(".txt", ".laz")

        if bahia == "tumaco":
            processed_path = input_path.replace(".txt", "_canal_tumaco_processed.laz")
            pipeline_path = os.path.join(
                settings.BASE_DIR, "convert", "pipeline_tumaco.json"
            )

        elif bahia == "buenaventura":
            processed_path = input_path.replace(
                ".txt", "_canal_buenaventura_processed.laz"
            )
            pipeline_path = os.path.join(
                settings.BASE_DIR, "convert", "pipeline_buenaventura.json"
            )

        else:
            return Response(
                {"error": "Bahía no válida. Usa 'tumaco' o 'buenaventura'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            convert_txt_to_laz(input_path, output_path)

            if os.path.exists(pipeline_path):
                subprocess.run(
                    [
                        "pdal",
                        "pipeline",
                        pipeline_path,
                        "--readers.las.filename=" + output_path,
                        "--writers.las.filename=" + processed_path,
                    ],
                    check=True,
                )
                final_path = processed_path
            else:
                final_path = output_path

            if os.path.exists(final_path):
                response = FileResponse(
                    open(final_path, "rb"), content_type="application/octet-stream"
                )
                response["Content-Disposition"] = (
                    f'attachment; filename="{os.path.basename(final_path)}"'
                )
                return response
            else:
                return Response(
                    {"error": "Archivo procesado no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except subprocess.CalledProcessError as e:
            return Response(
                {"error": "Error al ejecutar PDAL", "detalle": e.stderr},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
            # No eliminamos final_path aquí porque está siendo enviado
