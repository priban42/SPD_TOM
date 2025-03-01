import xml.etree.ElementTree as ET

def svg_to_dict(svg_file_path):
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
    # Convert the root SVG element and its children
    return element_to_dict(root)
svg_file_path = "buildings/T2_0.svg"
svg_dict = svg_to_dict(svg_file_path)
pass