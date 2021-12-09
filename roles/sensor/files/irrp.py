#!/usr/bin/env python3

import time
import json
import os
import argparse

import pigpio  # http://abyz.co.uk/rpi/pigpio/python.html


last_tick = 0
in_code = False
code = []
fetching_code = False


class IRRemoteControl:

    @staticmethod
    def backup(f):
        """
        f -> f.bak -> f.bak1 -> f.bak2
        """
        try:
            os.rename(os.path.realpath(f)+".bak1", os.path.realpath(f)+".bak2")
        except:
            pass
        try:
            os.rename(os.path.realpath(f)+".bak", os.path.realpath(f)+".bak1")
        except:
            pass
        try:
            os.rename(os.path.realpath(f), os.path.realpath(f)+".bak")
        except:
            pass

    @staticmethod
    def carrier(gpio, frequency, micros):
        """
        Generate carrier square wave.
        """
        wf = []
        cycle = 1000.0 / frequency
        cycles = int(round(micros/cycle))
        on = int(round(cycle / 2.0))
        sofar = 0
        for c in range(cycles):
            target = int(round((c+1)*cycle))
            sofar += on
            off = target - sofar
            sofar += off
            wf.append(pigpio.pulse(1 << gpio, 0, on))
            wf.append(pigpio.pulse(0, 1 << gpio, off))
        return wf

    def __init__(self, args):
        self.GPIO = args.gpio
        self.FILE = args.file
        self.GLITCH = args.glitch
        self.PRE_MS = args.pre
        self.POST_MS = args.post
        self.FREQ = args.freq
        self.VERBOSE = args.verbose
        self.SHORT = args.short
        self.GAP_MS = args.gap
        self.NO_CONFIRM = args.no_confirm
        self.TOLERANCE = args.tolerance
        self.POST_US = self.POST_MS * 1000
        self.PRE_US = self.PRE_MS * 1000
        self.GAP_S = self.GAP_MS / 1000.0
        self.CONFIRM = not self.NO_CONFIRM
        self.TOLER_MIN = (100 - self.TOLERANCE) / 100.0
        self.TOLER_MAX = (100 + self.TOLERANCE) / 100.0
        # instance
        self.pi = pigpio.pi()  # Connect to Pi.

    def __del__(self):
        if self.is_connected():
            self.pi.stop()  # Disconnect from Pi.

    def is_connected(self):
        if not self.pi.connected:
            exit(0)

    def normalise(self, c):
        """
        Typically a code will be made up of two or three distinct
        marks (carrier) and spaces (no carrier) of different lengths.
        Because of transmission and reception errors those pulses
        which should all be x micros long will have a variance around x.
        This function identifies the distinct pulses and takes the
        average of the lengths making up each distinct pulse.  Marks
        and spaces are processed separately.
        This makes the eventual generation of waves much more efficient.

        Input

        M    S   M   S   M   S   M    S   M    S   M
        9000 4500 600 540 620 560 590 1660 620 1690 615

        Distinct marks

        9000                average 9000
        600 620 590 620 615 average  609

        Distinct spaces

        4500                average 4500
        540 560             average  550
        1660 1690           average 1675

        Output

        M    S   M   S   M   S   M    S   M    S   M
        9000 4500 609 550 609 550 609 1675 609 1675 609
        """
        if self.VERBOSE:
            print("before normalise", c)
        entries = len(c)
        p = [0]*entries  # Set all entries not processed.
        for i in range(entries):
            if not p[i]:  # Not processed?
                v = c[i]
                tot = v
                similar = 1.0
                # Find all pulses with similar lengths to the start pulse.
                for j in range(i+2, entries, 2):
                    if not p[j]:  # Unprocessed.
                        # Similar.
                        if (c[j]*self.TOLER_MIN) < v < (c[j]*self.TOLER_MAX):
                            tot = tot + c[j]
                            similar += 1.0
                # Calculate the average pulse length.
                newv = round(tot / similar, 2)
                c[i] = newv
                # Set all similar pulses to the average value.
                for j in range(i+2, entries, 2):
                    if not p[j]:  # Unprocessed.
                        # Similar.
                        if (c[j]*self.TOLER_MIN) < v < (c[j]*self.TOLER_MAX):
                            c[j] = newv
                            p[j] = 1
        if self.VERBOSE:
            print("after normalise", c)

    def compare(self, p1, p2):
        """
        Check that both recodings correspond in pulse length to within
        TOLERANCE%.  If they do average the two recordings pulse lengths.

        Input

            M    S   M   S   M   S   M    S   M    S   M
        1: 9000 4500 600 560 600 560 600 1700 600 1700 600
        2: 9020 4570 590 550 590 550 590 1640 590 1640 590

        Output

        A: 9010 4535 595 555 595 555 595 1670 595 1670 595
        """
        if len(p1) != len(p2):
            return False
        for i in range(len(p1)):
            v = p1[i] / p2[i]
            if (v < self.TOLER_MIN) or (v > self.TOLER_MAX):
                return False
        for i in range(len(p1)):
            p1[i] = int(round((p1[i]+p2[i])/2.0))
        if self.VERBOSE:
            print("after compare", p1)
        return True

    def tidy_mark_space(self, records, base):
        ms = {}
        # Find all the unique marks (base=0) or spaces (base=1)
        # and count the number of times they appear,
        for rec in records:
            rl = len(records[rec])
            for i in range(base, rl, 2):
                if records[rec][i] in ms:
                    ms[records[rec][i]] += 1
                else:
                    ms[records[rec][i]] = 1
        if self.VERBOSE:
            print("t_m_s A", ms)

        v = None
        for plen in sorted(ms):
            # Now go through in order, shortest first, and collapse
            # pulses which are the same within a tolerance to the
            # same value.  The value is the weighted average of the
            # occurences.
            #
            # E.g. 500x20 550x30 600x30  1000x10 1100x10  1700x5 1750x5
            #
            # becomes 556(x80) 1050(x20) 1725(x10)
            #
            if v == None:
                e = [plen]
                v = plen
                tot = plen * ms[plen]
                similar = ms[plen]
            elif plen < (v*self.TOLER_MAX):
                e.append(plen)
                tot += (plen * ms[plen])
                similar += ms[plen]
            else:
                v = int(round(tot/float(similar)))
                # set all previous to v
                for i in e:
                    ms[i] = v
                e = [plen]
                v = plen
                tot = plen * ms[plen]
                similar = ms[plen]

        v = int(round(tot/float(similar)))
        # set all previous to v
        for i in e:
            ms[i] = v

        if self.VERBOSE:
            print("t_m_s B", ms)

        for rec in records:
            rl = len(records[rec])
            for i in range(base, rl, 2):
                records[rec][i] = ms[records[rec][i]]

    def tidy(self, records):
        self.tidy_mark_space(records, 0)  # Marks.
        self.tidy_mark_space(records, 1)  # Spaces.

    def end_of_code(self):
        global code, fetching_code
        if len(code) > self.SHORT:
            self.normalise(code)
            fetching_code = False
        else:
            code = []
            print("Short code, probably a repeat, try again")

    def cbf(self, gpio, level, tick):
        global last_tick, in_code, code, fetching_code

        if level != pigpio.TIMEOUT:
            edge = pigpio.tickDiff(last_tick, tick)
            last_tick = tick
            if fetching_code:
                if (edge > self.PRE_US) and (not in_code):  # Start of a code.
                    in_code = True
                    # Start watchdog.
                    self.pi.set_watchdog(self.GPIO, self.POST_MS)
                elif (edge > self.POST_US) and in_code:  # End of a code.
                    in_code = False
                    self.pi.set_watchdog(self.GPIO, 0)  # Cancel watchdog.
                    self.end_of_code()
                elif in_code:
                    code.append(edge)
        else:
            self.pi.set_watchdog(self.GPIO, 0)  # Cancel watchdog.
            if in_code:
                in_code = False
                self.end_of_code()

    def record(self):
        self.is_connected()
        try:
            f = open(self.FILE, "r")
            records = json.load(f)
            f.close()
        except:
            records = {}
        # IR RX connected to this GPIO.
        self.pi.set_mode(self.GPIO, pigpio.INPUT)
        self.pi.set_glitch_filter(self.GPIO, self.GLITCH)  # Ignore glitches.
        self.pi.callback(self.GPIO, pigpio.EITHER_EDGE, self.cbf)

        # Process each id
        print("Recording")
        for arg in args.id:
            print("Press key for '{}'".format(arg))
            code = []
            fetching_code = True
            while fetching_code:
                time.sleep(0.1)
            print("Okay")
            time.sleep(0.5)

            if self.CONFIRM:
                press_1 = code[:]
                done = False

                tries = 0
                while not done:
                    print("Press key for '{}' to confirm".format(arg))
                    code = []
                    fetching_code = True
                    while fetching_code:
                        time.sleep(0.1)
                    press_2 = code[:]
                    the_same = self.compare(press_1, press_2)
                    if the_same:
                        done = True
                        records[arg] = press_1[:]
                        print("Okay")
                        time.sleep(0.5)
                    else:
                        tries += 1
                        if tries <= 3:
                            print("No match")
                        else:
                            print("Giving up on key '{}'".format(arg))
                            done = True
                        time.sleep(0.5)
            else:  # No confirm.
                records[arg] = code[:]

        self.pi.set_glitch_filter(self.GPIO, 0)  # Cancel glitch filter.
        self.pi.set_watchdog(self.GPIO, 0)  # Cancel watchdog.

        self.tidy(records)
        self.backup(self.FILE)

        f = open(self.FILE, "w")
        f.write(json.dumps(records, sort_keys=True).replace("],", "],\n")+"\n")
        f.close()

    def playbook(self):
        self.is_connected()
        try:
            f = open(self.FILE, "r")
        except:
            print("Can't open: {}".format(self.FILE))
            exit(0)
        records = json.load(f)
        f.close()
        # IR TX connected to this GPIO.
        self.pi.set_mode(self.GPIO, pigpio.OUTPUT)
        self.pi.wave_add_new()
        emit_time = time.time()

        if self.VERBOSE:
            print("Playing")
        for arg in args.id:
            if arg in records:
                code = records[arg]
                # Create wave
                marks_wid = {}
                spaces_wid = {}
                wave = [0]*len(code)
                for i in range(0, len(code)):
                    ci = code[i]
                    if i & 1:  # Space
                        if ci not in spaces_wid:
                            self.pi.wave_add_generic([pigpio.pulse(0, 0, ci)])
                            spaces_wid[ci] = self.pi.wave_create()
                        wave[i] = spaces_wid[ci]
                    else:  # Mark
                        if ci not in marks_wid:
                            wf = self.carrier(self.GPIO, self.FREQ, ci)
                            self.pi.wave_add_generic(wf)
                            marks_wid[ci] = self.pi.wave_create()
                        wave[i] = marks_wid[ci]
                delay = emit_time - time.time()

                if delay > 0.0:
                    time.sleep(delay)
                self.pi.wave_chain(wave)
                if self.VERBOSE:
                    print("key " + arg)
                while self.pi.wave_tx_busy():
                    time.sleep(0.002)
                emit_time = time.time() + self.GAP_S
                for i in marks_wid:
                    self.pi.wave_delete(marks_wid[i])
                marks_wid = {}
                for i in spaces_wid:
                    self.pi.wave_delete(spaces_wid[i])
                spaces_wid = {}
            else:
                print("Id {} not found".format(arg))


