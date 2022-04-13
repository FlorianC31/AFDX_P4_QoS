#!/usr/bin/env python3

def messages(filename):
    with open(filename, 'rt') as file:
        (_, sw_name) = file.readline().split() # "with <sw-name>"
        file.readline() # "resulting order: .."

        for line in file.readlines():
            line = line.strip()
            if not line or line.startswith("#"): continue
            (vl, data) = line.split()
            (burst_nb, nb_msg, rnd) = data.strip("()").split("-")
            yield (vl, burst_nb, nb_msg)

def process(filename):
    for vl, burst_nb, msg_nb in messages(filename):
        print(vl, burst_nb, msg_nb)

if True:
    from sys import argv, stderr

    prog = argv.pop(0)
    if not len(argv) or "-h" == argv[0]:
        from os import path
        prog = path.basename(prog)
        print(f"""Usage: {prog} <file>

  "Analyse" "fairness" for the given file; its format should be:

        with <sw-name>
        resulting order: (<total-msg-count>)
        \t<msg>
        \t<msg>
        \t..

        with <msg> a <vl> (<data>)
        and <data> a <msg-nb>-<burst-nb>-<rnd>
""", file=stderr)
        exit(2)

    file = argv[0]

    process(file)
