from django.shortcuts import render
from django.http import HttpResponse
from .forms import FileUploadForm
from django.conf import settings

import os
import csv

# read in the list of printers
in_f_path = os.path.join(".", "test_data", "b9_active_printers.csv")
printers_list = []
with open(in_f_path, mode="r") as in_f:
    for printer in csv.DictReader(in_f):
        printers_list.append(printer)

printers_by_model = dict()
for printer in printers_list:
    if not printers_by_model.get(printer["model_number"]):
        printers_by_model[printer["model_number"]] = [printer]
    else:
        printers_by_model[printer["model_number"]].append(printer)

B9_PRINTER_FILES_ROOT = b9_printer_dir = os.path.join(
    settings.MEDIA_ROOT, "b9_printer_files"
)


def index(request):
    context = {}
    return render(request, "base/index.html", context)


def printer_display(request):
    context = {
        "printers_550X": printers_by_model["Core 550X"],
        "printers_550XT": printers_by_model["Core 550XT"],
        "printers_530X": printers_by_model["Core 530X"],
    }
    return render(request, "printer_display/index.html", context)


def get_printers(request):
    printer_model = request.GET["printer_model"]
    context = {
        "printer_model": printer_model,
        "printers": printers_by_model[printer_model],
    }
    return render(request, "printer_display/partials/printers_list.html", context)


def b9_files(request):
    selected_printer, b9_printer_dir, selected_file_to_delete, method = "", "", "", ""
    if request.method in ["POST"]:
        method = request.POST["method"].strip()
        selected_printer = request.POST["selected_printer"].strip()
        if method == "delete_file":
            selected_file_to_delete = request.POST["selected_file"].strip()

    elif request.method == "GET":
        selected_printer = request.GET["selected_printer"].strip()
    if request.method in ["GET", "POST", "DELETE"]:
        b9_printer_dir = os.path.join(B9_PRINTER_FILES_ROOT, selected_printer)
        os.makedirs(b9_printer_dir, exist_ok=True)

    if request.method == "POST":
        if method == "upload_file":
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.cleaned_data["file"]
                # TODO Validation?

                file_path = os.path.join(b9_printer_dir, uploaded_file.name)
                with open(file_path, "wb+") as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                print(
                    f'Uploaded "{uploaded_file.name}" to "{selected_printer}" Successfully.'
                )

            else:
                print(form.errors)
        elif method == "delete_file":
            file_path = os.path.join(b9_printer_dir, selected_file_to_delete)

            print(f'From "{selected_printer}", deleting "{selected_file_to_delete}"')
            os.remove(file_path)

    if request.method in ["GET", "POST"]:
        files_in_dir = [
            {
                "file_name": file_name,
                "file_path": os.path.join(b9_printer_dir, file_name),
                "this_printer": selected_printer,
            }
            for file_name in os.listdir(b9_printer_dir)
        ]

        form = FileUploadForm()

        context = {
            "files": files_in_dir,
            "form": form,
            "selected_printer": selected_printer,
        }
        return render(
            request, "printer_display/partials/files-this-printer.html", context
        )
