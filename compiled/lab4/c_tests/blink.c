#include <stdio.h>
#include <wiringPi.h>
#include <time.h>

#define NSEC_PER_SEC    (1000000000) /* The number of nsecs per sec. */

struct timespec t;

int main (int argc, char** argv)
{
  int period = 9000;  // set initial period for delay in nsec
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

  pinMode(24, OUTPUT);

  while( current_sec < 100 ) {   // run the loop for 100 sec
     digitalWrite (24,  PinValue) ;
     clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &t, NULL); // delay a bit...
     PinValue = PinValue ^ 1;
     t.tv_nsec += period;   // add in initial period

     while (t.tv_nsec >= NSEC_PER_SEC) {   // This accounts for 1 sec rollover
        t.tv_nsec -= NSEC_PER_SEC;
        t.tv_sec++;
        current_sec = t.tv_sec - start_sec;  // how many seconds since we started?
     }
  }
  printf ("stopped at %d seconds\n", current_sec);

  return 0 ;
}


