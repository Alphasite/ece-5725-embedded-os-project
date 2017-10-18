#include <stdio.h>
#include <wiringPi.h>

#define LED 24 //BCM.GPIO 19 = wiringPi Pin 24
#define DELAY 500 //ms
int main (void)
{
    wiringPiSetup();

    pinMode (LED, OUTPUT);

    for (;;)
    {
        digitalWrite(LED,1); //on
        delay(DELAY);
        digitalWrite(LED, 0); //off
        delay(DELAY);
    }
    return 0;
}
