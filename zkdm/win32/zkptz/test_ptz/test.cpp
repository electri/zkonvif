#include <stdio.h>
#include <stdlib.h>
#include "../../../ptz/ptz.h"

int main(int argc, char **argv)
{
	if (argc < 2) {
		fprintf(stderr, "usage: %s <COM num | cfg fname>\n", argv[0]);
		return -1;
	}

	ptz_t *ptz;

	if (atoi(argv[1]) > 0 && atoi(argv[1]) < 20) {
		char name[16];
		_snprintf(name, sizeof(name), "COM%d", atoi(argv[1]));

		ptz = ptz_open(name, 0);
	}
	else {
		ptz = ptz_open_with_config(argv[1]);
	}

	if (!ptz) {
		fprintf(stderr, "XXX: open fault, code=%d\n", ptz_last_error());
	}
	else {
		ptz_close(ptz);
		fprintf(stderr, "XXX: end!\n");
	}

	return 0;
}
