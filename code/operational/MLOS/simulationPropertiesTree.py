#!/usr/bin/env python
#-*-coding: utf8 -*-

""" That file contain material to parse a DART simulation.properties file and
convert it to a xml.etree.ElementTree object in the aim to view it in graphical
application.
"""

import xml.etree.ElementTree as ET
import os, sys

__author__ = "GREGOIRE Tristan"
__version__ = "1.0"

class Key(ET.Element):
    """ Inherit from the xml.etree.ElementTree.Element object and add a usefull
        method to parse path from a text line (parse_text)
        This class also add three attribut (path, tag and value) from the
        parse_text method.
    """

    def __init__(self, text):
        ## Get path, tag and value
        self.path, tag, value = self.parse_text(text)

        ## Init ET.Element
        ET.Element.__init__(self, tag, value=value)

    def parse_text(self, text):
        """ Parse from DART simulation properties text line (text) and return
            a valid path, a tag and a value
        """
        ## Get full path and value
        path, value = text.split(':')

        ## Convert path
        path = path.replace('.', '/')

        ## Get tag (last element of path)
        tag = os.path.basename(os.path.normpath(path))
        
        ## Remove tag in path
        path = os.path.dirname(path)

        ## Return
        return path, tag, value
        

class SimulationProperties(ET.ElementTree):
    """ Inherit from xml.etree.ElementTree.ElementTree object and implements
        specific methods and attributs for DART simulation.properties case.

        It load an entire ElementTree from a given DART simulation.properties
        file thanks to the load_element_from_file method and the Key class.

        It also implement two usefull atributs:
            - parent_map: A simple dictionaray that allow one to get parent 
                          from a child element in the Tree
            - element_list: A simple list wihtin all the different elements in
                            the tree.
    """
    def __init__(self, filename, simulation_name="Simulation"):
        ## String to by displayed in case of error
        self.errorStr = ""

        ## Create root element
        ET.ElementTree.__init__(self, ET.Element(simulation_name))

        ## Generate the whole tree from filename
        self.load_element_from_file(filename)
        
        ## Map child->parent dictionary
        self.parent_map = dict((c, p) for p in self.getiterator() for c in p)

        ## List of all the element in the tree
        self.element_list = list(set(
            [ elem.tag for elem in self.getiterator() ]))

    def load_element_from_file(self, filename):
        """ Load the whole ElementTree from a file (filename) using the Key 
            class.
        """
        ## Read file
        with open(filename, 'r') as fstream:
            lines = fstream.readlines()
            fstream.close()
            
        ## Remove '\n'
        lines = [ line.strip("\n") for line in lines ]

        ## Loop over
        for line in lines:
            ## Create key
            try:
                key = Key(line)
            except ValueError as e:
                print sys.stderr.write("Warning: simulation.properties file is inconsistent, at line {line}\n".format(line=line))
                self.errorStr = "Warning: simulation.properties file is inconsistent"

            ## Get node where to insert key
            node = self._root.find(key.path)
            
            ## Check if node exist
            if node == None:
                node = self.create_path(key.path)

            ## Add key in Tree
            node.append(key)

    def create_path(self, path):
        """ Create a given path in the Tree if not already exist.
        """
        ## Init node from _root
        node = self._root

        ## Walk in path from begining to end
        for p in path.split('/'):
            if node.find(p) == None:
                node.append(ET.Element(p))
            node = node.find(p)

        ## Return 
        return node

    def getElementList(self):
        """ Return the element_list attribut
        """
        return self.element_list

if __name__ == "__main__":
    tree = SimulationProperties("simulation.properties.txt")
    tree.write("outout.xml")
