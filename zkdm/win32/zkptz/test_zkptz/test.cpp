#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#ifdef WIN32
#	include <Windows.h>
#	define msleep Sleep
#else
#	include <unistd.h>
#	define msleep(x) usleep(x*1000)
#endif // 

#include "../../../ptz/ptz.h"


int main(int argc, char **argv)
{
	const char *serial_name = "COM3";
	if (argc == 2)
		serial_name = argv[1];

	ptz_t *ptz = ptz_open(serial_name, 1);
	if (!ptz) {
		fprintf(stderr, "ERR: can't open %s\n", serial_name);
		return -1;
	}

	fprintf(stderr, "DEBUG: open %s ok\n", serial_name);

	int x, y;
	if (ptz_get_pos(ptz, &x, &y) < 0) {
		fprintf(stderr, "ERR: get_pos err\n");
		return -1;
	}
	
	fprintf(stderr, "DEBUG: get_pos: %d, %d\n", x, y);

	int want_x = 300, want_y = 300;

	if (ptz_set_pos(ptz, want_x, want_y, 1, 1) < 0) {
		fprintf(stderr, "ERR: set_pos err\n");
		return -1;
	}

	fprintf(stderr, "DEBUG: set_pos: 300, 300\n");

	while (1) {
		ptz_get_pos(ptz, &x, &y);
		if (fabs((float)x - want_x) < 5 && fabs((float)y - want_y) < 5)
			break;

		fprintf(stderr, "\tpos=%d, %d\n", x, y);
		msleep(100);
	}

	fprintf(stderr, "test end!\n");

	return 0;
}
