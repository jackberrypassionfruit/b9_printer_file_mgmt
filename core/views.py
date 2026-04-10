from django.shortcuts import render
from .forms import FileUploadForm
from django.conf import settings
from django.http import HttpRequest

import os
import csv
import shutil

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

B9_PRINTER_FILES_ROOT = os.path.join(settings.MEDIA_ROOT, "b9_printer_files")

BANK_FILES_ROOT = os.path.join(settings.MEDIA_ROOT, "file_bank")


def _get_files_in_dir(b9_printer_dir):
    files_in_dir = []
    for file in sorted(os.scandir(b9_printer_dir), key=lambda f: f.name):
        if file.is_dir():
            try:
                file = next(os.scandir(file))
            except:
                file = None
        if file:
            files_in_dir.append(
                {
                    "file_name": file.name,
                    "file_path": file.path,
                }
            )
    return files_in_dir


def _shake_files(files_in_dir, b9_printer_dir):
    for i, file in enumerate(files_in_dir):
        sub_folder = str(i + 1).zfill(2)
        src_file = file["file_path"]
        dest_dir = os.path.join(b9_printer_dir, sub_folder)
        os.makedirs(dest_dir, exist_ok=True)
        try:
            shutil.move(src_file, dest_dir)
        except Exception as e:
            print(e)


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
    (
        selected_printer,
        b9_printer_dir,
        file_to_delete,
        file_path_to_delete,
        method,
    ) = (
        "",
        "",
        "",
        "",
        "",
    )
    if request.method in ["POST"]:
        method = request.POST["method"].strip()
        selected_printer = request.POST["selected_printer"].strip()
        if method == "delete_file":
            file_to_delete = request.POST["selected_file"].strip()
            # file_path_to_delete = request.POST["selected_file_path"].strip()

    elif request.method == "GET":
        # selected_printer = request.GET["selected_printer"].strip()
        selected_printer = request.headers.get("selected-printer")
    if request.method in ["GET", "POST", "DELETE"]:
        b9_printer_dir = os.path.join(B9_PRINTER_FILES_ROOT, selected_printer)
        os.makedirs(b9_printer_dir, exist_ok=True)

        # Shuffle all parts to the top of the filesystem
        # ie. for each file o the printer, add it to the folder of its index
        # If you are uploading a new file, first make sure that the folder of the highest index exists first
        files_in_dir = _get_files_in_dir(b9_printer_dir)

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
        elif method == "drag_file":
            # TODO this is also where B9 API firmware could be called
            banked_file_path = request.POST.get("file_path")
            shutil.copy(banked_file_path, b9_printer_dir)
        elif method == "delete_file":
            # because the HTML tag's data path might've changed during dragging,
            # just reference files_in_dir on matching filename
            file_path_to_delete = [
                file["file_path"]
                for file in files_in_dir
                if file["file_name"] == file_to_delete
            ][0]
            print(f'From "{selected_printer}", deleting "{file_to_delete}"')
            os.remove(file_path_to_delete)

    if request.method in ["GET", "POST"]:
        # do it again bc you just changed the files
        files_in_dir = _get_files_in_dir(b9_printer_dir)
        # make sure the priority queue stays incrementing from 1
        _shake_files(files_in_dir, b9_printer_dir)

        form = FileUploadForm()

        bank_files = [
            {"name": file.name, "path": file.path}
            for file in os.scandir(BANK_FILES_ROOT)
            if file.name not in [f["file_name"] for f in files_in_dir]
        ]

        context = {
            "files": files_in_dir,
            "form": form,
            "selected_printer": selected_printer,
            "bank_files": bank_files,
        }
        return render(
            request, "printer_display/partials/files-this-printer.html", context
        )
