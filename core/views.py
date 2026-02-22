from django.shortcuts import render

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


def index(request):
    context = {}
    return render(request, "base/index.html", context)


def printer_display(request):
    # testing

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


def get_files_this_printer(request):
    selected_printer = request.GET["selected_printer"]
