import fdb
import time
import configparser

print("Generator raportu opłat i nadpłat działkowców ROD. Wersja 2.8")
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
IDinne = parser['BASIC']['idinne'] #ID of accural to which all unknown accurals will be added
debug_mode = int(debug)

print("Zapis do pliku '%s'. Upewnij się, że jest pusty!" % filepath)

con = fdb.connect(database=database, user=user, password=password)
cur = con.cursor()

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

        cur.execute("SELECT IDDZIALKI FROM \"@PZD_DZIALKI\" WHERE NUMERDZIALKI='%s' " % nrdz)
        iddzialkilist = cur.fetchall()
        iddzialki = iddzialkilist[0][0]
        if debug_mode == 1:
            print("id dzialki:")
            print(iddzialki)

        L[0] = nrdz

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
        cur.execute("SELECT EMAIL FROM SIKONTR WHERE IDSIKONTR='%s'" % idaktualnego)
        emailraw = cur.fetchall()
        email = emailraw[0][0]
        if debug_mode == 1:
            print("email:")
            print(email)

        # Finding ID for co-owners
        cur.execute("SELECT IDSIKONTRMALZ FROM \"@PZD_RELDZIALKISIKONTR\" WHERE IDDZIALKI='%s'" % iddzialki)
        idsikontrwlarawMALZ = cur.fetchall()

        # Joining owners and co-owners ID lists together
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
    print("Program zakończył pracę sukcesem. Wyłączam za 3 sekundy")
    time.sleep(3)
else:
    print("Nie wpisano 'T'. Program zakończony przez użytkownika. Wyłączam za 3 sekundy")
    time.sleep(3)
con.close()
