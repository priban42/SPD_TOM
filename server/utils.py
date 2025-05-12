import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pytz
import calendar
import numpy as np

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

def heatmap_color(value, a=0.3):
    """
    Map a float value between 0 and 1 to a heatmap color from green to red.
    """
    value = max(0.0, min(1.0, value))  # Clamp to [0, 1]
    r = int(255 * value)
    g = int(255 * (1 - value))
    b = 0
    return f'rgba({r}, {g}, {b}, {a})'


def get_time_labels(interval="today"):
    now = datetime.now()
    labels = []

    if interval == "day":
        for i in range(24):
            hour = (now - timedelta(hours=23 - i)).replace(minute=0, second=0, microsecond=0)
            labels.append(hour.strftime("%H:00"))

    elif interval == "week":
        for i in range(7):
            day = (now - timedelta(days=6 - i))
            labels.append(day.strftime("%d.%m"))

    elif interval == "month":
        for i in range(30):
            day = (now - timedelta(days=29 - i))
            labels.append(day.strftime("%d.%m"))

    elif interval == "year":
        for i in range(12):
            month = (now.replace(day=1) - timedelta(days=30 * (11 - i)))
            labels.append(month.strftime("%B"))

    return labels


def get_histogram(visit_timestamps, interval="day"):
    now = datetime.now()
    now_ts = now.timestamp()

    if interval == "day":
        bins = np.arange(0, 24 * 60 * 60 + 1, 60 * 60) + now_ts - 24 * 60 * 60

    elif interval == "week":
        bins = np.arange(0, 7 * 24 * 60 * 60 + 1, 24 * 60 * 60) + now_ts - 7 * 24 * 60 * 60

    elif interval == "month":
        bins = np.arange(0, 30 * 24 * 60 * 60 + 1, 24 * 60 * 60) + now_ts - 30 * 24 * 60 * 60

    elif interval == "year":
        bins = np.arange(0, 12 * 30 * 24 * 60 * 60 + 1, 30 * 24 * 60 * 60) + now_ts - 12 * 30 * 24 * 60 * 60

    else:
        raise ValueError(f"Unknown interval: {interval}")

    histogram, _ = np.histogram(visit_timestamps, bins=bins)
    return histogram.tolist()