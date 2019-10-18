"""
/***************************************************************************
 SeilaplanPlugin
                                 A QGIS plugin
 Seilkran-Layoutplaner
                              -------------------
        begin                : 2013
        copyright            : (C) 2015 by ETH Zürich
        email                : seilaplanplugin@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import numpy as np

import os
import math
import time
import textwrap

p = 21
nl = os.linesep


def getTimestamp(tStart):
    """Calculate duration of algorithm run"""
    tEnd = time.time()
    tDuration = tEnd - tStart
    # Format time
    tsFormated1 = time.strftime("%Y-%m-%d_%H'%M", time.localtime(tStart))
    tsFormated2 = time.strftime("%d.%m.%Y, %H:%M Uhr", time.localtime(tStart))
    mini = int(math.floor(tDuration/60))
    sek = int(tDuration-mini*60)
    if mini == 0:
        tdFormated = str(sek) + " s"
    else:
        tdFormated = str(mini) + " min " + str(sek) + " s"
    return [tdFormated, tsFormated1, tsFormated2]


def formatNum(numbr):
    """Format big numbers with thousand separator"""
    return f"{numbr:,.1f}".replace(',', "'")


def removeTxtElements(text, key):
    """Prepare Text for report by removing 'nan' values"""
    if type(text) is str:
        if key in text:
            return "-"
        else:
            return text
    elif type(text) is list:
        return [removeTxtElements(x, key) for x in text]
    elif type(text) is set:
        return {removeTxtElements(x, key) for x in text}
    else:
        return text


def generateReportText(confHandler, result, comment):
    """ Arrange texts and values for report generation.
    
    :type confHandler: configHandler.ConfigHandler
    """
    poles = confHandler.project.poles
    poleslist = poles.poles
    [pole_d, pole_z, pole_h, pole_dtop, pole_ztop] = poles.getAsArray()
    hmodell = confHandler.project.getDhmAsStr()
    kraft = result['force']

    # Values for survey work
    hDist = []
    sDist = []
    az_gon = poles.azimut * 1.11111
    for i in range(len(pole_d)-1):
        dist_h = pole_d[i+1] - pole_d[i]
        dist_z = pole_z[i + 1] - pole_z[i]
        hDist.append(dist_h)
        sDist.append((dist_h**2 + dist_z**2)**0.5)

    poleCount = len(pole_d)
    fieldCount = poleCount - 1
    sHeader = [i['name'] for i in poleslist[1:-1]]
    fHeader = [f"{i+1}. Feld" for i in range(poleCount)]

    # First section with duration, dhm and several comments
    str_time = [
        [],
        ["Zeitpunkt", f"{result['duration'][2]}, Berechnungsdauer: {result['duration'][0]}"],
        ["Höhenmodell", hmodell], []]
    if comment:
        commentWraped = textwrap.fill(comment, 150).split('\n')
        # First line
        str_time.append(['Bemerkung', commentWraped[0]])
        # Consecutive lines
        for line in commentWraped[1:]:
            str_time.append(['', line])
        str_time.append([])

    str_time.append(["Erklärungen und Diagramme zu den technischen Werten sind in der "
         "Dokumentation zu finden."])
    if True:
        str_time.append(["Markierung für fixe Stützen: ° = fixe Position, °* = fixe Position und Höhe"])
    
    # Section poles
    str_posi = [["", "Höhe", "X-Koordinate", "Y-Koordinate", "Z-Koordinate", "(M.ü.M)"]]
    for s in range(poleCount):
        pole = poles.poles[s]
        str_posi.append([
            f"{pole['name']}", f"{pole['h']:.1f} m",
            f"{formatNum(pole['coordx'])}",
            f"{formatNum(pole['coordy'])}",
            f"{formatNum(pole['z'])}"])

    # Section field survey
    str_abst = [[f"Azimut: {az_gon:.1f} gon"],
                ["", "Horizontaldistanz", "Schrägdistanz"]]
    for f in range(fieldCount):
        str_abst.append([f"von {sHeader[f]} zu {sHeader[f+1]}",
                         f"{hDist[f]:.1f} m", f"{sDist[f]:.1f} m"])

    # Section cable pull strength
    str_opti = [["optimaler Wertebeich",
                 f"{np.min(result['optSTA_arr']):.0f} - {np.max(result['optSTA_arr']):.0f} kN"],      # TODO: Was machen mit manuell definiertem OptSTA? Leo fragen
                ["gewählte Seilzugkraft bei der Anfangsstütze",
                 f"{kraft['Spannkraft'][0]:.0f} kN"]]

    # Section cable length
    str_laen = [[""]*2 + fHeader,
                ["Länge Leerseil bei Anfangszugkraft",
                 f"{kraft['LaengeSeil'][0]:.0f} m"] + [""]*fieldCount,
                ["Länge Leerseil bei 0 kN Seilzugkraft",
                 f"{kraft['LaengeSeil'][1]:.0f} m"] + [""]*fieldCount,
                ["Länge der Spannfelder"] + (",{:.0f} m"*fieldCount).format(
                    *tuple(kraft['LaengeSeil'][2])).split(',', fieldCount)]

    # Section cable slack
    str_durc = [["Abk.", ""] + fHeader,
                ["yLE", "Leerseil"] + ("{:.2f} m,"*fieldCount).format(
                    *tuple(kraft['Durchhang'][0])).rstrip(',').split(',', fieldCount),
                ["yLA", "Lastseil"] + ("{:.2f} m,"*fieldCount).format(
                    *tuple(kraft['Durchhang'][1])).rstrip(',').split(',', fieldCount)]

    str_seil1 = [
        ["Abk.", "am Leerseil"] + [""]*(poleCount+1),
        ["T0,A", "Seilzugkraft an der Anfangsstütze"] +
        [f"{kraft['Spannkraft'][0]:.0f} kN"] + [""]*poleCount,
        ["T0,E", "Seilzugkraft an der Endstütze"] +
        [f"{kraft['Spannkraft'][1]:.0f} kN"] + [""]*poleCount,
        [""]*3 + sHeader,
        ["T0", "Seilzugkraft des Leerseils an den Stützen", ""] +
        ("{:.0f} kN,"*poleCount).format(*tuple(
            np.round(kraft['Seilzugkraft'][0]))).rstrip(',').split(',', poleCount)]
    str_seil2 = [
        ["HS", "Leerseilverhältnis: Horizontalkomponente"] + fHeader,
        ["", "     der Seilzugkraft an den Stützen"] +
        ("{:.0f} kN,"*fieldCount).format(*tuple(
                kraft['Seilzugkraft'][1])).rstrip(',').split(',', fieldCount)]
    str_seil3 = [
        ["", "am Lastseil"] + [""]*fieldCount,
        ["", "Max. auftretende Seilzugkraft"],
        ["Tmax", "     am höchsten Punkt im Seilsystem",
         f"{kraft['MaxSeilzugkraft_L'][0]:.0f} kN"],
        ["Tmax,A", "     am Anfangsanker",
         f"{kraft['MaxSeilzugkraft_L'][1]:.0f} kN"],
        ["Tmax,E", "     am Endanker",
         f"{kraft['MaxSeilzugkraft_L'][2]:.0f} kN"]]
    str_seil4 = [
        ["", "am Lastseil mit Last in Feldmitte"] + fHeader,
        ["Tm", "Max. auftretende Seilzugkraft gemessen in Feldmitte"] +
            ("{:.0f} kN,"*fieldCount).format(*tuple(kraft['MaxSeilzugkraft'][0])
            ).rstrip(',').split(','),
        ["Hm", "     davon horizontale Komponente"] +
            ("{:.0f} kN,"*fieldCount).format(*tuple(kraft['MaxSeilzugkraft'][1])
            ).rstrip(',').split(','),
        ["Tm,max", "     gemessen am höchsten Punkt im Seilsystem"] +
            ("{:.0f} kN,"*fieldCount).format(*tuple(kraft['MaxSeilzugkraft'][2])
            ).rstrip(',').split(','),
        ]
    str_seil = [str_seil1, str_seil2, str_seil3, str_seil4]

    # Section cable forces
    str_stue1 = [
        ["", "an befahrbarer Stütze, Laufwagen auf Stütze"] + sHeader,
        ["F_Sa_BefRes", "Sattelkraft, resultierend"] +
            ("{:.0f} kN,"*poleCount).format(*tuple(
                kraft['Sattelkraft_Total'][0])).rstrip(',').split(','),
        ["F_Sa_BefV", "Sattelkraft, vertikale Komponente"] +
            ("{:.0f} kN,"*poleCount).format(*tuple(
                kraft['Sattelkraft_Total'][1])).rstrip(',').split(','),
        ["F_Sa_BefH", "Sattelkraft, horizontale Komponente"] +
            ("{:.0f} kN,"*poleCount).format(*tuple(
                kraft['Sattelkraft_Total'][2])).rstrip(',').split(','),
        ["FSR", "Sattelkraft (Anteil von Tragseil), resultierend"] +
            ("{:.0f} kN,"*poleCount).format(*tuple(
                kraft['Sattelkraft_ausSeil'][0])).rstrip(',').split(','),
        ["FSV", "Sattelkraft (Anteil von Tragseil), vertikale Komponente"] +
            ("{:.0f} kN,"*poleCount).format(*tuple(
                kraft['Sattelkraft_ausSeil'][1])).rstrip(',').split(','),
        ["FSH", "Sattelkraft (Anteil von Tragseil), horizontale Komponente"] +
            ("{:.0f} kN,"*poleCount).format(*tuple(
                kraft['Sattelkraft_ausSeil'][2])).rstrip(',').split(','),
        ["FU", "Einwirkung auf Stütze aus Last, Gewicht Zug- & Tragseil"] +
            ("{:.0f} kN,"*poleCount).format(*tuple(
                kraft['UebrigeKraft_befStuetze'])).rstrip(',').split(','),
        ]
    newHeader = [""]*(poleCount*2)
    a = 0
    for i in range(0, poleCount*2, 2):
        newHeader[i+1] = sHeader[a]
        a += 1
    str_stue2 = [
        ["", "an nicht befahrbarer Stütze,"] + newHeader,
        ["", "     Laufwagen unmittelbar links/rechts bei Stütze"] +
            ["links", "rechts"]*poleCount,
        ["TCS", "Seilzugkraft"] +
            ("{:.0f} kN,"*(poleCount*2)).format(*tuple(
                kraft['Seilzugkraft_beiStuetze'])).rstrip(',').split(','),
        ["F_Sa_NBefRes", "Sattelkraft, resultierend"] +
            ("{:.0f} kN,"*(poleCount*2)).format(*tuple(
                kraft['Sattelkraft_beiStuetze'][0])).rstrip(',').split(','),
        ["F_Sa_NBefV", "Sattelkraft, vertikale Komponente"] +
            ("{:.0f} kN,"*(poleCount*2)).format(*tuple(
                kraft['Sattelkraft_beiStuetze'][1])).rstrip(',').split(','),
        ["F_Sa_NBefH", "Sattelkraft, horizontale Komponente"] +
            ("{:.0f} kN,"*(poleCount*2)).format(*tuple(
                kraft['Sattelkraft_beiStuetze'][2])).rstrip(',').split(','),
    ]
    str_stue = [str_stue1, str_stue2]

    # Section cable angles
    str_wink = [
        ["", "am Leerseil"] + sHeader,
        ["alpha LA", "eingehender Winkel"] +
            ("{:.0f}°,"*poleCount).format(*tuple(
                kraft['Anlegewinkel_Leerseil'][0])).rstrip(',').split(','),
        ["alpha LE", "ausgehender Winkel"] +
            ("{:.0f}°,"*poleCount).format(*tuple(
                kraft['Anlegewinkel_Leerseil'][1])).rstrip(',').split(','),
        [""],
        ["", "am Lastseil"] + sHeader,
        ["alpha LA", "eingehender Winkel", ""] +
            ("{:.0f}°,"*fieldCount).format(*tuple(
                kraft['Anlegewinkel_Lastseil'][0][1:])).rstrip(',').split(','),
        ["alpha LE", "ausgehender Winkel"] +
            ("{:.0f}°,"*fieldCount).format(*tuple(
                kraft['Anlegewinkel_Lastseil'][1][:-1])).rstrip(',').split(',')
        ]

    # Section verification
    str_nach = [
        ["", ""] + sHeader,
        ["beta", "Leerseilknickwinkel"] +
            ("{:.0f}°,"*poleCount).format(*tuple(
                kraft['Leerseilknickwinkel'])).rstrip(',').split(','),
        ["", "Nachweis erfüllt"] +
            ("{},"*poleCount).format(*tuple(
                kraft['Nachweis'])).rstrip(',').split(',')
    ]
    
    orderedParams = confHandler.params.paramOrder
    # Parameter set name
    str_anna = [['Parameterset:', confHandler.params.currentSetName, '', ''],
                ['']*4]     # empty row
    lenParam = math.ceil(len(orderedParams) / 2)
    for i in range(lenParam):
        paramFirstRow = confHandler.params.params[orderedParams[i]]
        paramSecondRow = confHandler.params.params[orderedParams[i + lenParam]]
        firstColum = [paramFirstRow['label'],
                      f"{confHandler.params.getParameterAsStr(orderedParams[i])} "
                      f"{paramFirstRow['unit']}"]
        spacer = ['']
        secondColumn = [paramSecondRow['label'],
                        f"{confHandler.params.getParameterAsStr(orderedParams[i + lenParam])} "
                        f"{paramSecondRow['unit']}"]
        str_anna.append(firstColum + spacer + secondColumn)

    text = [str_time, str_posi, str_abst, str_opti, str_laen, str_durc,
            str_seil, str_stue, str_wink, str_nach, str_anna]
    str_report = removeTxtElements(text, "nan")

    return str_report


def generateReport(reportText, savePath, projname):
    """Generate PDF report with reprotlab"""
    from ..packages.reportlab.lib.pagesizes import A4, cm, landscape
    from ..packages.reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from ..packages.reportlab.graphics.shapes import colors

    width, height = landscape(A4)
    margin = 1.5*cm
    if os.path.exists(savePath):
        os.remove(savePath)
    doc1 = SimpleDocTemplate(savePath, encoding='utf8', topMargin=margin,
                             bottomMargin=margin, leftMargin=margin,
                             rightMargin=margin, pageBreakQuick=1,
                             pagesize=landscape(A4))
    elements = []

    [str_time, str_posi, str_abst, str_opti, str_laen,
     str_durc, [str_seil1, str_seil2, str_seil3, str_seil4],
     [str_stue1, str_stue2], str_wink, str_nach, str_anna] = reportText

    widthT, heightT = [width-2*margin, height-2*margin]
    wi_doc = [widthT]
    wi_clo = [2.7 * cm]
    wi_abk = [1.7*cm]
    he_row = [0.40 * cm]
    he_rowT = [0.45 * cm]
    len_pole = len(str_posi)-1
    len_field = len_pole - 1
    lPadd = 6
    fontSize = 8
    smallfontSize = 6
    
    # Title definition
    h_tite = [["Seilbahnprojekt        "+projname]]
    h_posi = [["Stützenpositionen"]]
    h_abst = [["Daten für Absteckung im Feld"]]
    h_opti = [["Vorspannung der Seilzugkraft"]]
    h_leng = [["Seillänge"]]
    h_durc = [["Durchhang"]]
    h_seil = [["Auftretende Kräfte am Seil"]]
    h_stue = [["Auftretende Kräfte an den Stützen"]]
    h_wink = [["Seilwinkel an den Stützen"]]
    h_nach = [["Nachweis, dass Tragseil nicht vom Sattel abhebt"]]
    h_anna = [["Annahmen"]]

    # Table styles
    font = 'Helvetica'
    fontBold = 'Helvetica-Bold'
    fontHeader = 'Helvetica-Oblique'

    title_style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                              ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                              ('FONT', (0, 0), (-1, -1), font, 8),
                              ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                              ])
    stdStyleA = [('LEFTPADDING', (0, 0), (0, -1), lPadd),  # Align everything left
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),  # after first column aling right
                ('FONT', (0, 0), (-1, -1), font, fontSize)]
    stdStyleB = [('LEFTPADDING', (0, 0), (0, -1), lPadd),
                 ('FONT', (1, 0), (-1, -1), font, fontSize),
                 ('ALIGN', (2, 0), (-1, -1), 'RIGHT')]

    t_tite1 = Table(h_tite, wi_doc, [0.8*cm])
    t_tite2 = Table(str_time, [2.6*cm, 15.2*cm], len(str_time) * he_row)
    t_tite1.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONT', (0, 0), (-1, -1), fontBold, 13),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.black),
        ]))
    t_tite2.setStyle(TableStyle([('FONT', (0, 0), (-1, -1), font, fontSize),
                                 ('LEFTPADDING', (0, 0), (0, -1), lPadd)]))

    t_posi1 = Table(h_posi, wi_doc, he_rowT)
    t_posi2 = Table(str_posi, [1.7*cm] + 5*[2.5*cm], len(str_posi) * he_row)
    t_posi1.setStyle(title_style)
    t_posi2.setStyle(TableStyle(stdStyleA + [
        ('ALIGN', (5, 0), (5, -0), 'LEFT'),
        ('FONT', (0, 0), (-2, 0), fontHeader, smallfontSize)]))

    t_abst1 = Table(h_abst, wi_doc, he_rowT)
    t_abst2 = Table(str_abst, [5*cm] + 2*wi_clo, len(str_abst) * he_row)
    t_abst1.setStyle(title_style)
    t_abst2.setStyle(TableStyle(stdStyleA + [
        ('FONT', (0, 1), (-1, 1), fontHeader, smallfontSize)]))

    t_opti1 = Table(h_opti, wi_doc, he_rowT)
    t_opti2 = Table(str_opti, [5*cm] + wi_clo, 2*he_row)
    t_opti1.setStyle(title_style)
    t_opti2.setStyle(TableStyle(stdStyleA))

    t_laen1 = Table(h_leng, wi_doc, he_rowT)
    t_laen2 = Table(str_laen, [5.8*cm] + [2*cm] + [1.5*cm]*len_field, 4*he_row)
    t_laen1.setStyle(title_style)
    t_laen2.setStyle(TableStyle(stdStyleA + [
        ('FONT', (2, 0), (-1, 0), fontHeader, smallfontSize)]))  # field headers

    t_durc1 = Table(h_durc, wi_doc, he_rowT)
    t_durc2 = Table(str_durc, wi_abk + [3*cm] + [1.7*cm]*len_field, 3*he_row)
    t_durc1.setStyle(title_style)
    t_durc2.setStyle(TableStyle(stdStyleB + [
        ('FONT', (2, 0), (-1, 0), fontHeader, smallfontSize),  # field headers
        ('FONT', (0, 0), (0, -1), font, smallfontSize)]))  # abbreviation in first column

    t_seil1 = Table(h_seil, wi_doc, he_rowT)
    t_seil2 = Table(str_seil1, wi_abk + [6*cm] + [1*cm] + [1.5*cm]*len_field, len(str_seil1)*he_row)
    t_seil3 = Table(str_seil2, wi_abk + [7.7*cm] + [1.5*cm]*len_pole, len(str_seil2)*he_row)
    t_seil4 = Table(str_seil3, wi_abk + [6*cm] + [1*cm], len(str_seil3)*he_row)
    t_seil5 = Table(str_seil4, wi_abk + [7.7*cm] + [1.5*cm]*len_field, len(str_seil4)*he_row)
    t_seil1.setStyle(title_style)
    t_seil2.setStyle(TableStyle(stdStyleB + [
        ('FONT', (0, 0), (-1, 0), fontHeader, fontSize),  # first row = subsection
        ('FONT', (3, 3), (-1, 3), fontHeader, smallfontSize),  # pole header
        ('FONT', (0, 0), (0, -1), font, smallfontSize),  # abbreviation in first column
        ('BOTTOMPADDING', (0, -1), (-1, -1), 0)]))
    t_seil3.setStyle(TableStyle(stdStyleB + [
        ('FONT', (2, 0), (-1, 0), fontHeader, smallfontSize),  # pole header
        ('FONT', (0, 0), (0, -1), font, smallfontSize),  # abbreviation in first column
        ('TOPPADDING', (0, 0), (-1, 0), 0)]))
    t_seil4.setStyle(TableStyle(stdStyleB + [
        ('FONT', (0, 0), (-1, 0), fontHeader, fontSize),  # first row = subsection
        ('FONT', (0, 0), (0, -1), font, smallfontSize)]))  # abbreviation in first column
    t_seil5.setStyle(TableStyle(stdStyleB + [
        ('FONT', (0, 0), (1, 0), fontHeader, fontSize),  # first row = subsection
        ('FONT', (2, 0), (-1, 0), fontHeader, smallfontSize),  # field header
        ('FONT', (0, 0), (0, -1), font, smallfontSize)]))  # abbreviation in first column

    t_stue1 = Table(h_stue, wi_doc, he_rowT)
    t_stue2 = Table(str_stue1, wi_abk + [6.8*cm] + [2.2*cm]*len_pole, len(str_stue1)*he_row)
    t_stue3 = Table(str_stue2, wi_abk + [6.8*cm] + [1.1*cm]*len_pole,len(str_stue2)*he_row)
    t_stue1.setStyle(title_style)
    t_stue2.setStyle(TableStyle(stdStyleB + [
        ('FONT', (2, 0), (-1, 0), fontHeader, smallfontSize),  # field header
        ('FONT', (1, 0), (1, 0), fontHeader, fontSize),  # subsection
        ('FONT', (0, 0), (0, -1), font, smallfontSize)]))  # abbreviation in first column
    stdStyleStue = stdStyleB + [
        ('FONT', (2, 0), (-1, 1), fontHeader, smallfontSize),   # field header
        ('FONT', (1, 0), (1, 1), fontHeader, fontSize),  # subsection
        ('FONT', (0, 0), (0, -1), font, smallfontSize),  # abbreviation in first column
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('ALIGN', (-2, 1), (-2, -1), 'CENTER')]
    for i in range(2, len_pole*2+2, 2):
        stdStyleStue += [
                         ('RIGHTPADDING', (i, 1), (i, -1), 1)]
    t_stue3.setStyle(TableStyle(stdStyleStue))

    t_wink1 = Table(h_wink, wi_doc, he_rowT)
    t_wink2 = Table(str_wink, wi_abk + [4*cm] + [1.7*cm]*len_field, 7*he_row)
    t_wink1.setStyle(title_style)
    t_wink2.setStyle(TableStyle(stdStyleB + [
        ('FONT', (1, 0), (1, 0), fontHeader, fontSize),  # heading empty cable
        ('FONT', (1, 4), (1, 4), fontHeader, fontSize),  # heading load cable
        ('FONT', (2, 0), (-1, 0), fontHeader, smallfontSize),  # field header
        ('FONT', (2, 4), (-1, 4), fontHeader, smallfontSize),  # field header
        ('FONT', (0, 0), (0, -1), font, smallfontSize)]))  # abbreviation in first column

    t_nach1 = Table(h_nach, wi_doc, he_rowT)
    t_nach2 = Table(str_nach, wi_abk + [4*cm] + [1.7*cm]*len_field, 3*he_row)
    t_nach1.setStyle(title_style)
    t_nach2.setStyle(TableStyle(stdStyleB + [
        ('FONT', (2, 0), (-1, 0), fontHeader, smallfontSize),  # field header
        ('FONT', (0, 0), (0, -1), font, smallfontSize)]))  # abbreviation in first column

    t_anna1 = Table(h_anna, wi_doc, he_rowT)
    t_anna2 = Table(str_anna, [5*cm, 3*cm, 1*cm, 5*cm, 3*cm], len(str_anna) * [0.35*cm])
    t_anna1.setStyle(title_style)
    t_anna2.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (0, -1), lPadd),
        ('ALIGN', (3, 0), (3, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('FONT', (0, 0), (-1, -1), font, fontSize)]))

    data = [ [Table([[t_tite1], [t_tite2]])], [Table([[t_posi1], [t_posi2]])],
             [Table([[t_abst1], [t_abst2]])],
             [Table([[t_opti1], [t_opti2]])], [Table([[t_laen1], [t_laen2]])],
             [Table([[t_durc1], [t_durc2]])], [Table([[t_seil1], [t_seil2],
             [t_seil3], [t_seil4], [t_seil5]])],
             [Table([[t_stue1], [t_stue2], [t_stue3]])],
             [Table([[t_wink1], [t_wink2]])],
             [Table([[t_nach1], [t_nach2]])], [Table([[t_anna1], [t_anna2]])]]

    elements.append(Table(data))
    doc1.build(elements)
    del elements


def createOutputFolder(folder, name):
    location = os.path.join(folder, name)
    i = 1
    while os.path.exists(location):
        if i == 1:
            location = "{}_{}".format(location, i)
        location = "{}_{}".format(location[:-2], i)
        i += 1
    os.makedirs(location)
    return location
