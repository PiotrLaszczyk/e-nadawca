# -*- coding: utf-8 -*- 
import getpass
import urllib
import urllib2
from cookielib import CookieJar, FileCookieJar, LWPCookieJar
import re

cookie=LWPCookieJar("_cookie")
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

def zbior():
	data=urllib.urlencode({'action':'SetFolder','arg1':'1','js':'true'})
	site=opener.open("https://e-nadawca.poczta-polska.pl/przesylki/",data)
	zbior=re.findall("(\d{8})' OnClick='return Ajax.Go\(this\)' target='self'>(.{12,50})</a>",site.read())
	print "\nDostępne zbiory:"
	for z in zbior:
		print z[0]+' - '+z[1]
	zbior=raw_input("Podaj id zbioru: ")
	return zbior

def main():
	u=raw_input('uzytkownik: ')
	p=getpass.getpass('haslo: ')
	if logowanie(u,p)==-1:
		print "Błąd: nieprawidłowy login lub hasło"
	else:
		print "Zalogowano"
		print zbior()

if __name__ == '__main__':
	main()