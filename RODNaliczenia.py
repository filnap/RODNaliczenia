import fdb
import time
import configparser

print("Generator raportu opłat i nadpłat działkowców ROD. Wersja 2.6")
print("Copyright (C) 2021 Filip Napierała i Marianna Humska")
print("Data kompilacji 08.04.2021")
print("--------------------------------------------------------------------------------------------------------")
print("Niniejszy program jest wolnym oprogramowaniem - możesz go rozpowszechniać dalej i/lub modyfikować na warunkach Powszechnej Licencji Publicznej GNU")
print("wydanej przez Fundację Wolnego Oprogramowania, według wersji 3 tej Licencji lub dowolnej z późniejszych wersji.")
print("Niniejszy program rozpowszechniany jest z nadzieją, iż będzie on użyteczny - jednak BEZ ŻADNEJ GWARANCJI, nawet domyślnej gwarancji PRZYDATNOŚCI HANDLOWEJ,")
print("albo PRZYDATNOŚCI DO OKREŚLONYCH ZASTOSOWAŃ. Bliższe informacje na ten temat można uzyskać z Powszechnej Licencji Publicznej GNU.")
print("Powszechnej Licencji Publicznej GNU powinna zostać ci dostarczona razem z tym programem")
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

print("Zapis do pliku '%s'. Upewnij się, że jest pusty!" % filepath)

con = fdb.connect(database=database, user=user, password=password)
cur = con.cursor()
# Main loop
print("Wszystkie dane wpisane prawidłowo")

