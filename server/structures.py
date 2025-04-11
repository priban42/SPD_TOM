from utils import parse_svg_toilets
import numpy as np
import os

class Building:
    def __init__(self, name, events):
        self.name = name
        self.floors = {}
        self.events = events
        for floor_name in os.listdir("static"):
            if floor_name[:len(name)] == name:
                self.floors[floor_name[:-4]] = Floor(self, floor_name[:-4])

    def __getitem__(self, key):
        return self.floors[key]

    def __iter__(self):
        for floor_name in self.floors:
            yield self.floors[floor_name]

    def refresh_data(self):
        for floor in self:
            floor.refresh_data()

class Floor:
    def __init__(self, parent:Building, name: str) -> None:
        self.name = name
        self.svg_path = 'static/' + self.name + ".svg"
        self.parent = parent
        self.toilets = {}
        self._load_toilets()

    def __getitem__(self, key):
        return self.toilets[key]

    def __iter__(self):
        for toilet_name in self.toilets:
            yield self.toilets[toilet_name]

    def _load_toilets(self):
        self.toilets = {}
        toilets_dict = parse_svg_toilets(self.svg_path)
        for toilet_name in toilets_dict:
            self.toilets[toilet_name] = Toilet(self,
                                               toilet_name,
                                               toilets_dict[toilet_name]["width"],
                                               toilets_dict[toilet_name]["height"],
                                               toilets_dict[toilet_name]["x"],
                                               toilets_dict[toilet_name]["y"],
                                               toilets_dict[toilet_name]["gender"],
                                               toilets_dict[toilet_name]["stall_count"])
    def refresh_data(self):
        for toilet in self:
            toilet.refresh_data()


class Toilet:
    def __init__(self, parent: Floor, name: str, width: float, height: float, x: float, y: float, gender: str, stall_count: int) -> None:
        self.parent = parent
        self.name = name
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.gender = gender
        self.stall_count = stall_count
        self.visits = None
        self.visit_time = None
        self.visit_timestamps = None
        self.visit_durations = None
        self.stalls = []
        self._load_stalls()

    def __getitem__(self, key):
        return self.stalls[key]

    def __iter__(self):
        for stall in self.stalls:
            yield stall

    def _load_stalls(self):
        self.stalls = []
        for i in range(self.stall_count):
            self.stalls.append(Stall(self, i))

    def refresh_data(self):
        self.visits = 0
        self.visit_time = 0
        self.visit_timestamps = np.array([], dtype=np.int64)
        self.visit_durations = np.array([], dtype=np.int64)
        for stall in self:
            stall.refresh_data()
            self.visits += stall.visits
            self.visit_time += stall.visit_time
            self.visit_timestamps = np.hstack((self.visit_timestamps, stall.visit_timestamps))
            self.visit_durations = np.hstack((self.visit_durations, stall.visit_durations))


class Stall:
    def __init__(self, parent: Toilet, id: int) -> None:
        self.parent = parent
        self.id = id
        self.timestamps = None
        self.visit_timestamps = None
        self.visit_durations = None
        self.visits = None
        self.visit_time = None

    def get_timestamps(self):
        events = self.parent.parent.parent.events.query.filter_by(node_id=self.parent.name, stall_id=self.id).all()
        event_timestamps = np.zeros((len(events), 2), dtype=np.int64)
        for i in range(len(events)):
            event_timestamps[i, 0] = events[i].timestamp
            event_timestamps[i, 1] = events[i].event_type
        return event_timestamps

    @staticmethod
    def compute_stats(timestamps):
        last_state = 1
        detected = False
        door_closed_ts = None
        visit_timestamps = []
        visit_durations = []
        for i in range(timestamps.shape[0]):
            state = timestamps[i, 1]
            if state == 1 and detected and last_state == 0:
                visit_timestamps.append(door_closed_ts)
                visit_durations.append(timestamps[i, 0] - door_closed_ts)
                detected = False
                door_closed_ts = None
                last_state = 1
            if state == 0:
                detected = False
                last_state = 0
                door_closed_ts = timestamps[i, 0]
            if state == 2:
                detected = True
        return [np.array(visit_timestamps, dtype=np.int64), np.array(visit_durations, dtype=np.int64)]

    def refresh_data(self):
        self.timestamps = self.get_timestamps()
        self.visit_timestamps, self.visit_durations = self.compute_stats(self.timestamps)
        self.visits = len(self.visit_timestamps)
        self.visit_time = np.sum(self.visit_durations)