import math

class CollisionManager:
    """Quản lý va chạm"""
    
    @staticmethod
    def point_to_line_distance(px, py, p1, p2):
        """Tính khoảng cách từ điểm đến đoạn thẳng"""
        x1, y1 = p1
        x2, y2 = p2
        line_len = math.hypot(x2 - x1, y2 - y1)
        
        if line_len == 0:
            return math.hypot(px - x1, py - y1)
        
        t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_len ** 2)
        t = max(0, min(1, t))
        
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        return math.hypot(px - proj_x, py - proj_y)
    
    @staticmethod
    def check_slice(objects, start_pos, end_pos, radius):
        """Kiểm tra vật thể có bị chém không"""
        sliced = []
        
        for obj in objects:
            dist = CollisionManager.point_to_line_distance(
                obj.x, obj.y, start_pos, end_pos
            )
            if dist < radius:
                sliced.append(obj)
        
        return sliced
