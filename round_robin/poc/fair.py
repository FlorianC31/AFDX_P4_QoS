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
            yield (int(vl), int(burst_nb), int(nb_msg))

# sometimes py is kinda dumb
_next = next
def next(*a, **k):
    try:
        return _next(*a, **k)
    except StopIteration:
        return None

def with_sliding_win(filename):
    """
    count occurences (not only consecutives) of messages from each
    vls inside a sliding window which size is the sum of weights
    """
    # repartition[vl]: list of "run lengths" for vl
    repartition: 'dict[int, list[int]]' = {}
    WIN_SIZE, WIN_STEP = 3+5+7, 1
    wins = slice(WIN_SIZE)

    every = list(messages(filename))

    # until no message left
    for k in range(len(every)-WIN_SIZE):
        # window's content
        content = (vl for (vl, burst_nb, msg_nb) in every[wins])

        # count occurences of vl in content (of the window)
        for vl in content:
            lst = repartition.get(vl, [])
            if k < len(lst):
                lst[k]+= 1
            else:
                lst.append(1)
                assert k == len(lst)-1
            repartition[vl] = lst

        # slide window forward
        wins = slice(wins.start + WIN_STEP, wins.stop + WIN_STEP)

    show_repartition(repartition)

def with_run_length(filename):
    """
    simple process: count consecutives occurences of messages from
    the same vl; plots a bar plot with error bars of the resulting
    repartitions
    """
    # repartition[vl]: list of "run lengths" for vl
    repartition: 'dict[int, list[int]]' = {}
    curr_vl, run_length = None, 0

    one = messages(filename)
    anymore = None

    # until no message left
    while True:
        # until message form another vl or no message left
        while True:
            # fetch next one
            anymore = next(one)
            if not anymore: break
            (vl, burst_nb, msg_nb) = anymore

            # the very first iteration
            if None == curr_vl: curr_vl = vl

            # end of streak
            if curr_vl != vl:
                lst = repartition.get(curr_vl, [])
                lst.append(run_length)
                repartition[curr_vl] = lst
                curr_vl, run_length = vl, 1 # already 1 message
                break

            # continue streak
            else:
                run_length+= 1

        if not anymore: break

    show_repartition(repartition)

def show_repartition(repartition: 'dict[int, list[int]]'):
    import numpy as np
    import matplotlib.pyplot as plt

    # data structures for the plot
    names = []
    arrays = []
    means = []
    stds = []
    absc = []
    for (k, (vl, lst)) in enumerate(repartition.items()):
        names.append("VL " + str(vl))
        arrays.append(np.array(lst))
        means.append(np.mean(arrays[-1]))
        stds.append(np.std(arrays[-1]))
        absc.append(k)
        # print(vl, sum(lst), "/", len(lst), "=", sum(lst)/len(lst))

    # do the plot itself
    fig, ax = plt.subplots()
    ax.bar(absc, means, yerr=stds, align='center', alpha=.5, ecolor='black')
    ax.set_xticks(absc)
    ax.set_xticklabels(names)
    ax.yaxis.grid(True)
    plt.tight_layout()
    plt.show()

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

    with_run_length(file)
