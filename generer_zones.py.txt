import xml.etree.ElementTree as ET
import sys

def create_taz_from_net(net_file, output_file):
    """
    Analyse un fichier .net.xml de SUMO pour identifier les arêtes de bordure
    et génère un fichier additionnel avec des Zones d'Activité de Trafic (TAZ)
    géographiquement regroupées (Nord, Sud, Est, Ouest).

    Args:
        net_file (str): Chemin vers le fichier goodmap.net.xml.
        output_file (str): Chemin vers le fichier de sortie (ex: zones.add.xml).
    """
    print(f"Analyse du fichier réseau : {net_file}")
    
    try:
        tree = ET.parse(net_file)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"ERREUR : Le fichier réseau '{net_file}' n'a pas été trouvé.", file=sys.stderr)
        print("Veuillez vous assurer que le script est dans le même dossier que votre fichier .net.xml.", file=sys.stderr)
        return
    except ET.ParseError:
        print(f"ERREUR : Impossible de parser le fichier XML '{net_file}'. Le fichier est peut-être corrompu.", file=sys.stderr)
        return

    # 1. Trouver les limites de la carte
    location = root.find('location')
    if location is None or 'convBoundary' not in location.attrib:
        print("ERREUR: Impossible de trouver l'attribut 'convBoundary' dans la balise <location>.", file=sys.stderr)
        return
        
    boundary_str = location.get('convBoundary')
    min_x, min_y, max_x, max_y = map(float, boundary_str.split(','))
    
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    
    print(f"Limites de la carte détectées : X=[{min_x}, {max_x}], Y=[{min_y}, {max_y}]")

    # 2. Identifier les arêtes de bordure
    # Une arête est considérée comme une bordure si elle n'a pas de successeur ou de prédécesseur défini par l'utilisateur.
    # L'attribut "function='internal'" désigne les arêtes à l'intérieur des jonctions, que nous devons ignorer.
    all_edges = {edge.get('id') for edge in root.findall("edge") if edge.get('function') != 'internal'}
    
    internal_edges = set()
    for edge in root.findall("edge"):
        if 'from' in edge.attrib and 'to' in edge.attrib:
            # Si une arête a une connexion sortante, elle n'est pas une arête "puits" finale.
            for connection in root.findall(f"connection[@from='{edge.get('id')}']"):
                internal_edges.add(edge.get('id'))

    # Une heuristique simple : les arêtes de bordure ont peu de connexions.
    # On va trouver les jonctions de bordure (celles avec peu d'arêtes connectées)
    junction_connections = {}
    for edge in root.findall("edge"):
        from_node = edge.get('from')
        to_node = edge.get('to')
        if from_node:
            junction_connections[from_node] = junction_connections.get(from_node, 0) + 1
        if to_node:
            junction_connections[to_node] = junction_connections.get(to_node, 0) + 1

    border_junction_ids = {jid for jid, count in junction_connections.items() if count <= 2}

    border_edges = {}
    
    for edge in root.findall("edge"):
        edge_id = edge.get('id')
        if edge.get('function') == 'internal':
            continue

        from_node = edge.get('from')
        to_node = edge.get('to')
        
        if from_node in border_junction_ids or to_node in border_junction_ids:
            # Calcule la position moyenne de l'arête pour la catégoriser
            lane = edge.find('lane')
            if lane is not None:
                shape_coords = lane.get('shape').split()
                x_coords = [float(c.split(',')[0]) for c in shape_coords]
                y_coords = [float(c.split(',')[1]) for c in shape_coords]
                avg_x = sum(x_coords) / len(x_coords)
                avg_y = sum(y_coords) / len(y_coords)

                # 3. Catégoriser géographiquement
                # On utilise une diagonale pour séparer les zones
                if avg_y > avg_x - (center_x - center_y): # Au dessus de la diagonale y = x - (cx-cy)
                    if avg_y > -avg_x + (center_x + center_y): # Au dessus de la diagonale y = -x + (cx+cy)
                        zone = "Nord"
                    else:
                        zone = "Est"
                else: # En dessous de la diagonale y = x - (cx-cy)
                    if avg_y > -avg_x + (center_x + center_y): # Au dessus de la diagonale y = -x + (cx+cy)
                        zone = "Ouest"
                    else:
                        zone = "Sud"
                
                if zone not in border_edges:
                    border_edges[zone] = []
                border_edges[zone].append(edge_id)

    print("Catégorisation des arêtes de bordure terminée.")
    for zone, edges in border_edges.items():
        print(f" - Zone {zone}: {len(edges)} arêtes trouvées.")

    # 4. Générer le fichier XML
    additional = ET.Element('additional')
    
    for zone, edges in sorted(border_edges.items()):
        taz_id = f"taz_{zone.lower()}"
        taz = ET.SubElement(additional, 'taz', id=taz_id)
        
        for edge_id in sorted(edges):
            # Chaque arête de bordure peut être une source (départ) et un puits (arrivée)
            ET.SubElement(taz, 'tazSource', id=edge_id, weight="1")
            ET.SubElement(taz, 'tazSink', id=edge_id, weight="1")

    tree = ET.ElementTree(additional)
    # Rendre le XML plus lisible (pretty print)
    ET.indent(tree, space="\t", level=0)
    
    tree.write(output_file, encoding='UTF-8', xml_declaration=True)
    
    print(f"\nSuccès ! Le fichier '{output_file}' a été généré.")
    print("Vous pouvez maintenant l'utiliser avec l'option --taz-files dans randomTrips.py.")

# --- Point d'entrée du script ---
if __name__ == "__main__":
    # Assurez-vous que le nom du fichier réseau est correct
    network_filename = "goodmap.net.xml" 
    output_filename = "zones.add.xml"
    create_taz_from_net(network_filename, output_filename)
