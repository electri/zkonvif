#include "../../ptz/ptz.h"
#include <stdio.h>
#include <stdlib.h>
#include <Windows.h>
#include <string>
#include <vector>
#include <sstream>
#include <math.h>

static double util_now()
{
	return GetTickCount()/1000.0;
}

class TimeUsed
{
	std::string info_;
	double max_, begin_;

public:
	TimeUsed(const char *info, double t = 0.100)
	{
		begin_ = util_now();
		info_ = info;
		max_ = t;
	}

	double duration() const
	{
		return util_now() - begin_;
	}

	bool is_timeout() const
	{
		return duration() >= max_;
	}

	~TimeUsed()
	{
		double now = util_now();
		if (now - begin_ >= max_) {
			fprintf(stderr, "ERR: %s 超时, 用了 %.3f 秒\n", info_.c_str(), now - begin_);
		}
	}
};

typedef int (*PFN_test)(ptz_t *ptz, std::ostream &os);

static int test_left(ptz_t *ptz, std::ostream &info);
static int test_stop(ptz_t *ptz, std::ostream &info);
static int test_pos(ptz_t *ptz, std::ostream &info);
static int test_zoom(ptz_t *ptz, std::ostream &info);

struct Func
{
	const char *name;
	PFN_test func;
};

static Func _funcs[] = {
	{ "left", test_left, },
	{ "stop", test_stop, },
	{ "set_pos/get_pos", test_pos, },
	{ "set_zoom/get_zoom", test_zoom, },
	{ 0, 0 },
};

struct Result
{
	std::string name;
	int code;
	std::string info;
};

static std::vector<Result> _results;

class Exec
{
public:
	Exec(const char *name, PFN_test func, ptz_t *ptz)
	{
		Result r;
		r.name = name;

		fprintf(stderr, "测试：%s ....... ", name);

		std::stringstream ss;
		r.code = func(ptz, ss);
		r.info = ss.str();

		fprintf(stderr, ", 返回 %d\n", r.code);

		_results.push_back(r);
	}
};

int main (int argc, char **argv)
{
	ptz_t *ptz = ptz_open_with_config("ptz.config");
	if (!ptz) {
		MessageBoxA(0, "无法打开云台，请检查 ptz.config 中的 ptz_serial_name 指定的串口是否被占用？", "错误", MB_OK | MB_ICONHAND);
		return -1;
	}

	fprintf(stderr, "开始验证云台，测试 left, stop, get_pos, get_zoom, set_pos, set_zoom\n\n");

	Func *f = _funcs;
	while (f->name) {
		Exec e(f->name, f->func, ptz);
		f++;
	}

	std::stringstream ss;
	for (std::vector<Result>::const_iterator it = _results.begin(); it != _results.end(); ++it) {
		ss << "测试: '" << it->name << "', ";
		if (it->code == 0) {
			ss << "成功";
		}
		else if (it->code == -2) {
			ss << "超时";
		}
		else if (it->code == -1) {
			ss << "失败";
		}
		else {
			ss << "未知错误";
		}

		ss << std::endl;
	}

	MessageBoxA(0, ss.str().c_str(), "测试结果", MB_OK | MB_ICONINFORMATION);

	return 0;
}

static int test_left(ptz_t *ptz, std::ostream &os)
{
	TimeUsed tu(__FUNCTION__);
	int rc = ptz_left(ptz, 1);
	if (rc < 0) {
		return -1;
	}
	if (tu.is_timeout()) {
		return -2;
	}
	return 0;
}

static int test_stop(ptz_t *ptz, std::ostream &os)
{
	TimeUsed tu(__FUNCTION__);
	int rc = ptz_stop(ptz);
	if (rc < 0) {
		return -1;
	}
	if (tu.is_timeout()) {
		return -2;
	}
	return 0;
}

static int test_zoom(ptz_t *ptz, std::ostream &os)
{
	int rc;
	int z;
#define TO_Z 10000

	rc = ptz_set_zoom_with_reply(ptz, 0);
	if (rc < 0) {
		return -1;
	}

	double t1 = util_now();
	
	rc = ptz_set_zoom(ptz, TO_Z);
	if (rc < 0) {
		return -1;
	}

	rc = ptz_get_zoom(ptz, &z);
	if (rc < 0) {
		return -1;
	}

	double t2 = util_now();
	if (t2 - t1 > 0.500) {
		fprintf(stderr, "ERR: set_zoom/get_zoom 超时，使用了 %.3f 秒\n", t2 - t1);
		return -2;
	}

	while (1) {
		fprintf(stderr, "INFO: get_zoom ret %d\n", z);

		if (abs(z - TO_Z) < 10) {
			break;
		}

		rc = ptz_get_zoom(ptz, &z);
		if (rc < 0) {
			return -1;
		}
	}

	double t3 = util_now();
	fprintf(stderr, "INFO: set_zoom using %.3f 秒\n", t3 - t1);

	return 0;
}

static int test_pos(ptz_t *ptz, std::ostream &os)
{
#define TO_X -600
#define TO_Y -400

	int x, y;
	int rc;

	rc = ptz_set_pos_with_reply(ptz, 400, 400, 36, 36);
	if (rc < 0) {
		return -1;
	}

	double t1 = util_now();

	rc = ptz_set_pos(ptz, TO_X, TO_Y, 36, 36);
	if (rc < 0) {
		return -1;
	}

	rc = ptz_get_pos(ptz, &x, &y);
	if (rc < 0) {
		return -1;
	}

	double t2 = util_now();
	if (t2 - t1 > 0.500) {
		fprintf(stderr, "ERR: set_pos/get_pos 超时，使用了 %.3f 秒\n", t2 - t1);
		return -2;
	}

	while (1) {
		fprintf(stderr, "INFO: get_pos ret {%d - %d}\n", x, y);

		if (abs(x - TO_X) < 5 && abs(y - TO_Y) < 5) {
			break;
		}

		rc = ptz_get_pos(ptz, &x, &y);
		if (rc < 0) {
			return -1;
		}
	}

	double t3 = util_now();
	fprintf(stderr, "INFO: set_pos using %.3f 秒\n", t3 - t1);

	return 0;
}
