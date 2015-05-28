#pragma once

#ifdef __cplusplus
extern "C" {
#endif // c++

typedef struct ptz_t ptz_t;

int is_prepared(ptz_t *ptz);
ptz_t *ptz_open(const char *serial_name, int addr);
ptz_t *ptz_open_with_config(const char *cfg_name);
void ptz_close(ptz_t *ptz);

int ptz_last_error();

int ptz_left(ptz_t *ptz, int speed);
int ptz_right(ptz_t *ptz, int speed);
int ptz_up(ptz_t *ptz, int speed);
int ptz_down(ptz_t *ptz, int speed);

int ptz_stop(ptz_t *ptz);

int ptz_set_pos(ptz_t *ptz, int x, int y, int xspeed = 5, int yspeed = 5);
int ptz_get_pos(ptz_t *ptz, int *x, int *y);
int ptz_set_relative_pos(ptz_t *ptz, int x, int y, int sx= 0, int sy = 0);

int ptz_set_zoom(ptz_t *ptz, int z);
int ptz_get_zoom(ptz_t *ptz, int *z);

int ptz_preset_save(ptz_t *ptz, int id);
int ptz_preset_call(ptz_t *ptz, int id);
int ptz_preset_clear(ptz_t *ptz, int id);

int ptz_zoom_tele(ptz_t *ptz, int s);
int ptz_zoom_wide(ptz_t *ptz, int s);
int ptz_zoom_stop(ptz_t *ptz);

int ptz_set_pos_with_reply(ptz_t *ptz, int x, int y, int sx = 5, int sy = 5);
int ptz_set_zoom_with_reply(ptz_t *ptz, int z);

int ptz_mouse_trace(ptz_t *ptz, double hvs, double vvs, int sx = 5, int sy = 5);
/// 从 zoom value 计算返回实际倍率 ..
double ptz_ext_get_scals(ptz_t *ptz, int z);

#ifdef __cplusplus
}
#endif // c++

