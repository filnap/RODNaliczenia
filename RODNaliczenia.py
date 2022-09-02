import os
import fdb
import time
import configparser
import xml.etree.ElementTree as ET
from datetime import datetime

print("Generator raportu opłat i nadpłat działkowców ROD. Wersja 3.0")
print("Copyright (C) 2021 Filip Napierała i Marianna Humska")
print("Data kompilacji 05.07.2022r.")
print("--------------------------------------------------------------------------------------------------------")
print("Niniejszy program jest wolnym oprogramowaniem - możesz go rozpowszechniać dalej i/lub modyfikować ")
print("na warunkach Powszechnej Licencji Publicznej GNU")
print("wydanej przez Fundację Wolnego Oprogramowania, według wersji 3 tej Licencji lub dowolnej z późniejszych wersji.")
print("Niniejszy program rozpowszechniany jest z nadzieją, iż będzie on użyteczny - jednak BEZ ŻADNEJ GWARANCJI,")
print("nawet domyślnej gwarancji PRZYDATNOŚCI HANDLOWEJ,")
print("albo PRZYDATNOŚCI DO OKREŚLONYCH ZASTOSOWAŃ. Bliższe informacje na ten temat można uzyskać z")
print("Powszechnej Licencji Publicznej GNU.")
print("Powszechna Licencja Publiczna GNU powinna zostać ci dostarczona razem z tym programem")
print("--------------------------------------------------------------------------------------------------------")
print("Program powinien być uruchamiany na serwerze")
print("Proszę sprawdzić plik config.txt pod kątem zgodności danych domyślnych z tymi na Państwa Ogrodzie")
print("Potencjalne aktualizacje programu będą dostępne pod adresem: www.github.com/filnap/RODNaliczenia")

config = "config.txt"
parser = configparser.ConfigParser()
parser.read('config.txt')

filepath = parser['BASIC']['filepath']
database = parser['BASIC']['database']
user = parser['BASIC']['user']
password = parser['BASIC']['password']
debug = parser['BASIC']['debug']
IDinne = parser['BASIC']['idinne']  # ID of accural to which all unknown accurals will be added
debug_mode = int(debug)
xml_doc = ET.Element('root')

print("Zapis do pliku '%s'." % filepath)
try:
    os.remove(filepath)
    print("Utworzono nowy plik w miejsce poprzedniego.")
except:
    print("Brak pliku, tworzę nowy.")

con = fdb.connect(database=database, user=user, password=password, charset='utf8')
cur = con.cursor()
cur.execute("SELECT DATA FROM \"@WYCIAGI_WYCIAG\" ORDER BY IDWYCIAG DESC ")
data_wyciagu = cur.fetchall()[0][0]

print("Najnowszy wyciąg z dnia: " + str(data_wyciagu))

now = datetime.now()
xml_doc = ET.Element('dzialki', data_teraz=str(now), data_wyciagu=str(data_wyciagu))

cur.execute("SELECT NAZWAOPLATY FROM \"@PZD_SLOOPLATY\" WHERE IDSLOOPLATY='%s' " % IDinne)
IDinneN = cur.fetchall()
print("Wszystkie dane wpisane prawidłowo")
print("Naliczenia które będą miały ID \"NONE\" zostaną dodane do ID nr: " + str(IDinne) + " (" + str(IDinneN[0][0]) + ")")
cur.execute("SELECT NUMERDZIALKI FROM \"@PZD_DZIALKI\" ")
listadzialek = cur.fetchall()
# Creating list in file
L = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
print("Długość listy (maksymalna liczba ID naliczeń) to: " + str(len(L) - 3) + " (Pierwszy indeks to zero)")
if debug_mode == 1:
    print("TRYB DEBUGOWANIA AKTYWNY")