if __name__ == '__main__':
    p = argparse.ArgumentParser()

    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("-p", "--play",   help="play keys",   action="store_true")
    g.add_argument("-r", "--record", help="record keys", action="store_true")
    p.add_argument("-g", "--gpio", help="GPIO for RX/TX",
                   required=True, type=int)
    p.add_argument("-f", "--file", help="Filename",       required=True)
    p.add_argument('id', nargs='+', type=str, help='IR codes')
    p.add_argument("--freq",      help="frequency kHz",
                   type=float, default=38.0)
    p.add_argument("--gap",       help="key gap ms",
                   type=int, default=100)
    p.add_argument("--glitch",    help="glitch us",
                   type=int, default=100)
    p.add_argument("--post",      help="postamble ms",
                   type=int, default=15)
    p.add_argument("--pre",       help="preamble ms",
                   type=int, default=200)
    p.add_argument("--short",     help="short code length",
                   type=int, default=10)
    p.add_argument("--tolerance", help="tolerance percent",
                   type=int, default=15)
    p.add_argument("-v", "--verbose", help="Be verbose",
                   action="store_true")
    p.add_argument("--no-confirm", help="No confirm needed",
                   action="store_true")
    args = p.parse_args()

    irRemoteControl = IRRemoteControl(args)

    if args.record:
        irRemoteControl.record()
    else:
        irRemoteControl.playbook()
