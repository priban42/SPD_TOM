import xml.etree.ElementTree as ET

def parse_svg_toilets(svg_file_path):
    # Parse the SVG file
    tree = ET.parse(svg_file_path)
    root = tree.getroot()
    # Convert XML to a dictionary
    def element_to_dict(element):
        # Convert element to a dictionary of its attributes
        data = {k: v for k, v in element.attrib.items()}
        # If the element has children, recurse into them
        children = list(element)
        if children:
            data['children'] = [element_to_dict(child) for child in children]
        return data
    raw_dict = element_to_dict(root)
    raw_tolets = None
    t1 = (0, 0)
    transform1 = raw_dict['children'][2]['transform'][10:-1].split(',')
    t1 = (float(transform1[0]), float(transform1[1]))
    t2 = (0, 0)
    for i in range(len(raw_dict['children'][2]['children'])):
        if  '{http://www.inkscape.org/namespaces/inkscape}label' in raw_dict['children'][2]['children'][i]:
            if raw_dict['children'][2]['children'][i]['{http://www.inkscape.org/namespaces/inkscape}label'] == 'toilets':
                raw_tolets = raw_dict['children'][2]['children'][i]['children']
                transform2 = raw_dict['children'][2]['children'][i]['transform'][10:-1].split(',')
                t2 = (float(transform2[0]), float(transform2[1]))
    toilets = {}
    width = float(raw_dict['width'][:-2])
    height = float(raw_dict['height'][:-2])
    for i in range(len(raw_tolets)):
        label = raw_tolets[i]['{http://www.inkscape.org/namespaces/inkscape}label']
        toilets[raw_tolets[i]['{http://www.inkscape.org/namespaces/inkscape}label']] = {'width':100*float(raw_tolets[i]['width'])/width,
                                                                                          'height':100*float(raw_tolets[i]['height'])/height,
                                                                                          'x':100*(float(raw_tolets[i]['x']) + t1[0] + t2[0])/width,
                                                                                          'y':100*(float(raw_tolets[i]['y']) + t1[1] + t2[1])/height,
                                                                                          'gender':label.split("_")[4],
                                                                                          'stall_count':int(label.split("_")[5]),
                                                                                          'visits':None,
                                                                                          'visit_time':None}
    return toilets