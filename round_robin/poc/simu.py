#!/usr/bin/env python3

settings = {}
def default_settings():
    """ sets up default settings, see __main__ at file bottom """
    settings['tested_switches'] = [DumbSwitch, TrueRRSwitch, PseudoRRSwitch]

    # VL are from 0 to this excluded
    settings['nb_vl'] = 3

    # settings for the SP-RR (`PseudoRR` class)
    if True:
        # 3 VLs (0..2), each can send 1 packets before rr-ing to next
        settings['VL_N'] = [
            1,
            1,
            1,
        ]
        # 8 out- priority queues
        settings['NB_Q'] = 8

    # messages from the same VL have same color
    settings['colors'] = False

    # rng seed
    settings['seed'] = None
    # how many messages in total
    settings['count'] = 42
    # span for burst random sizes
    settings['burst-range'] = (3, 10)
    # span for after burst transmition
    settings['trsmit-range'] = (10, 11)

class Msg:
    class StdMeta:
        def __init__(self):
            self.prio = 0
    def __init__(self, vl: int, data: str):
        self.vl = vl
        self.data = data
        self.std_meta = Msg.StdMeta()
    def __str__(self):
        return (settings['colors']
            and f"\x1b[{31+self.vl}m%s (%s)\x1b[m"
            or "%s (%s)"
        ) % (self.vl, self.data)

#---

class Switch:
    """ abstract base class """
    def incoming(self, msg: Msg): "abstract public, receives a message"
    def outgoing(self) -> Msg: "abstract public, sends a pending message"
    #def _ingress(self, msg: Msg): "abstract private"
    #def _egress(self, msg: Msg): "abstract private"

class DumbSwitch(Switch):
    """ sends the message in the order they are received """
    def __init__(self):
        self.infinit_queue = []
    def incoming(self, msg: Msg):
        self.infinit_queue.append(msg)
    def outgoing(self) -> Msg:
        return self.infinit_queue.pop(0) if self.infinit_queue else None

class TrueRRSwitch(Switch):
    """ correct (maybe) implementation of the round robin """
    def __init__(self):
        self.msg_per_vl = [[] for _ in range(settings['nb_vl'])]
        self.current_holder = 0
        self.current_holder_left = settings['VL_N'][self.current_holder]

    def incoming(self, msg: Msg):
        self.msg_per_vl[msg.vl].append(msg)

    def outgoing(self) -> Msg:
        next_one = (self.current_holder + 1) % settings['nb_vl']

        #  credit used                  or no more message to send
        if 0 == self.current_holder_left or not self.msg_per_vl[self.current_holder]:
            # next one
            self.current_holder = next_one
            self.current_holder_left = settings['VL_N'][self.current_holder]

        # if message to send
        if self.msg_per_vl[self.current_holder]:
            # use credit
            self.current_holder_left-= 1
            return self.msg_per_vl[self.current_holder].pop(0)

        # else, need to check for every other list in order,
        # starting from after current and excluding current
        in_order = self.msg_per_vl[next_one:] \
                + self.msg_per_vl[:self.current_holder]
        for other_lst in in_order:
            # if did find a non empty list of pending message(s)
            if other_lst:
                return self.outgoing() # lazy solution :/

        # no message to send at all
        return None

