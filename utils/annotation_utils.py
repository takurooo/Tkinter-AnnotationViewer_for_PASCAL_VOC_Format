#------------------------------------------------------
# import
#------------------------------------------------------
import os
import glob
import xml.dom.minidom
from xml.etree import ElementTree
import numpy as np



#------------------------------------------------------
# function
#------------------------------------------------------
class PascalVOC_Writer(object):

    def __init__(self, dir=os.getcwd()):
        self.dir = dir

    def _append_child(self, newdoc, parent, child, value=None):

        if value is not None:
            if not isinstance(value, str):
                value = str(value)
            child.appendChild(newdoc.createTextNode(value))
        parent.appendChild(child)


    def write(self, fname, size, classes, boxes):
        width, height, depth = size

        newdoc = xml.dom.minidom.Document()

        elm_annotation = newdoc.createElement('annotaion')
        self._append_child(newdoc, newdoc, elm_annotation)

        self._append_child(newdoc, elm_annotation, newdoc.createElement('filename'), fname)

        elm_size = newdoc.createElement('size')
        self._append_child(newdoc, elm_annotation, elm_size)

        self._append_child(newdoc, elm_size, newdoc.createElement('depth'), depth)
        self._append_child(newdoc, elm_size, newdoc.createElement('width'), width)
        self._append_child(newdoc, elm_size, newdoc.createElement('height'), height)

        for classname, box in zip(classes, boxes):
            xmin, ymin, xmax, ymax = box
            elm_object = newdoc.createElement('object')
            self._append_child(newdoc, elm_annotation, elm_object)

            self._append_child(newdoc, elm_object, newdoc.createElement('name'), classname)
            self._append_child(newdoc, elm_object, newdoc.createElement('pose'), 'Unspecified')

            elm_bndbox= newdoc.createElement('bndbox')
            self._append_child(newdoc, elm_object, elm_bndbox)

            self._append_child(newdoc, elm_bndbox, newdoc.createElement('xmin'), xmin)
            self._append_child(newdoc, elm_bndbox, newdoc.createElement('ymin'), ymin)
            self._append_child(newdoc, elm_bndbox, newdoc.createElement('xmax'), xmax)
            self._append_child(newdoc, elm_bndbox, newdoc.createElement('ymax'), ymax)


        voc_xml = newdoc.toprettyxml()
        out_path = os.path.join(self.dir, fname+'.xml')

        with open(os.path.join(self.dir, fname+'.xml'), 'w') as f:
            f.write(voc_xml)


class PascalVoc_Object(object):

    def __init__(self, classname=None, pose=None, box=None):
        self.classname = classname
        self.pose = pose
        self.box = box

class PascalVOC_Reader(object):

    def __init__(self, dir=os.getcwd()):
        self.dir = dir
        self.data = dict()
        self._parse()

    def _parse(self):
        fnames = glob.glob(os.path.join(self.dir, '*.xml'))
        for fname in fnames:
            tree = ElementTree.parse(fname)
            root = tree.getroot()
            size_tree = root.find('size')
            width = float(size_tree.find('width').text)
            height = float(size_tree.find('height').text)
            objects = []
            for object_tree in root.findall('object'):
                for bbox in object_tree.iter('bndbox'):
                    xmin = float(bbox.find('xmin').text)/width
                    ymin = float(bbox.find('ymin').text)/height
                    xmax = float(bbox.find('xmax').text)/width
                    ymax = float(bbox.find('ymax').text)/height
                bbox = [xmin, ymin, xmax, ymax]
                class_name = object_tree.find('name').text
                pose = object_tree.find('pose').text

                objects.append(PascalVoc_Object(class_name, pose, bbox))

            image_name = root.find('filename').text
            self.data[image_name] = objects

    def read(self):
        return self.data


#------------------------------------------------------
# main
#------------------------------------------------------
if __name__ == '__main__':
    dir = os.getcwd()

    fname = 'fname_0'
    size = [640, 460, 3]
    classes = ['dog', 'cat', 'fish']
    boxes = [[1,2,3,4], [10,20,30,40], [100,200,300,400]]

    writer = PascalVOC_Writer(dir)
    writer.write(fname, size, classes, boxes)

    voc_annotations = PascalVOC_Reader(dir).read()

    for fname, objects in voc_annotations.items():
        print(fname)
        for object in objects:
            print("classname : ", object.classname)
            print("pose      : ", object.pose)
            print("box       : ", object.box)
