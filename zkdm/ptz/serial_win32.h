#pragma once

typedef struct serial_t serial_t;

serial_t *serial_open(const char *name);
void serial_close(serial_t *s);

/// return last error code
int serial_last_error(serial_t *s);

/// write
int serial_write(serial_t *s, const void *data, int len);

/// read
int serial_read(serial_t *s, void *buf, int buf_len);

/// clear buf