class PseudoRRSwitch(Switch):
    """ rr approximation with static priority queues """
    def __init__(self):
        # usage[vl][q]: usage for vl on queue q
        self.usage = [
            [0 for _ in range(settings['NB_Q'])]
            for __ in settings['VL_N']
        ]
        # queues locals to the switch
        self.queues: 'list[list[Msg]]' = [[] for _ in range(settings['NB_Q'])]

    def __repr__(self):
        """ /!\\ for debug purpose """
        head = "    "
        body = [f"{q: 3} " for q in range(settings['NB_Q'])]

        for (vl, can) in enumerate(settings['VL_N']):
            head+= f"| {vl: 3} "
            for q in range(settings['NB_Q']):
                body[q]+= f"| {self.usage[vl][q]}/{can} "

        for q in range(settings['NB_Q']):
            body[q]+= "  ["
            body[q]+= ", ".join(str(msg.vl) for msg in self.queues[q])
            body[q]+= "]"

        sep = "\n" + "-"*len(head) + "\n"
        table = head + sep + sep.join(body)

        return f"PseudoRR switch, usage:\n{table}"

    def incoming(self, msg: Msg):
        self._ingress(msg)
        p = msg.std_meta.prio
        assert -1 < p < settings['NB_Q']
        self.queues[p].append(msg)

    def outgoing(self) -> Msg:
        # find first non empty queue by order of decreasing priority
        for queue in self.queues:
            if queue:
                msg = queue.pop(0)
                self._egress(msg)
                return msg
        # no message pending
        return None

    def _ingress(self, msg: Msg):
        """
        finds the first queue that has room (usage not maxed out)
        for the incoming message;
        if find then use, if not find then panic
        """
        for q in range(settings['NB_Q']):
            if self.usage[msg.vl][q] < settings['VL_N'][msg.vl]:
                # count = sum(1
                #     for mate in self.queues[q]
                #     if msg.vl == mate.vl
                # )
                # assert count == self.usage[msg.vl][q], f"{count} == {self.usage[msg.vl][q]}"
                # can here, use 1 on this queue
                self.usage[msg.vl][q]+= 1
                msg.std_meta.prio = q
                return
            # cannot here, try next
            continue

        # could not, multiple behavior may be fdbsfbds

        # panic (initial implementation)
        #assert False

        # enabling over-usage of the last queue
        # (trades fairness for preserved packet ordering)
        self.usage[msg.vl][q]+= 1
        msg.std_meta.prio = q

        # cycle to first priority queue
        # (does not assume on the queues' capacities,
        # but loses packet ordering to /try/ to keep a
        # rr- fairness)
        #self._egress(msg, turn+1)
        # `turn` as a parameter (default value 1) would multiply
        # `usage` in the comparison inside the `for` above
        # easiest way to implement in p4 /might/ be recirculate
        # or something

    def _egress(self, msg: Msg):
        """
        only decrease this's usage in queue if no message after
        ie if this's usage in below queue is none;
        if from that, usage in queue is now none, this was the tail
        ie reset every usage in queues above
        """
        assert 0 < self.usage[msg.vl][msg.std_meta.prio]

        # 'below' as in priority-wise
        below = msg.std_meta.prio + 1

        # if this is already the least prio queue (nothing below)
        if below == settings['NB_Q']:
            # is tail, check, free 1 on it
            self.usage[msg.vl][msg.std_meta.prio]-= 1

            # was the last pending message, reset
            if 0 == self.usage[msg.vl][msg.std_meta.prio]:
                for above in range(msg.std_meta.prio):
                    self.usage[msg.vl][above] = 0
            return

        # else if this is any other queue but the last one
        if 0 == self.usage[msg.vl][below]:
            # is tail, free 1 on this queue
            self.usage[msg.vl][msg.std_meta.prio]-= 1

            # was the last pending message, reset
            if 0 == self.usage[msg.vl][msg.std_meta.prio]:
                for above in range(msg.std_meta.prio):
                    self.usage[msg.vl][above] = 0

# ---

def simulate(switch: Switch, msg_bursts: 'list[tuple[list[Msg], int]]',
        send_msg):
    """
    msg_busts should be a list of (list of message, integer); each of
            these represent a burst of messages arriving at once
            and how many message it has time to process before next
            burst (if any)

    send_msg is the callback for when a message would be emitted; it
            takes a single parameter which is the message itself

    rec_msg is an optional callback used to signal that a message is
            received and enters the processing chain

    will always send every messages through send_msg
    """
    # process each burst of messages described
    for (burst, can) in msg_bursts:
        # process messages as they come (all at once; no sending yet)
        for msg in burst:
            switch.incoming(msg)

        # send messages between two busts (in the resulting order)
        for _ in range(can):
            msg = switch.outgoing()
            # (avoid sending 'None's when no messages left)
            if not msg: break
            send_msg(msg)

    # send remaining messages
    while True:
        msg = switch.outgoing()
        if not msg: break
        send_msg(msg)

    # any final word?
    #print(switch)