cur.execute("SELECT NUMERDZIALKI FROM \"@PZD_DZIALKI\" ")
listadzialek = cur.fetchall()
# Creating list in file
L = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
print("Długość listy (maksymalna liczba ID naliczeń) to: "+ str(len(L)) + " (Pierwszy indeks to zero)")
potwierdzenie = input("Liczba wszystkich działek to:" + str(len(listadzialek)) + " Prawidłowo? [T/n]")
if potwierdzenie == "T" or potwierdzenie == "t":

    for h in range(len(listadzialek)):
        L = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        nrdzlist = listadzialek[h]
        nrdz = nrdzlist[0]
        print("Obsługuję działkę nr: " + nrdz)

        # TODO: Interface!!

        cur.execute("SELECT IDDZIALKI FROM \"@PZD_DZIALKI\" WHERE NUMERDZIALKI='%s' " % nrdz)
        iddzialkilist = cur.fetchall()
        iddzialkituple = iddzialkilist[0]
        iddzialki = iddzialkituple[0]
        # print("id dzialki:")
        # print(iddzialki)

        f = open(filepath, "a")

        L[0] = nrdz

        cur.execute("SELECT IDNALICZENIA FROM \"@PZD_NALICZENIA\" WHERE IDDZIALKI='%s'" % iddzialki)
        idnaliczenia = cur.fetchall()

        kwotanaliczen = 0

        i = 0
        j = 0
        KwotaOplat = 0

        for i in range(len(idnaliczenia)):

            jednoid = idnaliczenia[i]
            jednoidnal = jednoid[0]
            cur.execute("SELECT KWOTA FROM \"@PZD_NALICZENIAPOZ\" WHERE IDNALICZENIA='%s'" % jednoidnal)
            kwotalista = cur.fetchall()

            # accrual calculation stops here !!!

            # --------------------------------------------------------------------

            # checking accrual category
            cur.execute("SELECT IDSLOOPLATY FROM \"@PZD_NALICZENIAPOZ\" WHERE IDNALICZENIA='%s'" % jednoidnal)
            idsioplaty = cur.fetchall()
            # print("IDOPLATY:")
            # print(idsioplaty)

            # left to pay check
            cur.execute("SELECT IDZOBOWIAZANIAKONTR FROM \"@PZD_NALICZENIAPOZ\" WHERE IDNALICZENIA='%s'" % jednoidnal)
            IDZOBOWIAZANIAKONTR = cur.fetchall()

            # Weird section
            for a in range(len(IDZOBOWIAZANIAKONTR)):
                idzobpierw = IDZOBOWIAZANIAKONTR[a]
                idzobdrug = idzobpierw[0]
                # print("idzobowikontr")
                # print(idzobdrug)
                cur.execute(
                    "SELECT POZOSTALA_ZALEGLOSC FROM \"@ZAPL_ZOBOWIAZANIAKONTR\" WHERE IDZOBOWIAZANIAKONTR='%s'" % (
                        idzobdrug))
                pozostalo = cur.fetchall()

                for l in range(len(pozostalo)):
                    pozostalojeden = pozostalo[l]
                    pozostalodwa = pozostalojeden[0]

                    if pozostalodwa != 0:
                        indeks = idsioplaty[a]
                        indekss = indeks[0]
                        if str(indekss) == "None":
                            indekss = 38

                        opnalist = L[int(indekss)]
                        L[indekss] = opnalist + pozostalodwa
                    l = l + 1
                a = a + 1

                # done
                # --------------------------------------------------------------------------------------------------
                # returning to accrual calculation
            for j in range(len(kwotalista)):
                kwotatuple = kwotalista[j]
                kwota = kwotatuple[0]
                kwotanaliczen = kwotanaliczen + kwota
                j = j + 1

            i = i + 1

            # Payment section
        # For first one
        cur.execute("SELECT IDSIKONTRWLA FROM \"@PZD_RELDZIALKISIKONTR\" WHERE IDDZIALKI='%s'" % iddzialki)
        idsikontrwlarawWLAS = cur.fetchall()
        # For second one
        cur.execute("SELECT IDSIKONTRMALZ FROM \"@PZD_RELDZIALKISIKONTR\" WHERE IDDZIALKI='%s'" % iddzialki)
        idsikontrwlarawMALZ = cur.fetchall()

        # Adding second one to te first one's list
        idsikontrwlarawWLAS.extend(idsikontrwlarawMALZ)
        idsikontrwlaraw = idsikontrwlarawWLAS

        #print(idsikontrwlaraw)
        # To remove duplicates
        idsikontrwla = list(dict.fromkeys(idsikontrwlaraw))
        #print(idsikontrwla)
        for l in range(len(idsikontrwla)):
            idsikontrwlaJed = idsikontrwla[l]
            idsikontrwlaDwa = idsikontrwlaJed[0]
            l = l + 1

            if idsikontrwlaDwa is not None:
                #print("ID kontrachenta: " + str(idsikontrwlaDwa))
                cur.execute("SELECT INDEKSKONTR FROM \"SIKONTR\" WHERE IDSIKONTR='%s'" % idsikontrwlaDwa)
                indekskontr = cur.fetchall()
                indekskontr = indekskontr[0]
                indekskontr = indekskontr[0]
                #print(indekskontr)
                # KP and KW
                cur.execute("SELECT KWOTA FROM \"DOKUMENTYKASOWE\" WHERE INDEKSKONTR ='%s'" % indekskontr)
                ZbiorczeOplaty = cur.fetchall()
                #print(ZbiorczeOplaty)

                k = 0
                for k in range(len(ZbiorczeOplaty)):
                    OplataJeden = ZbiorczeOplaty[k]
                    KwotaOplatyJeden = OplataJeden[0]
                    KwotaOplat = KwotaOplat + KwotaOplatyJeden
                    k = k + 1
                #print("Kwota opłat: " + str(KwotaOplat))
                # Bank statements
                cur.execute("SELECT KWOTA FROM \"@WYCIAGI_WYC_POZ\" WHERE INDEKSKONTR ='%s'" % indekskontr)
                Wyciagi = cur.fetchall()

                m = 0
                for m in range(len(Wyciagi)):
                    OplataJeden = Wyciagi[m]
                    KwotaOplatyJeden = OplataJeden[0]
                    #print("Kwota z wyciągu:" + str(KwotaOplatyJeden))
                    KwotaOplat = KwotaOplat + KwotaOplatyJeden
                    m = m + 1

        Saldo = kwotanaliczen - KwotaOplat
        print("Saldo:" + str(Saldo))
        L[41] = kwotanaliczen
        L[42] = KwotaOplat
        L[43] = Saldo

        f.write("\n")
        for g in range(len(L)):
            f.write(str(L[g]))
            f.write(";")
            g = g + 1
        f.close()
        h = h + 1
        print("Wiersz zapisano")
    print("Program zakończył pracę sukcesem. Wyłączam za 3 sekundy")
    time.sleep(3)
else:
    print("Nie wpisano 'T'. Program zakończony przez użytkownika. Wyłączam za 3 sekundy")
    time.sleep(3)
con.close()
