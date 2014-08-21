#pragma once

#ifdef __cplusplus
extern "C" {
#endif // c++

typedef struct ptz_t ptz_t;

ptz_t *ptz_open(const char *serial_name, int addr);
void ptz_close(ptz_t *ptz);

int ptz_left(ptz_t *ptz, int speed);
int ptz_right(ptz_t *ptz, int speed);
int ptz_up(ptz_t *ptz, int speed);
int ptz_down(ptz_t *ptz, int speed);

int ptz_stop(ptz_t *ptz);

int ptz_set_pos(ptz_t *ptz, int x, int y, int xspeed, int yspeed);
int ptz_get_pos(ptz_t *ptz, int *x, int *y);

int ptz_set_zoom(ptz_t *ptz, int z);
int ptz_get_zoom(ptz_t *ptz, int *z);

int ptz_preset_save(ptz_t *ptz, int id);
int ptz_preset_call(ptz_t *ptz, int id);
int ptz_preset_clear(ptz_t *ptz, int id);

int ptz_zoom_tele(ptz_t *ptz, int s);
int ptz_zoom_wide(ptz_t *ptz, int s);
int ptz_zoom_stop(ptz_t *ptz);

#ifdef __cplusplus
}
#endif // c++