potwierdzenie = input("Liczba wszystkich działek to:" + str(len(listadzialek)) + " Prawidłowo? [T/n]")
if potwierdzenie == "T" or potwierdzenie == "t":

    # Main loop
    for h in range(len(listadzialek)):
        L = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        nrdz = listadzialek[h][0]
        print("Obsługuję działkę nr: " + nrdz)

        # getting data about owner to put in XML file
        dzialka = ET.SubElement(xml_doc, 'dzialka', nrdz=str(nrdz))

        cur.execute("SELECT IDDZIALKI FROM \"@PZD_DZIALKI\" WHERE NUMERDZIALKI='%s' " % nrdz)
        iddzialkilist = cur.fetchall()
        iddzialki = iddzialkilist[0][0]
        if debug_mode == 1:
            print("id dzialki:")
            print(iddzialki)

        # Area
        L[0] = nrdz
        cur.execute("SELECT POWIERZCHNIA FROM \"@PZD_DZIALKI\" WHERE IDDZIALKI='%s'" % iddzialki)
        powierzchnia = cur.fetchall()[0][0] * 10000
        ET.SubElement(dzialka, 'ParametryDzialki', Powierzchnia=str(powierzchnia))

        # Electric energy meter
        print("IDdzialki")
        print(iddzialki)
        try:
            cur.execute("SELECT IDLICZNIK FROM \"@PZD_RELLICZNIKDZIALKI\" WHERE IDDZIALKI='%s'" % iddzialki)
            idlicznik = cur.fetchall()[0][0]

            cur.execute("SELECT STANLICZNIKA, DATAODCZYTU FROM \"@PZD_LICZNIKODCZYT\" WHERE IDLICZNIK='%s'" % idlicznik)
            odczyty_licznika = cur.fetchall()
            #print(odczyty_licznika)
            for l in range(len(odczyty_licznika)):
                #print("l")
                #print(l)
                stan_licznika = odczyty_licznika[l][0]
                #print(stan_licznika)
                data_odczytu_EE = odczyty_licznika[l][1]
                #print(data_odczytu_EE)
                ET.SubElement(dzialka, 'Licznik', StanLicznika=str(stan_licznika), DataOdczytu=str(data_odczytu_EE))
        except:
            print("Brak kolejnych odczytów lub licznika")
        # list all ID of accurals for selected plot
        cur.execute("SELECT IDNALICZENIA FROM \"@PZD_NALICZENIA\" WHERE IDDZIALKI='%s'" % iddzialki)
        idnaliczenia = cur.fetchall()

        kwotanaliczen = 0

        i = 0
        j = 0
        KwotaOplat = 0

        for i in range(len(idnaliczenia)):
            # select one accural
            jednoidnal = idnaliczenia[i][0]

            # checking accrual category
            cur.execute("SELECT IDSLOOPLATY FROM \"@PZD_NALICZENIAPOZ\" WHERE IDNALICZENIA='%s'" % jednoidnal)
            idsioplaty = cur.fetchall()

            # left to pay check
            cur.execute("SELECT IDZOBOWIAZANIAKONTR FROM \"@PZD_NALICZENIAPOZ\" WHERE IDNALICZENIA='%s'" % jednoidnal)
            IDZOBOWIAZANIAKONTR = cur.fetchall()

            # select one accural and check what is left to pay in POZOSTALA_ZALEGLOSC column
            for a in range(len(IDZOBOWIAZANIAKONTR)):
                idzobdrug = IDZOBOWIAZANIAKONTR[a][0]

                if debug_mode == 1:
                    print("idzobowikontr")
                    print(idzobdrug)

                cur.execute("SELECT POZOSTALA_ZALEGLOSC FROM \"@ZAPL_ZOBOWIAZANIAKONTR\" WHERE IDZOBOWIAZANIAKONTR='%s'" % (idzobdrug))
                pozostalo = cur.fetchall()

                # sum left to pay until there is nothing more
                for l in range(len(pozostalo)):
                    pozostalodwa = pozostalo[l][0]

                    if pozostalodwa != 0:
                        indekss = idsioplaty[a][0]

                        # add ID none to selected ID
                        if str(indekss) == "None":
                            indekss = IDinne

                        # prepair to write it in list (one line in txt file), sum up in list L. "indekss" is column number in created list.

                        cur.execute("SELECT NAZWAOPLATY FROM \"@PZD_SLOOPLATY\" WHERE IDSLOOPLATY='%s'" % (indekss))
                        nazwaoplaty = cur.fetchall()[0][0]

                        ET.SubElement(dzialka, 'NaliczeniePozostalo', pozostalodwa=str(pozostalodwa), nazwaoplaty=str(nazwaoplaty))

                        opnalist = L[int(indekss)]
                        if debug_mode == 1:
                            print("indekss: " + str(indekss))
                            print("opnalist: " + str(opnalist))
                            print("pozostalodwa: " + str(pozostalodwa))
                        L[int(indekss)] = opnalist + pozostalodwa
                    l = l + 1
                a = a + 1

                # --------------------------------------------------------------------------------------------------
            # old section of code. Only generates sum of accurals
            cur.execute("SELECT KWOTA FROM \"@PZD_NALICZENIAPOZ\" WHERE IDNALICZENIA='%s'" % jednoidnal)
            kwotalista = cur.fetchall()

            for j in range(len(kwotalista)):
                kwota = kwotalista[j][0]

                kwotanaliczen = kwotanaliczen + kwota
                j = j + 1

            i = i + 1

            # Payment and email section
        # Finding ID for owners
        cur.execute("SELECT IDSIKONTRWLA FROM \"@PZD_RELDZIALKISIKONTR\" WHERE IDDZIALKI='%s' ORDER BY 'DATAOD' " % iddzialki)
        idsikontrwlarawWLAS = cur.fetchall()
        # Getting owner's e-mail adress
        idaktualnego = idsikontrwlarawWLAS[len(idsikontrwlarawWLAS) - 1][0]
        if debug_mode == 1:
            print("IDsikontrwlaRAWWLAS")
            print(idsikontrwlarawWLAS)
            print("IDaktualnego")
            print(idaktualnego)

        # email
        cur.execute("SELECT NAZWAKONTR FROM SIKONTR WHERE IDSIKONTR='%s'" % idaktualnego)
        nazwakontr = cur.fetchall()[0][0]
        cur.execute("SELECT TELEFON FROM SIKONTR WHERE IDSIKONTR='%s'" % idaktualnego)
        telefon = cur.fetchall()[0][0]
        if telefon == None:
            telefon = "N/D"
        cur.execute("SELECT EMAIL FROM SIKONTR WHERE IDSIKONTR='%s'" % idaktualnego)
        email = cur.fetchall()[0][0]
        if email == None:
            email = "N/D"

        ET.SubElement(dzialka, 'DaneDzialkowiec1', nazwakontr=str(nazwakontr), telefon=str(telefon), email=str(email))
        if debug_mode == 1:
            print("email:")
            print(email)

        # Finding ID for co-owners
        cur.execute("SELECT IDSIKONTRMALZ FROM \"@PZD_RELDZIALKISIKONTR\" WHERE IDSIKONTRWLA='%s'" % idaktualnego)
        idaktualnegoMALZ = cur.fetchall()[0][0]

        print(idaktualnegoMALZ)
        if idaktualnegoMALZ != None:
            cur.execute("SELECT NAZWAKONTR FROM SIKONTR WHERE IDSIKONTR='%s'" % idaktualnegoMALZ)
            nazwakontr = cur.fetchall()[0][0]
            cur.execute("SELECT TELEFON FROM SIKONTR WHERE IDSIKONTR='%s'" % idaktualnegoMALZ)
            telefon = cur.fetchall()[0][0]
            if telefon == None:
                telefon = "N/D"
            cur.execute("SELECT EMAIL FROM SIKONTR WHERE IDSIKONTR='%s'" % idaktualnegoMALZ)
            email = cur.fetchall()[0][0]
            if email == None:
                email = "N/D"
        else:
            print("Brak współmałżonka")
            nazwakontr = "N/D"
            telefon = "N/D"
            email = "N/D"

        ET.SubElement(dzialka, 'DaneDzialkowiec2', nazwakontr=nazwakontr, telefon=telefon, email=email)




        # Joining owners and co-owners ID lists together
        cur.execute("SELECT IDSIKONTRMALZ FROM \"@PZD_RELDZIALKISIKONTR\" WHERE IDDZIALKI='%s'" % iddzialki)
        idsikontrwlarawMALZ = cur.fetchall()
        idsikontrwlarawWLAS.extend(idsikontrwlarawMALZ)
        idsikontrwlaraw = idsikontrwlarawWLAS

        # Try to remove duplicates
        idsikontrwla = list(dict.fromkeys(idsikontrwlaraw))
        if debug_mode == 1:
            print("idsikontrwlaraw")
            print(idsikontrwlaraw)
            print("idsikontrwla")
            print(idsikontrwla)

        for l in range(len(idsikontrwla)):
            idsikontrwlaDwa = idsikontrwla[l][0]
            l = l + 1

            if idsikontrwlaDwa is not None:
                if debug_mode == 1:
                    print("ID kontrahenta: " + str(idsikontrwlaDwa))

                cur.execute("SELECT INDEKSKONTR FROM \"SIKONTR\" WHERE IDSIKONTR='%s'" % idsikontrwlaDwa)
                indekskontr = cur.fetchall()
                indekskontr = indekskontr[0][0]

                if debug_mode == 1:
                    print("Indeks kontrahenta: ")
                    print(indekskontr)

                # KP and KW
                cur.execute("SELECT KWOTA FROM \"DOKUMENTYKASOWE\" WHERE INDEKSKONTR ='%s'" % indekskontr)
                ZbiorczeOplaty = cur.fetchall()
                # print(ZbiorczeOplaty)

                k = 0
                for k in range(len(ZbiorczeOplaty)):
                    KwotaOplatyJeden = ZbiorczeOplaty[k][0]
                    KwotaOplat = KwotaOplat + KwotaOplatyJeden
                    k = k + 1
                # print("Kwota opłat: " + str(KwotaOplat))

                # Bank statements
                cur.execute("SELECT KWOTA FROM \"@WYCIAGI_WYC_POZ\" WHERE INDEKSKONTR ='%s'" % indekskontr)
                Wyciagi = cur.fetchall()

                m = 0
                for m in range(len(Wyciagi)):
                    KwotaOplatyJeden = Wyciagi[m][0]
                    # print("Kwota z wyciągu:" + str(KwotaOplatyJeden))
                    KwotaOplat = KwotaOplat + KwotaOplatyJeden
                    m = m + 1

        Saldo = kwotanaliczen - KwotaOplat
        print("Saldo:" + str(Saldo))
        L[41] = kwotanaliczen
        L[42] = KwotaOplat
        L[43] = Saldo
        if email != None:
            L[44] = email

        f = open(filepath, "a")
        f.write("\n")
        for g in range(len(L)):
            f.write(str(L[g]))
            f.write(";")
            g = g + 1
        f.close()
        h = h + 1
        print("Wiersz zapisano")


    # generating XML file
    # https://stackoverflow.com/questions/749796/pretty-printing-xml-in-python/38573964#38573964
    def prettify(element, indent='  '):
        queue = [(0, element)]  # (level, element)
        while queue:
            level, element = queue.pop(0)
            children = [(level + 1, child) for child in list(element)]
            if children:
                element.text = '\n' + indent * (level + 1)  # for child open
            if queue:
                element.tail = '\n' + indent * queue[0][0]  # for sibling open
            else:
                element.tail = '\n' + indent * (level - 1)  # for parent close
            queue[0:0] = children  # prepend so children come before siblings


    prettify(xml_doc)

    tree = ET.ElementTree(xml_doc)
    tree.write('sample.xml', encoding='UTF-8', xml_declaration=True)

    print("Program zakończył pracę sukcesem. Wyłączam za 3 sekundy")
    time.sleep(3)
else:
    print("Nie wpisano 'T'. Program zakończony przez użytkownika. Wyłączam za 3 sekundy")
    time.sleep(3)
con.close()
