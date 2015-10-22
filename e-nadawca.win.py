# -*- coding: utf-8 -*- 
import getpass
import urllib
import urllib2
from cookielib import CookieJar
import re

cookie=CookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
def zapytanie(url,data=None):
		site=opener.open(url,data)
		return site.read()

class Enadawca:
	def login(self,u,p):
		data=urllib.urlencode({'u':u,'p':p})
		resp=zapytanie('https://e-nadawca.poczta-polska.pl',data)
		odmowa=re.search('Odmowa zalogowania',resp)
		try:
			odmowa.group()
			return -1 # Błąd: nieprawidłowy login lub hasło
		except:
			return 0 # Zalogowano

	def logout(self):
		data=urllib.urlencode({'action':'LogOut'})
		resp=zapytanie('https://e-nadawca.poczta-polska.pl',data)

	def session(self):
		resp=zapytanie('https://e-nadawca.poczta-polska.pl/przesylki')
		info=re.search('Zaloguj się...',resp)
		try:
			info.group()
			return -1 # Błąd: sesja wygasła
		except:
			return 0 # Sesja trwa

class Zbior:
	'''Klasa operująca za zbiorach'''
	def utworzZbior(self,nazwa,data):
		'''Tworzy zbiór, zwraca id_zbioru

		nazwa=2015-10-21%5C2&data_nadania=2015-10-21&pni=&idnadawca_profil=&action=InsZbior&js=true
		pni -> Urząd nadania
		idnadawca_profil -> do uzupełnienia

		'''
		data=urllib.urlencode({'nazwa':str(nazwa).split("'")[0],'data_nadania':str(data),'pni':'559619','idnadawca_profil':'18167','action':'InsZbior','js':'true'})
		resp=zapytanie('https://e-nadawca.poczta-polska.pl/przesylki/',data)
		info=re.search('alertBox',resp)
		try:
			info.group()
			return -1 # Błąd: Nie udało się utworzyć zbioru
		except:
			return 0

	def usunZbior(self,id_zbioru):
		'''Usuwa zbiór

		GET /przesylki/?action=DelZbior&arg1=&js=true HTTP/1.1

		'''
		data=urllib.urlencode({'action':'DelZbior','arg1':str(id_zbioru),'js':'true'})
		resp=zapytanie('https://e-nadawca.poczta-polska.pl/przesylki/',data)
		info=re.search('Zbiór został usunięty',resp)
		if info is None:
			return -1 # Błąd: Usunięcie zbioru nie powiodło się
		else:
			return 0 # Zbiór został usunięty

	def pokazZbior(self,id_zbioru):
		'''Zwraca słownik informacji o zbiorze, nazwa, planowana data nadania itp.

		'wlasciciel': 'Andrzej<br >Andrzejewski', 
		'data_utworzenia': '2015-10-21', 
		'data_nadania': '2015-10-21, 
		'nazwa': '2015-10-21\3 testowy'}

		GET /przesylki/?action=SetFolder&arg1=2&js=true HTTP/1.1

		arg:1 -> Przygotowane
		arg:2 -> Wysłane
		arg:3 -> Odebrane
		arg:4 -> Archiwum
		arg:5 -> Kosz

		'''
		data=urllib.urlencode({'action':'SetFolder','arg1':'1','js':'true'})
		resp=zapytanie('https://e-nadawca.poczta-polska.pl/przesylki/',data)
		r_title=re.compile(str(id_zbioru)+'\' OnClick=\'return Ajax.Go[(]this[)]\' target=\'self\'>(?P<nazwa>.{12,50})</a>')
		r_info=re.compile(str(id_zbioru)+'\' onmouseover=\'ToolTip[(]["]Data utworzenia: (?P<data_utworzenia>\d{4}-\d{2}-\d{2})&lt;br&gt;Planowana data nadania:<br >(?P<data_nadania>\d{4}-\d{2}-\d{2})&lt;br&gt;Utworzony przez: (?P<wlasciciel>\D+<br >\D+)&lt;br&gt;')
		title=r_title.search(resp).groupdict()
		info=r_info.search(resp).groupdict()
		new=info.copy()
		new.update(title)
		return new

	def pokazWszystkie(self):
		'''
		Zwraca listę dostępnych zbiorów  w przygotowaniu
		'''
		data=urllib.urlencode({'action':'SetFolder','arg1':'1','js':'true'})
		resp=zapytanie('https://e-nadawca.poczta-polska.pl/przesylki/',data)
		zbior=re.findall('(\d{8})\' OnClick=\'return Ajax.Go\(this\)\' target=\'self\'>(.{10,50})</a>',resp)
		return zbior

	def dodajPrzeslke(self,typ,zbior,tablica):
		data_polecony=urllib.urlencode({
					'kategoria':'EKONOMICZNA','gabaryt':'GABARYT_A','masa_gramy':'','potw_odbioru':'1','potw_odbioru_ilosc':'1','epo_zasady':'0',
					'idzbior':str(zbior),'idrodzaj_przesylki':'10','nazwa':tablica[0]+' '+tablica[1],'nazwa2':'','ulica':tablica[2]+', '+tablica[3],
					'numer_domu':tablica[4],'numer_lokalu':tablica[5],'kod_pocztowy':tablica[6],'miejscowosc':tablica[7],'mobile':'','email':'',
					'telefon':'','id_adresat':'1','opis':'','szablon_nazwa':'','action':'InsPrzesylka','js':'true'})
		data_zwykly=urllib.urlencode({
					'kategoria':'EKONOMICZNA','gabaryt':'GABARYT_A','masa_gramy':'350','idzbior':+str(zbior),'idrodzaj_przesylki':'22',
					'nazwa':+tablica[0]+' '+tablica[1],'nazwa2':'','ulica':+tablica[2]+', '+tablica[3],'numer_domu':+tablica[4],'numer_lokalu':+tablica[5],
					'kod_pocztowy':+tablica[6],'miejscowosc':+tablica[7],'mobile':'','email':'','telefon':'','id_adresat':'','opis':'','szablon_nazwa':'',
					'action':'InsPrzesylka','js':'true'})


