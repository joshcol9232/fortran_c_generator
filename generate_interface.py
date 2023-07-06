import open_fortran_parser as ofp
import xml.etree.ElementTree as ET


def dimensions_list_from_root_xml_node(dimensions):
    dimensions_list = []
    for dimension in dimensions.findall("dimension"):
        arg_dim_type = dimension.attrib["type"]
        if arg_dim_type == "assumed-shape":
            dimensions_list.append(":")
        elif arg_dim_type == "simple":
            dimensions_list.append(dimension.find("literal").attrib["value"])
        else:
            raise ValueError("'%s' arg dimensions not accounted for." % arg_dim_type)

    return dimensions_list

class Argument:
    def __init__(self, name, ftype, intent, dimensions = None):
        self.name = name
        self.ftype = ftype
        self.intent = intent
        self.dimensions = dimensions

    def __repr__(self):
        print_str = "{" + self.ftype + ", intent(" + self.intent + ") :: " + self.name
        
        if len(self.dimensions) > 0:
            print_str += "("
            idx = 0
            for dimension in self.dimensions:
                print_str += "%s" % dimension

                idx += 1
                if idx != len(self.dimensions):
                    print_str += ","
            print_str += ")"

        return print_str + "}"

class Subroutine:
    # Subroutine name, subroutine arguments
    # args = [arg1, arg2, ...]
    def __init__(self, name, args):
        self.name = name
        self.args = args

def argument_from_declaration_root_xml_node(declaration):
    intent_tr = declaration.find("intent")
    if intent_tr:
        # Must be a dummy argument
        intent = intent_tr.attrib["type"]
        ftype_name = declaration.find("type").attrib["name"]

        # WARNING: Assuming one variable per declaration
        variable = declaration.find("variables").findall("variable")[0]
        name = variable.attrib["name"]

        dimensions_list = []
        dimensions = variable.find("dimensions")
        if dimensions:
            dimensions_list = dimensions_list_from_root_xml_node(dimensions)

        return Argument(name, ftype_name, intent, dimensions_list)
    else:
        return None

def subroutine_from_root_xml_node(subroutine_tr):
    name = subroutine_tr.attrib["name"]
    print("Found subroutine:", name)
    # Fetch arguments

    body_specification = subroutine_tr.find("body").find("specification")
    args = []
    for decl in body_specification.findall("declaration"):
        arg = argument_from_declaration_root_xml_node(decl)
        if arg:
            args.append(arg)

    print(args)

    return Subroutine(name, args)

def parse_subroutines(tree):
    print("Parsing subroutines...")
    return [subroutine_from_root_xml_node(sub) for sub in tree.findall("subroutine")]

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
    print(ET.dump(tree))
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

