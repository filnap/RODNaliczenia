# RODNaliczenia
Software made for polish "Family Allotment Garden" capable of extracting data from firebird database 

PL version in "instrukcja.txt"

Manual for V3.3 app was tested on DGCS 22.27
1. Software must be started on computer with firebird server
2. Check if data in "config.txt" is correct (database address, username, password are default for DGCS). Software can create XML file and send it to server.
3. Start program (RODNaliczeniaVX.X.exe)
4. If nothing is displayed it's ok - exe files takes long to load.
5. If program shuts down quickly there is an error in "config.txt" or unexpected error occurred.
6. File "dane.txt" is automatically deleted when program starts, and new one is created.
7. After typing "t" or "T" program should start and will shut down when done (It is possible to start automatically when "auto = 1")
8. File "dane.txt" is created. Structure:
	a. First column is parcel number
	b. Next columns are next types of accruals
	c. fourth column from the end is sum of accruals
	d. fourth column from the end is sum of payments
	e. fourth column from the end is balance (minus is excess payment)
	f. fourth column from the end is e-mail address (for automatic messages).
9. File sample.xml is created
Information included is date of last bank statement, electricy reading, name, surname, telephone, e-mail accruals and balance. If parameter "ftp_enable = 1" program will try to send data over FTP.
10. File Bugs.txt contains know bugs (in polish)

