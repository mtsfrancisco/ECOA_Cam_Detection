import math

class Tracker:
    def __init__(self):
        self.center_points = {}
        self.id_count = 0

    def update(self, objects_rect):
        """
        Receives a list of rectangles (x, y, w, h)
        and assigns IDs to each rectangle according to position.
        """
        objects_bbs_ids = []

        # For each bounding box, we calculate the center (cx, cy)
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # Checks if there is already an object close to this center
            same_object_detected = False
            for obj_id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])
                if dist < 35:
                    # It's the same object, updates position
                    self.center_points[obj_id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, obj_id])
                    same_object_detected = True
                    break

            # If it didn't find an object nearby, it creates a new ID
            if not same_object_detected:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        # Remove IDs that have not been updated in this frame
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        self.center_points = new_center_points.copy()

        return objects_bbs_ids
