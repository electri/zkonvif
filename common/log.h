#pragma once

#include <stdio.h>
#include <stdarg.h>

#define LOG_FILENAME "libzkwsdd.log"
#define CONSOLE 1

#ifdef WIN32
#	define __func__ __FUNCTION__
#endif

#define LOG_FAULT 0
#define LOG_ERROR 1
#define LOG_WARNING 2
#define LOG_INFO 3
#define LOG_DEBUG 4

inline void log_init()
{
	FILE *fp = fopen(LOG_FILENAME, "w");
	if (fp) {
		fprintf(fp, "========= start =========\n");
		fclose(fp);
	}
}

inline void log(int reserved, int level, va_list args, const char *fmt)
{
	FILE *fp = fopen(LOG_FILENAME, "a");
	if (fp) {
		char buf[1024];
		vsnprintf(buf, sizeof(buf), fmt, args);
		fprintf(fp, "%s", buf);
#if CONSOLE
		fprintf(stderr, "%s", buf);
#endif // show on terminal console
		fclose(fp);
	}
}

inline void log(int level, const char *fmt, ...)
{
	va_list args;
	va_start(args, fmt);
	log(0, level, args, fmt);
	va_end(args);
}

inline void log(const char *fmt, ...)
{
	va_list args;
	va_start(args, fmt);
	log(0, LOG_DEBUG, args, fmt);
	va_end(args);
}