def main():
	enadawca=Enadawca()
	u=raw_input('uzytkownik: ')
	p=getpass.getpass('haslo: ')
	if enadawca.login(u,p)==-1:
		print 'Błąd: nieprawidłowy login lub hasło'
	else:
		print '------------------------'
		zbior=Zbior()
		while enadawca.session()==0:
			cmd=raw_input('$ ')
			if cmd=='help':
				print "\n"
				print "add <nazwa_zbioru> <data> - dodaje zbiór \nnp. add \'zbior testowy\' 2015-10-31"
				print 'del <id_zbioru> - usuwa zbiór'
				print 'exit - konczy prace'
				print 'help - wyświetla to co widzisz teraz'
				print 'info <id_zbioru> - wyświetla informacje o zbiorze'
				print 'list - wyświetla dostępne zbiory'
				print "\n"
			elif cmd=='list':
				for zb in zbior.pokazWszystkie():
					print zb[0]+' - '+zb[1]
			elif cmd.startswith('info '):
				param=int(cmd[cmd.index(' ')+1:])
				if param=='':
					print 'Usage: info <id_zbioru>'
				else:
					for key,value in zbior.pokazZbior(param).iteritems():
						print key+' = '+value
			elif cmd.startswith('del '):
				param=int(cmd[cmd.index(' ')+1:])
				if param=='':
					print 'Usage: del <id_zbioru>'
				else:
					prompt=raw_input('Jesteś pewny, że chcesz usunąć zbiór '+str(param)+'? t/n ')
					if prompt=='t':
						zbior.usunZbior(param)
			elif cmd.startswith('add '):
				param1=cmd[cmd.index("'")+1:]
				param2=param1[param1.index("'")+2:]
				if param1=='' or param2=='':
					print 'Usage: add \'<nazwa_zbioru>\' <data_w_formacie_2015-10-31>'
				else:
					zbior.utworzZbior(param1,param2)
			elif cmd=='exit':
				exit()
		print 'Sesja wygasła'
		#przesylka=raw_input(Podaj rodzaj przesyłki (1-polecona, 2-zwykła): )
		#if int(przesylka)==1:
		#	p=open(2.csv,r)
		#	for linia in p:
		#		print linia
		#		tablica=linia.split(';')
		#		
		#		site=opener.open(https://e-nadawca.poczta-polska.pl/przesylki/,data)

if __name__ == '__main__':
	main()