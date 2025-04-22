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
    if "transform" in raw_dict['children'][2]:
        transform1 = raw_dict['children'][2]['transform'][10:-1].split(',')
        t1 = (float(transform1[0]), float(transform1[1]))
    t2 = (0, 0)
    for i in range(len(raw_dict['children'][2]['children'])):
        if  '{http://www.inkscape.org/namespaces/inkscape}label' in raw_dict['children'][2]['children'][i]:
            if raw_dict['children'][2]['children'][i]['{http://www.inkscape.org/namespaces/inkscape}label'] == 'toilets':
                raw_tolets = raw_dict['children'][2]['children'][i]['children']
                if "transform" in raw_dict['children'][2]['children'][i]:
                    transform2 = raw_dict['children'][2]['children'][i]['transform'][10:-1].split(',')
                else:
                    transform2 = (0, 0)
                t2 = (float(transform2[0]), float(transform2[1]))
    toilets = {}
    width = float(raw_dict['width'][:-2])  # width of the image
    height = float(raw_dict['height'][:-2])  # height of the image
    for i in range(len(raw_tolets)):
        label = raw_tolets[i]['{http://www.inkscape.org/namespaces/inkscape}label']
        stalls = {}
        toilet = None
        t3 = (0, 0)
        if "transform" in raw_tolets[i]:
            transform3 = raw_tolets[i]['transform'][10:-1].split(',')
            t3 = (float(transform3[0]), float(transform3[1]))
        for j in range(len(raw_tolets[i]['children'])):
            child_label = raw_tolets[i]['children'][j]['{http://www.inkscape.org/namespaces/inkscape}label']
            if child_label == 'toilet':
                toilet = raw_tolets[i]['children'][j]
            else:
                pass

                stalls[child_label] = {'width':100*float(raw_tolets[i]['children'][j]['width'])/width,
                                                                                          'height':100*float(raw_tolets[i]['children'][j]['height'])/height,
                                                                                          'x':100*(float(raw_tolets[i]['children'][j]['x']) + t1[0] + t2[0])/width,
                                                                                          'y':100*(float(raw_tolets[i]['children'][j]['y']) + t1[1] + t2[1])/height,}
        toilets[label] = {'width':100*float(toilet['width'])/width,
                                                                                          'height':100*float(toilet['height'])/height,
                                                                                          'x':100*(float(toilet['x']) + t1[0] + t2[0] + t3[0])/width,
                                                                                          'y':100*(float(toilet['y']) + t1[1] + t2[1] + t3[0])/height,
                                                                                          'gender':label.split("_")[4],
                                                                                          'stall_count':int(label.split("_")[5]),
                                                                                          'stalls':stalls,
                                                                                          'visits':None,
                                                                         'visit_time':None}
    return toilets, width, height