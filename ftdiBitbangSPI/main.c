/* This program is distributed under the GPL, version 2 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "ftdi.h"

int main(int argc, char **argv)
{
  struct ftdi_context *ftdi;
  int f, i;
  unsigned char buf[1];
  int retval = 0;

  if ((ftdi = ftdi_new()) == 0)
  {
    fprintf(stderr, "ftdi_new failed\n");
    return EXIT_FAILURE;
  }

  f = ftdi_usb_open(ftdi, 0x0403, 0x6014);

  if (f < 0 && f != -5)
  {
    fprintf(stderr, "unable to open ftdi device: %d (%s)\n", f, ftdi_get_error_string(ftdi));
    retval = 1;
    ftdi_free(ftdi);

    return retval;
  }
  printf("ftdi open succeeded: %d\n", f);
  printf("enabling bitbang mode\n");
  ftdi_set_bitmode(ftdi, 0xF0, BITMODE_BITBANG);
  buf[0] = 0x0;
  printf("turning everything off\n");
  f = ftdi_write_data(ftdi, buf, 1);
  if (f < 0)
  {
    fprintf(stderr, "write failed for 0x%x, error %d (%s)\n", buf[0], f, ftdi_get_error_string(ftdi));
  }
  int enTable[]={10, 13, 11, 12};
  unsigned char res, oldRes = 0;
  int en = 0, oldEn = 0;
  int val = 0;
  int counter = 0;
  while (1)
  {
    f = ftdi_read_pins(ftdi, &res);
    if (f < 0)
    {
      fprintf(stderr, "read failed for 0x%x, error %d (%s)\n", buf[0], f, ftdi_get_error_string(ftdi));
      ftdi_usb_close(ftdi);

      ftdi_free(ftdi);
      return 1;
    }
    en = enTable[res & 0x03];

  //  if (res & 0x04 != 0)
  //    printf("NOW***************************\n");
    if (en != oldEn)
    {
      int delta = (en - oldEn);
      if (delta == 1 | delta == -3)
        val += 1;
      else
        val -= 1;
      oldEn = en;
      if (val == 0)
        printf("%d %d %d %d \n",counter, (res & 0x03), (en), (val));
      counter ++;
    }

    //  usleep(1 * 1000000);
  }

  ftdi_usb_close(ftdi);

  ftdi_free(ftdi);

  return retval;
}
