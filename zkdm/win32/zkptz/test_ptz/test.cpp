#include <stdio.h>
#include <stdlib.h>
#include "../../../ptz/ptz.h"
#include <Windows.h>

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

		int addr = 1;

		if (argc == 3) {
			addr = atoi(argv[2]);
		}

		ptz = ptz2_open(name, addr);
	}
	else {
		ptz = ptz2_open_with_config(argv[1]);
	}

	if (!ptz) {
		fprintf(stderr, "XXX: open fault, code=%d\n", ptz_last_error());
	}
	else {
		fprintf(stderr, "== set_pos: 0, 0\n");
		ptz2_set_pos_with_reply(ptz, 0, 0, 1, 1);

		fprintf(stderr, "== zoom tele\n");
		ptz2_zoom_tele(ptz, 1);
		Sleep(3000);

		int z;
		ptz2_get_zoom(ptz, &z);
		fprintf(stderr, "got: z=%d\n", z);

		fprintf(stderr, "== zoom wide\n");
		ptz2_zoom_wide(ptz, 1);
		Sleep(1000);

		ptz2_get_zoom(ptz, &z);
		fprintf(stderr, "get z=%d\n", z);

		fprintf(stderr, "== zoom stop\n");
		ptz2_zoom_stop(ptz);


		fprintf(stderr, "== left\n");
		ptz2_left(ptz, 1);
		Sleep(3000);

		fprintf(stderr, "== right\n");
		ptz2_right(ptz, 1);
		Sleep(3000);

		fprintf(stderr, "== up\n");
		ptz2_up(ptz, 3);
		Sleep(1000);

		fprintf(stderr, "== down\n");
		ptz2_down(ptz, 3);
		Sleep(1000);

		fprintf(stderr, "== stop\n");
		ptz2_stop(ptz);

		fprintf(stderr, "== set_pos 300, 300\n");
		ptz2_set_pos(ptz, 300, 300, 36, 36);
		int x, y;
		if (ptz2_get_pos(ptz, &x, &y) == 0) {
			fprintf(stderr, "get pos: %d, %d\n", x, y);
		}

		ptz2_close(ptz);
		fprintf(stderr, "XXX: end!\n");
	}

	return 0;
}
