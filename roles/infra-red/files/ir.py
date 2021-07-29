import time
import lgpio

# IR_SEND = 13
IR_RECEIVE = 4


def ir_receive():
    # handler
    handler = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_input(handler, IR_RECEIVE)

    try:
        lgpio.callback(handler, IR_RECEIVE, lgpio.BOTH_EDGES, call_back)

        while True:
            print("==========")
            time.sleep(0.1)

    except KeyboardInterrupt:
        lgpio.gpiochip_close(handler)


def call_back(chip, gpio, level, timestamp):
    print(chip, gpio, level, timestamp)


if __name__ == "__main__":
    ir_receive()
