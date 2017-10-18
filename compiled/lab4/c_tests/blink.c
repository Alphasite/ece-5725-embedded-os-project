#include <stdio.h>
#include <wiringPi.h>

#define LED 24 //BCM.GPIO 19 = wiringPi Pin 24
#define DELAY 500 //ms

#define NSEC_PER_SEC    (1000000000) /* The number of nsecs per sec. */

struct timespec t;

int main (int argc, char** argv)
{
  int period = 500000;  // set initial period for delay in nsec
  int PinValue = 0;  // hi/low indication of output Pin
  unsigned int current_sec, start_sec;
  float freq;

  if (argc>=2 && atoi(argv[1])>0 ) {  // if we have a positive input value
     period = atoi(argv[1]);
  }
  printf ("Set 1/2 period to %d nanoseconds\n",period);
  freq = NSEC_PER_SEC * ((float)1/(2*period));
  printf ("   Frequency =  %f Hz\n",freq);

  wiringPiSetup () ;

  clock_gettime(CLOCK_MONOTONIC ,&t); // setup timer t
  t.tv_nsec += period;   // add in initial period
  //printf ( "sec = %d \n", t.tv_sec);
  start_sec = t.tv_sec;
  current_sec = 0;

  pinMode (LED, OUTPUT) ;
