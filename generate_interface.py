import open_fortran_parser as ofp
import xml.etree.ElementTree as ET
from sys import argv

F_TO_C_TYPE = {
    "integer" : "integer(c_int)",
    "size_t"  : "integer(c_size_t)",    # CUSTOM - For array sizes
    "real"    : "real(c_double)",
    "logical" : "logical(c_bool)"
}

# header file types
# intent(x) determines const-ness
F_TO_C_H_TYPE = {
    "integer" : "int & ",
    "size_t"  : "size_t & ",
    "real"    : "double & ",
    "logical" : "bool & "
}

"""
Map type. If it is a derived/unknown type, assume there is some registry key for it.
"""
def f_to_c_type(inp):
    if inp in F_TO_C_TYPE:
        return F_TO_C_TYPE[inp], True
    else:
        return "c_key_" + inp, False

class Argument:
    def __init__(self, name, ftype, intent, dimensions = [], xml_declaration = None):
        self.xml_declaration = xml_declaration
        self.name = name
        self.ftype = ftype
        self.intent = intent
        self.dimensions = dimensions

    """
    Bool list of len(dimensions) which says if any of the args needs size
    """
    def needs_size_argument(self):
        dim_needs_arg = []
        for dim in self.dimensions:
            dim_needs_arg.append(dim == ":")
        print("NEEDS SIZE: ", dim_needs_arg)

        return dim_needs_arg

    def get_dim_string(self):
        out_str = ""
        if len(self.dimensions) > 0:
            out_str += "("
            idx = 0
            for dimension in self.dimensions:
                out_str += "%s" % dimension

                idx += 1
                if idx != len(self.dimensions):
                    out_str += ","
            out_str += ")"
        return out_str

    def to_f_interface_decl(self):
        # Turn into string
        f_c_type, is_in_map = f_to_c_type(self.ftype)
        out_str = f"{f_c_type}" + ", intent(" + self.intent + ") :: c_" + self.name
        out_str += self.get_dim_string()
        
        return out_str

    def __repr__(self):
        print_str = "{" + self.ftype + ", intent(" + self.intent + ") :: " + self.name
        print_str += self.get_dim_string()
        return print_str + "}"

class Subroutine:
    # Subroutine name, subroutine arguments
    # args = [arg1, arg2, ...]
    def __init__(self, root_xml, name, args):
        self.root_xml = root_xml
        self.name = name
        self.args = args

    def generate_f_interface_func(self, interface_prefix):
        # First check if any size arguments are needed.
        new_args = self.args
        for arg in self.args:
            print("DOING ARG: ", arg)
            needs_sizes = arg.needs_size_argument()
            if len(needs_sizes) == 1 and needs_sizes[0]:
                new_args.append(Argument(f"{arg.name}_size", "size_t", "in"))
            else:
                for idx, ns in enumerate(needs_sizes):
                    if ns:
                        new_args.append(Argument(f"{arg.name}_size{idx}", "size_t", "in"))

        out_str = f"subroutine {interface_prefix}_{self.name}_c("

        idx = 0
        for arg in new_args:
            out_str += "c_" + arg.name
            idx += 1
            if idx < len(new_args):
                out_str += ", "

        out_str += f""") &
    bind(c,name="{interface_prefix}_{self.name}_f90")

    use {interface_prefix}_mod, only: {self.name}
"""


        out_str += f"""
    implicit none
"""
        for arg in new_args:
            out_str += " "*4 + arg.to_f_interface_decl() + "\n"

        # Main body - call F function
        out_str += f"""
    call {self.name}()
"""        


        out_str += f"end subroutine {interface_prefix}_{self.name}_c"
        
        return new_args, out_str + "\n"*2


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

        return Argument(name, ftype_name, intent, dimensions_list, xml_declaration = declaration)
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

    return Subroutine(subroutine_tr, name, args)

def parse_subroutines(tree):
    print("Parsing subroutines...")
    return [subroutine_from_root_xml_node(sub) for sub in tree.findall("subroutine")]

def parse_functions(tree):
    return []

def make_f_interface_top(module_name):
    return ""

def make_f_interface_subroutines(interface_prefix, subroutines):
    out = ""
    for subroutine in subroutines:
        # TODO: re-use args for the c interface
        args, out_curr = subroutine.generate_f_interface_func(interface_prefix)
        out += out_curr

    return out

def make_f_interface_functions(functions):
    return ""


if __name__ == "__main__":
    filepath = str(argv[1])
    interface_prefix = str(argv[2])

    tree = ofp.parse(filepath)
    # print(ET.dump(tree))
    # TODO: Check there is only one? Is this needed?
    file = tree.find("file")

    subroutines = parse_subroutines(file)
    functions = parse_functions(file)

    # TODO: Parse from original module
    module_name = "example_interface"

    f_interface = ""
    f_interface += make_f_interface_top(module_name) 
    f_interface += make_f_interface_subroutines(interface_prefix, subroutines)
    f_interface += make_f_interface_functions(functions)

    print(f_interface)

