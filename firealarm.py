import RPi.GPIO as GPIO
import time

# ADC Gas Sensor
SPICLK = 11  # clock
SPIMISO = 9  # master input, slave output
SPIMOSI = 10  # master output, slave input
SPICS = 8  # chip select
mq2_dpin = 26  # digital pin
mq2_apin = 0  # analog chanel

# Buzzer
BUZZER = 2

# Flame sensor
flame_dpin = 3


# port init
def init():
    GPIO.setwarnings(False)
    GPIO.cleanup()  # clean up at the end of your script
    GPIO.setmode(GPIO.BCM)  # to specify whilch pin numbering system

    # set up the SPI interface pins
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)
    GPIO.setup(mq2_dpin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # set up Buzzer
    GPIO.setup(BUZZER, GPIO.OUT)
    GPIO.output(BUZZER, True)

    # set up Flame Sensor
    GPIO.setup(flame_dpin, GPIO.IN)


# read SPI data from MCP3008(or MCP3204) chip,8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if (adcnum > 7) or (adcnum < 0):
        return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)  # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3  # we only need to send 5 bits here
    for i in range(5):
        if commandout & 0x80:
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if GPIO.input(misopin):
            adcout |= 0x1

    GPIO.output(cspin, True)

    adcout >>= 1  # first bit is 'null' so drop it
    return adcout


def buzzer(value):
    if value == 1:
        for i in range(2):
            GPIO.output(BUZZER, False)
            time.sleep(0.2)
            GPIO.output(BUZZER, True)
            time.sleep(0.3)
            print("Gas leakage")
            colevel = readadc(mq2_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
            if (colevel / 1024.) * 3.3 >= 1.8:
                print "High flammable gas concentration"
        print "--------------"
    elif value == 2:
        for i in range(5):
            GPIO.output(BUZZER, False)
            time.sleep(0.1)
            GPIO.output(BUZZER, True)
            time.sleep(0.1)
            print("Flame detected")
        print "--------------"
    elif value == 3:
        GPIO.output(BUZZER, False)
        time.sleep(0.9)
        GPIO.output(BUZZER, True)
        time.sleep(0.1)
        print("Flame and gas leakage detected DANGER!")
        print "--------------"
    else:
        time.sleep(1)


# main loop
def main():
    init()
    print"please wait..."
    time.sleep(20)
    while True:
        value = 0
        if GPIO.input(mq2_dpin):
            print("No gas leak")
        else:
            value += 1

        if GPIO.input(flame_dpin):
            value += 2

        buzzer(value)


if __name__ == '__main__':
    try:
        main()
        pass
    except KeyboardInterrupt:
        pass

GPIO.cleanup()
