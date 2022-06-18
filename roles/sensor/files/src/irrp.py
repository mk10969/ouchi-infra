#!/usr/bin/env python3

import dataclasses
import time
import json
import os
import argparse
# http://abyz.me.uk/rpi/pigpio/python.html
import pigpio


# いまいちだな・・・
last_tick = 0
in_code = False
code = []
fetching_code = False


@dataclasses.dataclass(frozen=True)
class IROption:
    id: str
    gpio: int
    file: str
    freq: float = 38.0
    gap: int = 100
    glitch: int = 100
    pre: int = 200
    post: int = 15
    short: int = 10
    tolerance: int = 15
    no_confirm: bool = False
    verbose: bool = False


class IRRemoteControl:
    @staticmethod
    def backup(f):
        """
        f -> f.bak -> f.bak1 -> f.bak2
        """
        try:
            os.rename(
                os.path.realpath(f) + ".bak1",
                os.path.realpath(f) + ".bak2")
        except:
            pass
        try:
            os.rename(
                os.path.realpath(f) + ".bak",
                os.path.realpath(f) + ".bak1")
        except:
            pass
        try:
            os.rename(os.path.realpath(f), os.path.realpath(f) + ".bak")
        except:
            pass

    @staticmethod
    def carrier(gpio, frequency, micros):
        """
        Generate carrier square wave.
        """
        wf = []
        cycle = 1000.0 / frequency
        cycles = int(round(micros / cycle))
        on = int(round(cycle / 2.0))
        sofar = 0
        for c in range(cycles):
            target = int(round((c + 1) * cycle))
            sofar += on
            off = target - sofar
            sofar += off
            wf.append(pigpio.pulse(1 << gpio, 0, on))
            wf.append(pigpio.pulse(0, 1 << gpio, off))
        return wf

    def __init__(self, option: IROption):
        self.ID = option.id
        self.GPIO = option.gpio
        self.FILE = option.file
        self.GLITCH = option.glitch
        self.PRE_MS = option.pre
        self.POST_MS = option.post
        self.FREQ = option.freq
        self.VERBOSE = option.verbose
        self.SHORT = option.short
        self.GAP_MS = option.gap
        self.NO_CONFIRM = option.no_confirm
        self.TOLERANCE = option.tolerance
        self.POST_US = self.POST_MS * 1000
        self.PRE_US = self.PRE_MS * 1000
        self.GAP_S = self.GAP_MS / 1000.0
        self.CONFIRM = not self.NO_CONFIRM
        self.TOLER_MIN = (100 - self.TOLERANCE) / 100.0
        self.TOLER_MAX = (100 + self.TOLERANCE) / 100.0
        # instance
        self.pi = pigpio.pi()  # Connect to Pi.

    def __del__(self):
        self.pi.stop()  # Disconnect from Pi.

    def check_connection(self):
        if not self.pi.connected:
            raise RuntimeError('Pigpio Connection Failed')

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
        p = [0] * entries  # Set all entries not processed.
        for i in range(entries):
            if not p[i]:  # Not processed?
                v = c[i]
                tot = v
                similar = 1.0
                # Find all pulses with similar lengths to the start pulse.
                for j in range(i + 2, entries, 2):
                    if not p[j]:  # Unprocessed.
                        # Similar.
                        if (c[j] * self.TOLER_MIN) < v < (c[j] *
                                                          self.TOLER_MAX):
                            tot = tot + c[j]
                            similar += 1.0
                # Calculate the average pulse length.
                newv = round(tot / similar, 2)
                c[i] = newv
                # Set all similar pulses to the average value.
                for j in range(i + 2, entries, 2):
                    if not p[j]:  # Unprocessed.
                        # Similar.
                        if (c[j] * self.TOLER_MIN) < v < (c[j] *
                                                          self.TOLER_MAX):
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
            p1[i] = int(round((p1[i] + p2[i]) / 2.0))
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
            elif plen < (v * self.TOLER_MAX):
                e.append(plen)
                tot += (plen * ms[plen])
                similar += ms[plen]
            else:
                v = int(round(tot / float(similar)))
                # set all previous to v
                for i in e:
                    ms[i] = v
                e = [plen]
                v = plen
                tot = plen * ms[plen]
                similar = ms[plen]

        v = int(round(tot / float(similar)))
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
        self.check_connection()
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
        print("Press key for '{}'".format(self.ID))
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
                print("Press key for '{}' to confirm".format(self.ID))
                code = []
                fetching_code = True
                while fetching_code:
                    time.sleep(0.1)
                press_2 = code[:]
                the_same = self.compare(press_1, press_2)
                if the_same:
                    done = True
                    records[self.ID] = press_1[:]
                    print("Okay")
                    time.sleep(0.5)
                else:
                    tries += 1
                    if tries <= 3:
                        print("No match")
                    else:
                        print("Giving up on key '{}'".format(self.ID))
                        done = True
                    time.sleep(0.5)
        else:  # No confirm.
            records[self.ID] = code[:]

        self.pi.set_glitch_filter(self.GPIO, 0)  # Cancel glitch filter.
        self.pi.set_watchdog(self.GPIO, 0)  # Cancel watchdog.

        self.tidy(records)
        self.backup(self.FILE)

        f = open(self.FILE, "w")
        f.write(
            json.dumps(records, sort_keys=True).replace("],", "],\n") + "\n")
        f.close()

    def playbook(self):
        self.check_connection()
        try:
            f = open(self.FILE, "r")
        except:
            raise RuntimeError("Can't open file")

        records = json.load(f)
        f.close()

        if self.ID not in records:
            raise ValueError(f'record ID not found')

        if self.VERBOSE:
            print("Playing")

        # IR TX connected to this GPIO.
        self.pi.set_mode(self.GPIO, pigpio.OUTPUT)
        self.pi.wave_clear()
        # 生成できる波形の長さには制限があるので、種類とcodeの長さごとにまとめて節約する
        mark_wids = {}  # Mark(38kHzパルス)波形, key:長さ, value:ID
        space_wids = {}  # Speace(待機)波形, key:長さ, value:ID
        send_wids = [0] * len(code)  # 送信する波形IDのリスト

        for i in range(len(code)):
            if i % 2 == 0:
                # 同じ長さのMark波形が無い場合は新しく生成
                if code[i] not in mark_wids:
                    pulses = []
                    n = code[i] // 26  # 38kHz = 26us周期の繰り返し回数
                    for _j in range(n):
                        pulses.append(pigpio.pulse(1 << self.GPIO, 0, 8))  # 8us highパルス
                        pulses.append(pigpio.pulse(0, 1 << self.GPIO, 18))  # 18us lowパルス
                    self.pi.wave_add_generic(pulses)
                    mark_wids[code[i]] = self.pi.wave_create()
                send_wids[i] = mark_wids[code[i]]
            else:
                # 同じ長さのSpace波形が無い場合は新しく生成
                if code[i] not in space_wids:
                    self.pi.wave_add_generic([pigpio.pulse(0, 0, code[i])])
                    space_wids[code[i]] = self.pi.wave_create()
                send_wids[i] = space_wids[code[i]]

        ### Compressing a wave code if the length is more than 600 ###
        ENTRY_MAX = 600
        LOOP_MAX = 20
        if len(send_wids) > ENTRY_MAX:
            import collections

            def make_ngram(l, n):
                ngrams = list(zip(*(l[i:] for i in range(n))))
                return(collections.Counter(ngrams).most_common())

            def depth_of_tuple(t):
                if isinstance(t, tuple):
                    if t == tuple() : return 1
                    return 1 + max(depth_of_tuple(item) for item in t)
                else:
                    return 0

            def nonloop_decode(wave, i, t):
                wave[i:i+1] = [t[num] for num in range(len(t)-1)]*t[-1]
                return wave

            def loop_decode(wave, i, t):
                repeat_unit = [t[num] for num in range(len(t)-1)]
                code = [255, 0, 255, 1, t[-1], 0]
                code[2:2] = repeat_unit
                wave[i:i+1] = code
                return wave

            #encoding the original wave to the tuple code
            for wl in range(2, len(send_wids)//2):
                pre_len = 0
                while len(send_wids) != pre_len:
                    pre_len = len(send_wids)
                    ngrams = make_ngram(send_wids, wl)
                    for ngram in ngrams:
                        ngram_wave = ngram[0]
                        ngram_freq = ngram[1]
                        if ngram_freq >= 2:
                            for i in range(len(send_wids) - len(ngram_wave)):
                                if tuple(send_wids[i:i+wl]) == ngram_wave:
                                    for rn in range(2, ngram_freq):
                                        if send_wids[i:i+(wl*rn)] != list(ngram_wave * rn):
                                            if wl*(rn-2) > 6 or depth_of_tuple(ngram_wave) >= 2 and rn-1 >= 2 :
                                                loop_code = list(ngram_wave) + [rn-1]
                                                send_wids[i:i+((rn-1)*wl)] = [tuple(loop_code)]
                                            break

            #decoding the tuple-type code into the wave code
            rest_loop_count = LOOP_MAX
            for _d in range(depth_of_tuple(tuple(send_wids))):
                for i,item in enumerate(send_wids):
                    if isinstance(item, tuple):
                        if rest_loop_count <= 0:
                            nonloop_decode(send_wids, i, item)
                        elif depth_of_tuple(item) > 1:
                            loop_decode(send_wids, i, item)
                            rest_loop_count -= 1
            efficiencies = sorted(set([(len(item)-1)*(item[-1]-1) for item in send_wids if isinstance(item, tuple)]), reverse=True)
            for eff in efficiencies:
                for i,item in enumerate(send_wids):
                    if isinstance(item, tuple):
                        if rest_loop_count <= 0:
                            nonloop_decode(send_wids, i, item)
                        elif (len(item)-1)*(item[-1]-1) == eff:
                            loop_decode(send_wids, i, item)
                            rest_loop_count -= 1
        ### Compression end ###

        self.pi.wave_chain(send_wids)
        self.pi.wave_clear()


if __name__ == '__main__':
    p = argparse.ArgumentParser()

    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("-p", "--play", help="play keys", action="store_true")
    g.add_argument("-r", "--record", help="record keys", action="store_true")
    p.add_argument("-g",
                   "--gpio",
                   help="GPIO for RX/TX",
                   required=True,
                   type=int)
    p.add_argument("-f", "--file", help="Filename", required=True)
    p.add_argument('id', nargs='+', type=str, help='IR codes')
    p.add_argument("--freq", help="frequency kHz", type=float, default=38.0)
    p.add_argument("--gap", help="key gap ms", type=int, default=100)
    p.add_argument("--glitch", help="glitch us", type=int, default=100)
    p.add_argument("--post", help="postamble ms", type=int, default=15)
    p.add_argument("--pre", help="preamble ms", type=int, default=200)
    p.add_argument("--short", help="short code length", type=int, default=10)
    p.add_argument("--tolerance",
                   help="tolerance percent",
                   type=int,
                   default=15)
    p.add_argument("-v", "--verbose", help="Be verbose", action="store_true")
    p.add_argument("--no-confirm",
                   help="No confirm needed",
                   action="store_true")
    args = p.parse_args()
    print(args)

    option: IROption = IROption(
        id=args.id[0],  # 複数指定できるが、最初のだけとる
        gpio=args.gpio,
        file=args.file,
        glitch=args.glitch,
        pre=args.pre,
        post=args.post,
        freq=args.freq,
        verbose=args.verbose,
        short=args.short,
        gap=args.gap,
        no_confirm=args.no_confirm,
        tolerance=args.tolerance)

    print(option)
    irRemoteControl = IRRemoteControl(option)

    if args.record:
        irRemoteControl.record()
    else:
        irRemoteControl.playbook()
