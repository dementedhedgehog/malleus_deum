"""
Used to parse image information from xml nodes

"""

class Img:

    def __init__(self):
        self.filename = None
        self.resource = None
        self.scale = None

        
    def parse(self, img_node):
        self.filename = img_node.get("src")
        self.resource_id = img.get("id")
        self.scale = img.get("scale", default=1.0)
        return

        
