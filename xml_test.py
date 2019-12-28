import xml.dom.minidom

def parse_tftinfo():
	doc = xml.dom.minidom.parse('tftinfo.xml')
	champs = doc.getElementsByTagName('champ')
	for champ in champs:
		synergies = champ.getElementsByTagName('synergy')
		for synergy in synergies:
			print(synergy.firstChild.data)
	return doc

print(parse_tftinfo())