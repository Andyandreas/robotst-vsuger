from machine import Pin, PWM
import utime

# Opsætning af motorer
PWMA = PWM(Pin(16))
PWMA.freq(1000)
AIN1 = Pin(17, Pin.OUT)
AIN2 = Pin(18, Pin.OUT)

PWMB = PWM(Pin(21))
PWMB.freq(1000)
BIN1 = Pin(19, Pin.OUT)
BIN2 = Pin(20, Pin.OUT)

# Opsætning af afstandssensor
Trig = Pin(14, Pin.OUT)
Echo = Pin(15, Pin.IN)

# Opsætning af yderligere infrarøde sensorer
DSR = Pin(2, Pin.IN)
DSL = Pin(3, Pin.IN)

# Giv tid til at systemet starter
utime.sleep(2)

# Funktion til at måle afstand med timeout
def measure_distance():
    Trig.value(0)
    utime.sleep_us(2)
    Trig.value(1)
    utime.sleep_us(10)
    Trig.value(0)

    timeout = utime.ticks_ms() + 200  # 200 ms timeout
    while Echo.value() == 0:
        if utime.ticks_ms() > timeout:  # Hvis timeout overskrides, returnér stor værdi
            return 100
    pulse_start = utime.ticks_us()

    timeout = utime.ticks_ms() + 200
    while Echo.value() == 1:
        if utime.ticks_ms() > timeout:
            return 100
    pulse_end = utime.ticks_us()

    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * 0.0343) / 2  # Omregning til cm
    print(f"Afstand: {distance:.2f} cm")
    return distance

# Funktion til at køre fremad
def forward(speed):
    duty = int(speed * 65535 / 100)
    
    PWMA.duty_u16(duty)
    AIN1.value(1)
    AIN2.value(0)  # Motor 1 kører fremad

    PWMB.duty_u16(duty)
    BIN1.value(0)  # Motor 2 kører fremad i modsatte retning
    BIN2.value(1)

    print(f"Kører fremad med {speed}% hastighed")

# Funktion til at stoppe motorer
def stop():
    PWMA.duty_u16(0)
    AIN1.value(0)
    AIN2.value(0)

    PWMB.duty_u16(0)
    BIN1.value(0)
    BIN2.value(0)

    print("Motorer stoppet")

# Funktion til at dreje til højre langsommere (20% hastighed)
def turn_right():
    PWMA.duty_u16(int(65535 * 0.20))  # 20% hastighed
    AIN1.value(1)  # Motor 1 drejer højre
    AIN2.value(0)

    PWMB.duty_u16(int(65535 * 0.20))  # 20% hastighed
    BIN1.value(1)  # Motor 2 drejer højre
    BIN2.value(0)

    print("Drejer til højre langsommere")

    utime.sleep(2)  # Drej langsommere i 2 sekunder (juster dette efter behov)
    stop()  # Stop drejningen

# Funktion til at dreje til venstre langsommere (20% hastighed)
def turn_left():
    PWMA.duty_u16(int(65535 * 0.10))  # 20% hastighed
    AIN1.value(0)  # Motor 1 drejer venstre
    AIN2.value(1)

    PWMB.duty_u16(int(65535 * 0.10))  # 20% hastighed
    BIN1.value(0)  # Motor 2 drejer venstre
    BIN2.value(1)

    print("Drejer til venstre langsommere")

    utime.sleep(2)  # Drej langsommere i 2 sekunder (juster dette efter behov)
    stop()  # Stop drejningen

# Funktion til at slukke systemet
def power_off():
    stop()
    print("Systemet er slukket")

# Start programmet
print("Starter program...")

while True:
    distance = measure_distance()
    dsr_value = DSR.value()
    dsl_value = DSL.value()
    
    if distance < 40 or dsr_value == 1 or dsl_value == 1:  # Stop og drej hvis objektet er tættere end 40 cm eller infrarøde sensorer aktiveres
        print("Objekt for tæt! Stopper motorerne og drejer.")
        stop()
        
        # Drej indtil der er mindst 60 cm plads
        while distance < 45:
            print("Drejning... vent på at der er nok plads.")
            turn_right()  # Eller brug turn_left(), afhængigt af hvilken retning du vil dreje
            distance = measure_distance()  # Mål afstanden igen
        
        forward(50)  # Kør fremad, når der er mindst 60 cm
    else:
        forward(50)  # Kør fremad, hvis der er mere end 40 cm
    utime.sleep(0.1)

    # Hvis du vil stoppe systemet, kan du bruge power_off() funktionen
    # power_off()  # For at slukke programmet


