# -*- coding: utf-8 -*-

import time
import os
import sys
import numpy as np
from PyQt4.QtCore import SIGNAL
# Pfad zu zusätzliche Libraries ergänzen
packagesPath = os.path.join(os.path.dirname(
                            os.path.dirname(__file__)), 'packages')
sys.path.append(packagesPath)


from geoExtract import generateDhm, calcProfile, stuePos, \
    calcAnker, updateAnker, markFixStue
from mainOpti import optimization
from cablelineFinal import preciseCable
from outputReport import vectorData


def checkInputParams(IS):
    # Ankerpunkten den Anfangs-/Endstützen anpassen
    if IS['HM_Anfang'][0] < 1:
        IS['d_Anker_A'][0] = 0.0
    if IS['HM_Ende_max'][0] < 1:
        IS['d_Anker_E'][0] = 0.0

    # Seilzugkräfte müssen ganzzahlig sein, aber in float-Form
    IS['zul_SK'][0] = round(IS['zul_SK'][0], 0)
    IS['min_SK'][0] = round(IS['min_SK'][0], 0)
    return IS


def main(progress, IS, projInfo):
    # import pydevd
    # pydevd.settrace('localhost', port=53100,
    #                  stdoutToServer=True, stderrToServer=True)

    IS = checkInputParams(IS)
    # STARTE BERECHNUNGEN
    # -------------------
    # resultStatus:
        #   1 = Berechnungen erfolgreich abgeschlossen
        #   2 = Berechnungen erfolgreich, jedoch hebt Seil von Stützen ab
        #   3 = Berechnungen teilweise erfolgreich, Seil spannt nicht ganze Länge
        #   4 = Seilverlauf konnte überhaupt nicht berechnet werden
    resultStatus = [1]
    t_start = time.time()
    # Abtastrate des Längenprofils
    # wird verwendet um Abstand Lastwegkurve - Terrain genau zu bestimmen
    DeltaH = 1      # DEFAULT 1m Genauigkeit, nicht änderbar!
    # Mindestdistanz zwischen Masten
    DeltaL = IS["L_Delta"][0]       # int
    coeff = DeltaL/DeltaH
    inputPoints = projInfo['Anfangspunkt'][:]
    inputPoints += projInfo['Endpunkt'][:]

    # Rasterdaten laden
    rasterdata = generateDhm(projInfo['Hoehenmodell'], inputPoints)
    if not progress.running:
            return False
    # Höhenprofil erstellen
    gp_old, zi_disp, diIdx = calcProfile(inputPoints, rasterdata, IS, DeltaH, coeff)
    if not progress.running:
            return False
    # Mögliche Stützenpositionen finden
    gp, StuetzenPos, peakLoc, diIdx = stuePos(IS, gp_old)
    possStue = gp['di_s'][StuetzenPos==1]

    # IS['HM_fix'] =
    IS['Ank'] = calcAnker(IS, inputPoints, rasterdata, gp)

    #Optimierungsprozedur
    out = optimization(IS, gp, StuetzenPos, progress)
    if not out:
        return False
    progress.emit(SIGNAL("text(PyQt_PyObject)"), u"Berechnung der optimale "
                                                 u"Seillinie...")
    [HM, HMidx, optValue, optSTA, optiLen] = out
    stuetzIdx = np.int32(diIdx[HMidx])
    IS['Ank'] = updateAnker(IS['Ank'], HM, stuetzIdx)
    IS['A_SK'][0] = optSTA[0]

    # Überprüfen ob Seil die gesamte Länge überspannt
    if int(HMidx[-1])+1 != gp['zi_s'].size:
        gp['di_s'] = gp['di_s'][:HMidx[-1]+1]
        gp['zi_s'] = gp['zi_s'][:HMidx[-1]+1]
        # Nicht alle Stützen konnten berechnet werden
        resultStatus.append(3)
        if HMidx == [0]:
            # Berechnungen nicht erfolgreich, keine einzige Stütze konnte
            #   berechnet werden
            resultStatus.append(4)
            return None, max(resultStatus)

    # Informationen für die Darstellung der fixen Stützen
    IS['HM_fix_marker'] = markFixStue(stuetzIdx, IS)

    # Präzise Seilfelddaten
    seil, kraft, seil_possible = preciseCable(gp['zi_s'], gp['di_s'], HM, HMidx, IS)
    if not seil_possible:       # Falls Seil von Stütze abhebt
        resultStatus.append(2)

    progress.emit(SIGNAL("value(PyQt_PyObject)"), optiLen*1.005)

    # Transformiere berechnete Daten in richtiges Koordinatensystem)
    [disp_data, seilDaten, HM] = vectorData(gp['xi'], gp['yi'], gp['di_n'],
                                        zi_disp, seil, stuetzIdx, HM, possStue)

    # IS.pop('Ank', None)
    return [t_start, disp_data, seilDaten, gp, HM, IS, kraft,
            optSTA, optiLen], max(resultStatus)
    # except:
    #     sys.exit()

