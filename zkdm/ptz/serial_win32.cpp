#include <stdio.h>
#include <stdlib.h>
#include <Windows.h>
#include "serial_win32.h"
#include <string.h>

struct serial_t
{
	HANDLE serial;
	char *name;
};

int serial_last_error(serial_t *s)
{
	return GetLastError();
}

serial_t *serial_open(const char *name)
{
	HANDLE h = CreateFile(name, GENERIC_READ | GENERIC_WRITE, 0, 0, OPEN_ALWAYS, 0, 0);
	if (h == INVALID_HANDLE_VALUE) {
		fprintf(stderr, "[ptz][%s]: %s: can't open %s, err=%d\n", name, __FUNCTION__, name, GetLastError());
		return 0;
	}

	// set comm
	if (!SetupComm(h, 4, 4)) {
		fprintf(stderr, "[ptz][%s]: %s: SetupComm fault!, err=%d\n", name, __FUNCTION__, GetLastError());
		CloseHandle(h);
		return 0;
	}

	DCB dcb;
	memset(&dcb, 0, sizeof(dcb));
	dcb.ByteSize = sizeof(dcb);
	if (!GetCommState(h, &dcb)) {
		fprintf(stderr, "[ptz][%s]: %s: GetCommState fault!, err=%d\n", name, __FUNCTION__, GetLastError());
		CloseHandle(h);
		return 0;
	}

	dcb.BaudRate = 9600;
	dcb.ByteSize = 8;
	dcb.Parity = NOPARITY;
	dcb.StopBits = ONESTOPBIT;
	dcb.fAbortOnError = TRUE; // ??
	dcb.fOutxCtsFlow = FALSE;	// Disable CTS monitoring
	dcb.fOutxDsrFlow = FALSE;	// Disable DSR monitoring
	dcb.fDtrControl = DTR_CONTROL_DISABLE;	// Disable DTR monitoring
	dcb.fOutX = FALSE;	// Disable XON/XOFF for transmission
	dcb.fInX = FALSE;	// Disable XON/XOFF for receiving
	dcb.fRtsControl = RTS_CONTROL_DISABLE;	// Disable RTS (Ready To Send)
	dcb.fBinary = TRUE;	// muss immer "TRUE" sein!
	dcb.fErrorChar = FALSE;
	dcb.fNull = FALSE;

	if (!SetCommState(h, &dcb)) {
		fprintf(stderr, "[ptz][%s]: %s SetCommState fault!, err=%d\n", name, __FUNCTION__, GetLastError());
		return 0;
	}

	// timeouts
	COMMTIMEOUTS timeout;
	if (!GetCommTimeouts(h, &timeout)) {
		fprintf(stderr, "[ptz][%s]: %s GetCommTimeouts fault!, err=%d\n", name, __FUNCTION__, GetLastError());
		return 0;
	}

	timeout.ReadIntervalTimeout = 100;
	timeout.ReadTotalTimeoutConstant = 10000;	// 5
	timeout.ReadTotalTimeoutMultiplier = 500;
	timeout.WriteTotalTimeoutConstant = 1000;
	timeout.WriteTotalTimeoutMultiplier = 500;
	if (!SetCommTimeouts(h, &timeout)) {
		fprintf(stderr, "[ptz][%s]: %s SetCommTimeouts fault!, err=%d\n", name, __FUNCTION__, GetLastError());
		return 0;
	}

	serial_t *s = new serial_t;
	s->serial = h;
	s->name = strdup(name);

	return s;
}

void serial_close(serial_t *s)
{
	CloseHandle(s->serial);
	free(s->name);
	delete s;
}

int serial_write(serial_t *s, const void *data, int len)
{
	DWORD bytes;
	if (!WriteFile(s->serial, data, len, &bytes, 0)) {
		fprintf(stderr, "[ptz][%s]: %s: WriteFile fault, err=%d\n", s->name, __FUNCTION__, GetLastError());
		return -1;
	}
	else {
		return bytes;
	}
}

int serial_read(serial_t *s, void *buf, int buf_len)
{
	DWORD bytes;
	if (!ReadFile(s->serial, buf, buf_len, &bytes, 0)) {
		fprintf(stderr, "[ptz][%s]: %s: ReadFile fault, err=%d\n", s->name, __FUNCTION__, GetLastError());
		return -1;
	}
	else {
		return bytes;
	}
}