def generate(msg_count: int, burst_range: 'tuple[int, int]',
        trsmit_range: 'tuple[int, int]', seed: int=None):
    """
    generates a random amount of messages
    grouped in randomly sized and spaced bursts

    data is <burst number> "-" <message number> "-" <random>

    returns an iterable
    """
    from random import randrange, seed as randseed
    if seed:
        randseed(seed)

    burst_k = 0
    data = (
        "%02d-%03d-%d" % (burst_k, k, randrange(10, 100))
        for k in range(msg_count)
    )
    while msg_count:
        # how many in this burst
        many = min(randrange(*burst_range), msg_count)
        # how many can be transmited before next burst
        trsmit = randrange(*trsmit_range)

        yield ([
                Msg(randrange(settings['nb_vl']), next(data))
                for _ in range(many)
            ], trsmit)

        msg_count-= many
        burst_k+= 1

if '__main__' == __name__:
    from sys import argv, stdout, stderr

    default_settings()

    prog = argv.pop(0)
    if "-h" in argv:
        from os import path
        prog = path.basename(prog)
        print(f"""Usage: {prog} [--rr <comma separated>] [--count <n>]
       {" "*len(prog)} [--rnd-range <mi> <ma>]
       {" "*len(prog)} [--seed <s>] [--colors]

  --rr            list VL_N to use eg. `--rr '1,1,1'`     (def.)
  --count         how many messages to generate           (def. 42)
  --burst-range   range for the size of the bursts        (def. 3 10)
  --trsmit-range  range for the transmition after bursts  (def. 10 11)
  --seed          the seed for the random generation      (def. random)
  --colors        (tries with) enables colors             (def. disabled)
  --save-files    saves results to .txt files             (def. disabled)

  Compare {len(settings['tested_switches'])} different switch implementations:
   - {(chr(10)+"   - ").join(
       swit.__name__ + ": " + (swit.__doc__ or "").strip()
       for swit in settings['tested_switches']
    )}
""", file=stderr)
        exit(1)

    while argv:
        arg = argv.pop(0)
        if "--rr" == arg:
            settings['VL_N'] = [
                int(it)
                for it in argv.pop(0).split(",")
            ]
        elif "--count" == arg:
            settings['count'] = int(argv.pop(0))
        elif "--burst-range" == arg:
            settings['burst-range'] = (int(argv.pop(0)), int(argv.pop(0)))
        elif "--trsmit-range" == arg:
            settings['trsmit-range'] = (int(argv.pop(0)), int(argv.pop(0)))
        elif "--seed" == arg:
            settings['seed'] = int(argv.pop(0))
        elif "--colors" == arg:
            settings['colors'] = True
            from os import system; system("") # (Windows)
        elif "--save-files" == arg:
            settings['save-files'] = True
        else:
            print(f"Unknown argument: '{arg}'", file=stderr)
            exit(1)

    # same traffic for each simulation
    msgs = list(generate(
        settings['count'],
        settings['burst-range'],
        settings['trsmit-range'],
        settings['seed']
    ))
    for Swit in settings['tested_switches']:
        # resulting order after passing through the switch
        ordered = []

        # (work off a copy of `msgs`, just in case)
        simulate(Swit(), list(msgs), lambda msg: ordered.append(msg))

        dropped = settings['count']-len(ordered) # if maybe for some reason..

        if settings['save-files']:
            out = open(Swit.__name__ + ".txt", 'wt')
        else:
            out = stdout
        print("with", Swit.__name__, file=out)
        print("resulting order:", end=" ", file=out)
        print("("+str(len(ordered)), "messages", dropped, "dropped)", file=out)
        print("\t" + "\n\t".join(str(msg) for msg in ordered), file=out)
