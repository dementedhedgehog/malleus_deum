
from utils import parse_xml



class Version:

    def __init__(self):
        self.major = None
        self.minor = None
        self.revision = None
        return

    def __str__(self):
        return "%s.%s.%s" % (self.major, self.minor, self.revision)

    @classmethod
    def load(cls, version_fname):
        doc = parse_xml(version_fname)        
        root = doc.getroot()        
        version = Version()
        
        for child in list(root):
           tag = child.tag

           if tag == "major":
               if version.major is not None:
                   raise Exception("Only one major per version. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   version.major = child.text.strip()
                   try:
                       version.major = int(version.major)
                   except ValueError:
                       raise Exception("Received invalid major version. (%s) expecting "
                                       "an integer\n" % child.tag)
           elif tag == "minor":
               if version.minor is not None:
                   raise Exception("Only one minor per version. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   version.minor = child.text.strip()
                   try:
                       version.minor = int(version.minor)
                   except ValueError:
                       raise Exception("Received invalid minor version. (%s) expecting "
                                       "an integer\n" % child.tag)
           elif tag == "revision":
               if version.revision is not None:
                   raise Exception("Only one revision per version. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   version.revision = child.text.strip()
                   try:
                       version.revision = int(version.revision)
                   except ValueError:
                       raise Exception("Received invalid revision version. (%s) expecting "
                                       "an integer\n" % child.tag)
           elif tag is COMMENT:
               # ignore comments!
               pass
           
           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, version_fname))           
        return version
        
