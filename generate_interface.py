from open_fortran_parser import parse

if __name__ == "__main__":
    xml = parse("example.F90", verbosity=0)
    print(type(xml))
