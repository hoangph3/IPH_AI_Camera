import math

def on_segment(p, q, r):
    return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
            q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))


def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0  # Collinear
    return 1 if val > 0 else 2  # Clockwise or Counterclockwise


def do_intersect(p1, q1, p2, q2):
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if o1 != o2 and o3 != o4:
        return True

    # Special cases
    if o1 == 0 and on_segment(p1, p2, q1):
        return True
    if o2 == 0 and on_segment(p1, q2, q1):
        return True
    if o3 == 0 and on_segment(p2, p1, q2):
        return True
    if o4 == 0 and on_segment(p2, q1, q2):
        return True

    return False


def box_line_intersection(box, line):
    """Check if a bounding box intersects with a line."""
    x1, y1, x2, y2 = box
    x3, y3, x4, y4 = line

    # Check if any of the box edges intersect with the line
    if (do_intersect((x1, y1), (x2, y1), (x3, y3), (x4, y4)) or
            do_intersect((x2, y1), (x2, y2), (x3, y3), (x4, y4)) or
            do_intersect((x2, y2), (x1, y2), (x3, y3), (x4, y4)) or
            do_intersect((x1, y2), (x1, y1), (x3, y3), (x4, y4))):
        return True

    return False


def line_intersection_half(line, bbox):
    x1, y1, x2, y2 = bbox
    x3, y3, x4, y4 = line

    m_line = (y4 - y3) / (x4 - x3) if (x4 - x3) != 0 else float('inf')
    x_intersect = (m_line * x3 - (y1 - y3)) / (m_line - (y2 - y1) / (x2 - x1))
    y_intersect = m_line * (x_intersect - x3) + y3

    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2

    if y_intersect <= mid_y:
        res = "Up"
    else:
        res = "Down"
    return res


def halve_bbox_y(bbox):
    x1, y1, x2, y2 = bbox
    mid_y = (y1 + y2) / 2

    upper_half_bbox = (x1, mid_y, x2, y2)
    lower_half_bbox = (x1, y1, x2, mid_y)

    return upper_half_bbox, lower_half_bbox


def get_centroid(bbox):
    x1, y1, x2, y2 = bbox
    centroid_x = (x1 + x2) / 2
    centroid_y = (y1 + y2) / 2
    return centroid_x, centroid_y

def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculate_perpendicular_point(centroid, line):
    x_c, y_c = centroid
    x1, y1, x2, y2 = line

    m_line = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else float('inf')

    m_perpendicular = -1 / m_line if m_line != 0 else float('inf')

    x_intersect = (m_line * x1 - m_perpendicular * x_c + y_c - y1) / (m_line - m_perpendicular)
    y_intersect = m_perpendicular * (x_intersect - x_c) + y_c

    return x_intersect, y_intersect