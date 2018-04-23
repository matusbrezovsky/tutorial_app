# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import get_site_path, today
import csv
import json
import os
import uuid

__version__ = '0.0.1'

@frappe.whitelist()
def print_invoices(list):

    list = json.loads(list)

    inv = []
    for invoice in list:
        inv.append(frappe.get_doc('Sales Invoice', invoice['name']))

    status, export = export_txt(inv)

    if status != 0:
        return

    curr_date = today()
    fname = "export_" + curr_date + "_" + str(uuid.uuid4()) + ".txt"
    save_path = get_site_path() + '/private/files'
    file_name = os.path.join(save_path, fname)

    with open(file_name, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(export)

    export_file = frappe.new_doc("File")
    export_file.file_name = fname
    export_file.attached_to_doctype = "Sales Invoice"

    export_file.file_url = "/private/files/" + fname
    export_file.is_folder = False

    export_file.folder = "Home"
    export_file.is_private = 1

    export_file.save()

    return export_file.name

@frappe.whitelist()
def export_txt(invoices):
    tab = '\t'
    export = []

    for invoice in invoices:
        # *******************************************************************R00

        R00_A = "R00"
        R00_B = "T01"
        R00_C = ""

        # R00 nepovinne
        R00_D = str(invoice.company)                        # nazov firmy
        R00_E = "87654321"                                  # ICO

        company_address = frappe.get_doc("Address", invoice.company_address)
        R00_F = str(company_address.address_line1)          # ulica cislo
        R00_G = str(company_address.pincode)                # PSC
        R00_H = str(company_address.city)                   # mesto

        export.append([R00_A + tab +
                       R00_B + tab +
                       R00_C + tab +
                       R00_D + tab +
                       R00_E + tab +
                       R00_F + tab +
                       R00_G + tab +
                       R00_H
                       ])
        # *******************************************************************R01

        R01_A = "R01"
        R01_B = invoice.name                                # cislo faktury
        R01_C = invoice.customer                            # meno partnera
        R01_D = "12345678"                                  # ICO
        R01_E = invoice.posting_date.strftime('%d.%m.%Y')   # datum vystavenia / datum prijatia
        R01_F = invoice.due_date.strftime('%d.%m.%Y')       # datum splatnosti
        R01_G = "01.01.2019"                                # datum uskutocnenia zdanitelneho plnenia

        sadzba_DPH_0 = 0                                    # DPH 0%
        sadzba_DPH_N = 10                                   # DPH 10%
        sadzba_DPH_V = 20                                   # DPH 20%
        suma_DPH_N = 0
        suma_DPH_V = 0

        tax_dict = json.loads(invoice.taxes[0].item_wise_tax_detail)
        for key, value in tax_dict.items():
            if value[0] not in [sadzba_DPH_0, sadzba_DPH_N, sadzba_DPH_V]:
                frappe.msgprint("Export nebol úspešný. Sadzba DPH nie je správna: " + invoice.name + ", " + key)
                return -1, []
            if value[0] == sadzba_DPH_N:
                suma_DPH_N += value[1]
            if value[0] == sadzba_DPH_V:
                suma_DPH_V += value[1]

        zaklad_DPH_N = (suma_DPH_N / sadzba_DPH_N) * 100
        zaklad_DPH_V = (suma_DPH_V / sadzba_DPH_V) * 100
        R01_H = str(abs(zaklad_DPH_N))                                          # zaklad DPH nizsi; standardne 0
        R01_I = str(abs(zaklad_DPH_V))                                          # zaklad DPH vyssi
        R01_J = str(abs(invoice.base_total - zaklad_DPH_N - zaklad_DPH_V))      # zaklad DPH nulovy
        R01_K = "0"                                                             # zaklad DPH neobsahuje
        R01_L = str(sadzba_DPH_N)                                               # sadzba DPH nizsia
        R01_M = str(sadzba_DPH_V)                                               # sadzba DPH vyssia
        R01_N = str(abs(suma_DPH_N))                                            # suma DPH nizsia; standardne 0
        R01_O = str(abs(suma_DPH_V))                                            # suma DPH vyssia
        R01_P = str(abs(invoice.rounding_adjustment))                           # halierove vyrovnanie
        R01_Q = str(abs(invoice.grand_total))                                   # suma spolu zahranicna mena

        R01_R = "0"
        R01_S = "OF"
        R01_T = "OF"

        # dobropis
        if invoice.is_return == 1:
            R01_R = "4"
            R01_S = "OD"
            R01_T = "OD"

        # R01 nepovinne
        customer_address = frappe.get_doc("Address", invoice.customer_address)

        if company_address.country == customer_address.country:
            R01_S = "z" + R01_S
            R01_T = "z" + R01_T

        R01_U = R01_V = R01_W = R01_X = ""
        R01_Y = str(customer_address.address_line1)
        R01_Z = str(customer_address.pincode)
        R01_AA = str(customer_address.city)
        R01_AB = R01_AC = R01_AD = R01_AE = R01_AF = R01_AG = R01_AH = R01_AI = R01_AJ = R01_AK = R01_AL = R01_AM = ""
        R01_AN = str(frappe.get_doc("Currency", invoice.currency).name)
        R01_AO = R01_AP = ""
        R01_AQ = str(abs(invoice.grand_total))

        export.append([R01_A + tab +
                       R01_B + tab +
                       R01_C + tab +
                       R01_D + tab +
                       R01_E + tab +
                       R01_F + tab +
                       R01_G + tab +
                       R01_H + tab +
                       R01_I + tab +
                       R01_J + tab +
                       R01_K + tab +
                       R01_L + tab +
                       R01_M + tab +
                       R01_N + tab +
                       R01_O + tab +
                       R01_P + tab +
                       R01_Q + tab +
                       R01_R + tab +
                       R01_S + tab +
                       R01_T + tab +
                       R01_U + tab +
                       R01_V + tab +
                       R01_W + tab +
                       R01_X + tab +
                       R01_Y + tab +
                       R01_Z + tab +
                       R01_AA + tab +
                       R01_AB + tab +
                       R01_AC + tab +
                       R01_AD + tab +
                       R01_AE + tab +
                       R01_AF + tab +
                       R01_AG + tab +
                       R01_AH + tab +
                       R01_AI + tab +
                       R01_AJ + tab +
                       R01_AK + tab +
                       R01_AL + tab +
                       R01_AM + tab +
                       R01_AN + tab +
                       R01_AO + tab +
                       R01_AP + tab +
                       R01_AQ
                       ])

        # *******************************************************************R02
        for item in invoice.items:
            R02_A = "R02"
            R02_B = item.description                    # nazov polozky
            R02_C = str(abs(item.qty))                  # mnozstvo
            R02_D = str(item.uom)                       # jednotka
            R02_E = str(abs(item.rate))                 # jednotkova cena bez DPH

            export.append([R02_A + tab + R02_B + tab + R02_C + tab + R02_D + tab + R02_E])

    with open("export_omega.txt", 'w') as file:
        writer = csv.writer(file)
        writer.writerows(export)

    return 0, export