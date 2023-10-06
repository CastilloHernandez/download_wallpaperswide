import requests
from bs4 import BeautifulSoup
from os.path  import basename
import os
import time 
import sqlite3
import argparse
import configparser

resoluciones = []

def cargar_argumentos_desde_archivo(args):
	config = configparser.ConfigParser()
	config.read('download_wallpaperswide.ini')
	if not args.reintentos and 'Configuracion' in config:
		args.reintentos = config['Configuracion'].get('reintentos', None)
	if not args.tiempoespera and 'Configuracion' in config:
		args.tiempoespera = config['Configuracion'].get('tiempoespera', None)
	if not args.profundidad and 'Configuracion' in config:
		args.profundidad = config['Configuracion'].get('profundidad', None)
	if not args.profundidad and 'Configuracion' in config:
		args.profundidad = config['Configuracion'].get('paginas', None)
	carga_resoluciones = config.items("Resoluciones")
	for key, resolucon in carga_resoluciones:
		resoluciones.append(resolucon)
	return args

def configurar_parser():
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('busqueda', nargs='?', default='') 
	parser.add_argument('--reintentos', help='Reintentos de las descarga')
	parser.add_argument('--tiempoespera', help='Tiempo de espera entre reintentos')
	parser.add_argument('--profundidad', help='Profundidad en la descarga de de relacionados')
	parser.add_argument('--paginas', help='Paginas a descargar (Por default todas)')
	parser.add_argument('--redescarga', default=False, action='store_true', help='')
	return parser

def cortar_cadena(texto):
	indice_interrogacion = texto.find('?')
	if indice_interrogacion >= 0:
		return texto[:indice_interrogacion]
	else:
		return texto

def verificar_archivo_descargado(db_cursor, hash_archivo):
	db_cursor.execute("SELECT COUNT(*) FROM archivos_descargados WHERE hash = ?", (hash_archivo,))
	resultado = db_cursor.fetchone()
	return resultado[0] > 0

def guardar_archivo_descargado(db_cursor, hash_archivo):
	db_cursor.execute("INSERT INTO archivos_descargados (hash) VALUES (?)", (hash_archivo,))
	db_cursor.connection.commit()

def get_with_retries(url):
	intentos_realizados = 0
	print ('Solicitando: ' + url)
	while intentos_realizados < int(args.reintentos):
		try:
			response = requests.get(url, timeout= int(args.tiempoespera))
			if response.status_code == 200:
				return response
			else:
				pass
		except requests.RequestException as e:
			pass
		intentos_realizados += 1
		time.sleep(int(args.tiempoespera))
	raise Exception(f"No se pudo completar la solicitud.")

def downloadmanga(l, profundidadactual=0, paginaactual=0):
	profundidadactual = profundidadactual + 1
	try:
		r = get_with_retries(l)
		soup = BeautifulSoup(r.text, 'lxml')
	except:
		return

	imgs = soup.findAll('a', attrs = {'target' : '_self'})
	for img in imgs:
		for res in resoluciones:
			#print (img.text)
			if img.text == res:
				if args.redescarga or not verificar_archivo_descargado(cursor, cortar_cadena(img.get('href'))):
					if os.path.exists(res):
						pass
					else:
						os.makedirs(res)
					try:
						with open(os.path.join(res , basename(cortar_cadena(img.get('href')))),"wb") as f:
							f.write(get_with_retries('https://wallpaperswide.com' + cortar_cadena(img.get('href'))).content)
						guardar_archivo_descargado(cursor, cortar_cadena(img.get('href')))
					except:
						pass

	divs = soup.findAll('div', attrs = {'class' : 'mini-hud', 'id':'hudtitle'})
	for div in divs:
		pages = div.findChildren()
		for page in pages:
			if 'href' in page.attrs:
				if len(page.get('href')) > 0:
					if profundidadactual > int(args.profundidad):
						return
					downloadmanga('https://wallpaperswide.com' + page.get('href'), profundidadactual, paginaactual)

	divs = soup.findAll('div', attrs = {'class' : 'pagination'})
	for div in divs:
		pages = div.findAll('a')
		for page in pages:
			if page.text == 'Next »':
				if len(page.get('href')) > 0:
					paginaactual = paginaactual + 1
					if paginaactual < int(args.paginas) or int(args.paginas) == 0:
						downloadmanga('https://wallpaperswide.com' + page.get('href').replace(' ','%20'), 0, paginaactual)

conexion = sqlite3.connect('download_wallpaperswide.db')
cursor = conexion.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS archivos_descargados (hash TEXT PRIMARY KEY)")

parser = configurar_parser()
args = parser.parse_args()
args = cargar_argumentos_desde_archivo(args)

if __name__ == '__main__':
	search = str(args.busqueda).replace(' ','%20')
	if len(search) > 0:
		downloadmanga('https://wallpaperswide.com/search.html?q=' + search)
	else:
		downloadmanga('https://wallpaperswide.com/')