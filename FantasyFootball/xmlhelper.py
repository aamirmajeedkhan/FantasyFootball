# Imports for XML EndPoints
from xml.etree import ElementTree
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from FantasyFootball.Model.schema import Team, Player

def generate_xml(teams,players):
	# Parent Top Element
	root = Element("FantasyFootball")	
	for t in teams:
		# First Child Element
		team = SubElement(root, 'team')
		# adding team attributes
		team.set('name',t.name)
		team.set('id',str(t.id))
		
		team.set('description',t.description)    
    	for p in players:
    		if(p.team_id == t.id):
    			# add child element player
    			player=	SubElement(team, 'player')
                # add attribute to player element
    			player.set('id',str(p.id))
    			player.set('name',p.name)
    			player.set('description',p.description)
    			player.set('position',p.position)
	return prettify(root)
	
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    code source: http://pymotw.com/2/xml/etree/ElementTree/create.html
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')    
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")