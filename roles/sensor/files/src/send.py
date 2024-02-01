import pigpio
import collections
import dataclasses
import json
import argparse

@dataclasses.dataclass(frozen=True)
class IROption:
    id: str
    gpio: int
    file: str

class InfraredSender:

    ENTRY_MAX = 600
    LOOP_MAX = 20

    def __init__(self, option: IROption):
        try:
            f = open(option.file, "r")
            records = json.load(f)
        except:
            raise RuntimeError("Can't read file")
        finally:
            f.close()

        if option.id not in records:
            raise ValueError('record ID not found')

        self.gpio = option.gpio # GPIOピン
        self.code = records[option.id] # 送信コード
        self.send_wids = [0] * len(self.code)  # 送信する波形IDのリスト

    def run(self) -> None:
        pi = pigpio.pi()

        if not pi.connected:
            raise RuntimeError('Pigpio Connection Failed')

        mark_wids = {}  # Mark(38kHzパルス)波形, key:長さ, value:ID
        space_wids = {}  # Speace(待機)波形, key:長さ, value:ID

        try:
            pi.set_mode(self.gpio, pigpio.OUTPUT)
            pi.wave_clear()

            for i in range(len(self.code)):
                if i % 2 == 0:
                    # 同じ長さのMark波形が無い場合は新しく生成
                    if self.code[i] not in mark_wids:
                        pulses = []
                        n = self.code[i] // 26  # 38kHz = 26us周期の繰り返し回数
                        for j in range(n):
                            pulses.append(pigpio.pulse(1 << self.gpio, 0, 8))  # 8us highパルス
                            pulses.append(pigpio.pulse(0, 1 << self.gpio, 18))  # 18us lowパルス
                        pi.wave_add_generic(pulses)
                        mark_wids[self.code[i]] = pi.wave_create()
                    self.send_wids[i] = mark_wids[self.code[i]]
                else:
                    # 同じ長さのSpace波形が無い場合は新しく生成
                    if self.code[i] not in space_wids:
                        pi.wave_add_generic([pigpio.pulse(0, 0, self.code[i])])
                        space_wids[self.code[i]] = pi.wave_create()
                    self.send_wids[i] = space_wids[self.code[i]]

            if len(self.send_wids) > InfraredSender.ENTRY_MAX:
                self.compress_wids()

            pi.wave_chain(self.send_wids)

        except Exception as e:
            print(e)
            raise RuntimeError('Can\'t send infrared signal')

        finally:
            pi.wave_clear()
            pi.stop()

    def compress_wids(self) -> None:
        ### Compressing a wave code if the length is more than 600 ###
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
            self.code = [255, 0, 255, 1, t[-1], 0]
            self.code[2:2] = repeat_unit
            wave[i:i+1] = self.code
            return wave

        #encoding the original wave to the tuple code
        for wl in range(2, len(self.send_wids)//2):
            pre_len = 0
            while len(self.send_wids) != pre_len:
                pre_len = len(self.send_wids)
                ngrams = make_ngram(self.send_wids, wl)
                for ngram in ngrams:
                    ngram_wave = ngram[0]
                    ngram_freq = ngram[1]
                    if ngram_freq >= 2:
                        for i in range(len(self.send_wids) - len(ngram_wave)):
                            if tuple(self.send_wids[i:i+wl]) == ngram_wave:
                                for rn in range(2, ngram_freq):
                                    if self.send_wids[i:i+(wl*rn)] != list(ngram_wave * rn):
                                        if wl*(rn-2) > 6 or depth_of_tuple(ngram_wave) >= 2 and rn-1 >= 2 :
                                            loop_code = list(ngram_wave) + [rn-1]
                                            self.send_wids[i:i+((rn-1)*wl)] = [tuple(loop_code)]
                                        break

        #decoding the tuple-type code into the wave code
        rest_loop_count = InfraredSender.LOOP_MAX
        for d in range(depth_of_tuple(tuple(self.send_wids))):
            for i,item in enumerate(self.send_wids):
                if isinstance(item, tuple):
                    if rest_loop_count <= 0:
                        nonloop_decode(self.send_wids, i, item)
                    elif depth_of_tuple(item) > 1:
                        loop_decode(self.send_wids, i, item)
                        rest_loop_count -= 1
        efficiencies = sorted(set([(len(item)-1)*(item[-1]-1) for item in self.send_wids if isinstance(item, tuple)]), reverse=True)
        for eff in efficiencies:
            for i,item in enumerate(self.send_wids):
                if isinstance(item, tuple):
                    if rest_loop_count <= 0:
                        nonloop_decode(self.send_wids, i, item)
                    elif (len(item)-1)*(item[-1]-1) == eff:
                        loop_decode(self.send_wids, i, item)
                        rest_loop_count -= 1
    ### Compression end ###


if __name__ == '__main__':
    p = argparse.ArgumentParser()

    p.add_argument("-g",
                   "--gpio",
                   help="GPIO for RX/TX",
                   required=True,
                   type=int)
    p.add_argument("-f", "--file", help="Filename", required=True)
    p.add_argument('id', nargs='+', type=str, help='IR codes')
    args = p.parse_args()

    option: IROption = IROption(
        id=args.id[0],  # 複数指定できるが、最初のだけとる
        gpio=args.gpio,
        file=args.file,
    )

    sender = InfraredSender(option)
    sender.run()
