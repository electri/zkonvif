#pragma once

#ifdef __cplusplus
extern "C" {
#endif // c++

typedef struct visca_t visca_t;

visca_t *visca_open(const char *serial_name, int addr);
void visca_close(visca_t *ctx);

// 返回云台水平，竖直最大速度.
int visca_get_max_speed(visca_t *ctx, int *sx, int *sy);

int visca_left(visca_t *ctx, int speed);
int visca_right(visca_t *ctx, int speed);
int visca_up(visca_t *ctx, int speed);
int visca_down(visca_t *ctx, int speed);
int visca_stop(visca_t *ctx);

int visca_setpos(visca_t *ctx, short x, short y, int sx, int sy);
int visca_setpos_blocked(visca_t *ctx, short x, short y, int sx, int sy);
int visca_getpos(visca_t *ctx, short *x, short *y);

int visca_zoom_set(visca_t *ctx, int z);
int visca_zoom_set_blocked(visca_t *ctx, int z);
int visca_zoom_get(visca_t *ctx, int *z);

int visca_zoom_tele(visca_t *ctx, int speed);
int visca_zoom_wide(visca_t *ctx, int speed);
int visca_zoom_stop(visca_t *ctx);

#ifdef __cplusplus
}
#endif // c++
