import open_fortran_parser as ofp
import xml.etree.ElementTree as ET

class Argument:
    def __init__(self, name, ftype):
        self.name = name
        self.ftype = ftype

class Subroutine:
    # Subroutine name, subroutine arguments
    def __init__(self, name, *args):
        self.name = name
        self.args = list(args)

    @classmethod
    def from_root_xml_node(xml_node):
        

        return Subroutine()


def parse_subroutines(tree):
    print("Parsing subroutines...")

    subroutines = tree.findall("subroutine")
    for subroutine in subroutines:
        name = subroutine.attrib["name"]
        print("Found subroutine:", name)

    return []


def parse_functions(tree):
    return []

def make_f_interface_top(module_name):
    return ""

def make_f_interface_subroutines(subroutines):
    return ""

def make_f_interface_functions(functions):
    return ""


if __name__ == "__main__":
    tree = ofp.parse("example.F90")
    # print(ET.dump(tree))
    # TODO: Check there is only one? Is this needed?
    file = tree.find("file")

    subroutines = parse_subroutines(file)
    functions = parse_functions(file)

    # TODO: Parse from original module
    module_name = "example_interface"

    f_interface = ""
    f_interface += make_f_interface_top(module_name) 
    f_interface += make_f_interface_subroutines(subroutines)
    f_interface += make_f_interface_functions(functions)

