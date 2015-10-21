# -*- coding: utf-8 -*- 
import getpass
import urllib
import urllib2
from cookielib import CookieJar
import re

cookie=CookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
def logowanie(u,p):
	data=urllib.urlencode({'u':u,'p':p})
	site=opener.open("https://e-nadawca.poczta-polska.pl",data)
	odmowa=re.search("Odmowa zalogowania",site.read())
	try:
		odmowa.group()
		return -1
	except:
		return 0

class Zbior:
	'''Klasa operująca za zbiorach'''
	def dodaj(self,nazwa,data):
		'''Tworzy zbiór, zwraca id_zbioru

		nazwa=2015-10-21%5C2&data_nadania=2015-10-21&pni=&idnadawca_profil=&action=InsZbior&js=true
		pni -> Urząd nadania
		idnadawca_profil -> do uzupełnienia

		'''
		data=urllib.urlencode({'nazwa':str(nazwa),'data_nadania':str(data),'pni':'559619','idnadawca_profil':'18167','action':'InsZbior','js':'true'})
		site=opener.open('https://e-nadawca.poczta-polska.pl/przesylki/',data)
		resp=site.read()
		print resp

	def usun(self,id_zbioru):
		'''Usuwa zbiór

		GET /przesylki/?action=DelZbior&arg1=&js=true HTTP/1.1

		'''
		data=urllib.urlencode({'action':'DelZbior','arg1':str(id_zbioru),'js':'true'})
		site=opener.open("https://e-nadawca.poczta-polska.pl/przesylki/",data)
		resp=site.read()
		info=re.search("Zbiór został usunięty",resp)
		if info is None:
			print "Błąd: Usunięcie zbioru nie powiodło się"
		else:
			print "Zbiór został usunięty"

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
		site=opener.open("https://e-nadawca.poczta-polska.pl/przesylki/",data)
		resp=site.read()
		r_title=re.compile(str(id_zbioru)+"' OnClick='return Ajax.Go\(this\)' target='self'>(?P<nazwa>.{12,50})</a>")
		r_info=re.compile(str(id_zbioru)+"' onmouseover='ToolTip[(]\"Data utworzenia: (?P<data_utworzenia>\d{4}-\d{2}-\d{2})&lt;br&gt;Planowana data nadania:<br >(?P<data_nadania>\d{4}-\d{2}-\d{2})&lt;br&gt;Utworzony przez: (?P<wlasciciel>\D+<br >\D+)&lt;br&gt;")
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
		site=opener.open("https://e-nadawca.poczta-polska.pl/przesylki/",data)
		resp=site.read()
		zbior=re.findall("(\d{8})' OnClick='return Ajax.Go\(this\)' target='self'>(.{12,50})</a>",resp)
		return zbior

def main():
	u=raw_input('uzytkownik: ')
	p=getpass.getpass('haslo: ')
	if logowanie(u,p)==-1:
		print "Błąd: nieprawidłowy login lub hasło"
	else:
		print "Zalogowano"
		zbior=Zbior()
		while True:
			cmd=raw_input('$ ')
			if cmd=='list':
				for zb in zbior.pokazWszystkie():
					print zb[0]+' - '+zb[1]
			elif cmd.startswith('info '):
				param=int(cmd[cmd.index(' ')+1:])
				for key,value in zbior.pokazZbior(param).iteritems():
					print key+' = '+value
			elif cmd.startswith('del '):
				param=int(cmd[cmd.index(' ')+1:])
				prompt=raw_input('Jesteś pewny, że chcesz usunąć zbiór '+str(param)+'? t/n ')
				if prompt=='t':
					zbior.usun(param)
			elif cmd=='exit':
				exit()
		#przesylka=raw_input("Podaj rodzaj przesyłki (1-polecona, 2-zwykła): ")
		#if int(przesylka)==1:
		#	p=open("2.csv","r")
		#	for linia in p:
		#		print linia
		#		tablica=linia.split(';')
		#		data=urllib.urlencode({
		#			'kategoria':'EKONOMICZNA','gabaryt':'GABARYT_A','masa_gramy':'','potw_odbioru':'1','potw_odbioru_ilosc':'1','epo_zasady':'0','idzbior':str(zbior()),'idrodzaj_przesylki':'10','nazwa':tablica[0]+' '+tablica[1],'nazwa2':'','ulica':tablica[2]+','+tablica[3],'numer_domu':tablica[4],'numer_lokalu':tablica[5],'kod_pocztowy':tablica[6],'miejscowosc':tablica[7],'mobile':'','email':'','telefon':'','id_adresat':'1','opis':'','szablon_nazwa':'','action':'InsPrzesylka','js':'true'})
		#		site=opener.open("https://e-nadawca.poczta-polska.pl/przesylki/",data)

if __name__ == '__main__':
	main()