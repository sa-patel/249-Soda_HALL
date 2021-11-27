class Webcam:
    def get_static_data(self):
        """Get locations of tables and waypoints"""
        static_data = {
            "tables": [],
        }
        return static_data

    def get_data(self):
        """Get location and heading of kobukis"""
        data = {
            "kobuki1": {
                "x": 0,
                "y": 0,
                "heading": 0
            },
            "kobuki2": {
                "x": 0,
                "y": 0,
                "heading": 0
            }
        }
        return data
