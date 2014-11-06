#include "../../ptz/ptz.h"
#include <stdio.h>
#include <stdlib.h>
#include <Windows.h>
#include <string>
#include <vector>
#include <sstream>
#include <math.h>
#include "visca.h"

#define TEST_MY_VISCA 1

static double util_now()
{
	return GetTickCount()/1000.0;
}

class TimeUsed
{
	std::string info_;
	double max_, begin_;

public:
	TimeUsed(const char *info, double t = 100.000)
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

#if TEST_MY_VISCA
int main(int argc, const char **argv)
{
	const char *serial_name = "COM1";

	if (argc > 1) {
		serial_name = argv[1];
	}

	fprintf(stderr, "启动测试：使用串口 %s\n\n", serial_name);

	int ret;
	visca_t *visca = visca_open(serial_name, 1);
	if (!visca) {
		fprintf(stderr, "无法打开云台，使用串口 %s\n", serial_name);
		return -1;
	}

	//int sx, sy;
	//ret = visca_get_max_speed(visca, &sx, &sy);
	//if (ret < 0) {
	//	fprintf(stderr, "无法得到云台转动最大速度\n\n");
	//}
	//else {
	//	fprintf(stderr, "云台最大转动速度：%d, %d\n", sx, sy);
	//}

	short x, y;
#define X 300
#define Y 300
#define Z 8000

	{
		ret = visca_setpos_blocked(visca, 0 - X, 0 - Y, 32, 32);
		if (ret < 0) {
			fprintf(stderr, "云台测试失败!!!!\n");
			return -1;
		}
		TimeUsed tu("云台归位");
		fprintf(stderr, "\n测试云台归位： ....");
		ret = visca_setpos_blocked(visca, 0, 0, 36, 36);
		if (ret < 0) {
			fprintf(stderr, "云台测试失败!!!!\n");
			return -1;
		}
		visca_zoom_set_blocked(visca, 0);
		fprintf(stderr, " 用时 %.3f 秒\n", tu.duration());
	}

	{
		fprintf(stderr, "\n测试云台转动....左..");
		ret = visca_left(visca, 3);
		if (ret < 0) {
			fprintf(stderr, "云台测试失败!!!!\n");
			return -1;
		}
		Sleep(3000);
		ret = visca_stop(visca);
		if (ret < 0) {
			fprintf(stderr, "云台测试失败!!!!\n");
			return -1;
		}

		fprintf(stderr, "右..");
		visca_right(visca, 3); 
		Sleep(3000);
		visca_stop(visca);

		fprintf(stderr, "上..");
		visca_up(visca, 3);
		Sleep(3000);
		visca_stop(visca);

		fprintf(stderr, "下..");
		visca_down(visca, 3);
		Sleep(3000);
		visca_stop(visca);
		fprintf(stderr, "  通过\n");
	}

	{
		fprintf(stderr, "\n测试 set_pos / get_pos ....\n");
		{
			TimeUsed tu("set_pos");
			visca_setpos(visca, X, Y, 2, 2);
			fprintf(stderr, "\t set_pos 用时 %.3f 秒\n");
		}
		
		int n = 0;
		do {
			{
				TimeUsed tu("get_pos");
				visca_getpos(visca, &x, &y);
				fprintf(stderr, "\t\t get_pos ret %d, %d，用时 %.3f 秒\n", x, y, tu.duration());
				n++;
			}
			Sleep(200);
		} while ((abs(x-X) > 5 || abs(y-Y) > 5) && n < 100);

		if (n >= 100) {
			fprintf(stderr, "嗯，这个云台转动不到 %d-%d ???\n", X, Y);
		}
		else if (n < 3) {
			fprintf(stderr, "嗯，这个云台不支持 set_pos 未完成时获取云台位置\n");
		}
		else {
			fprintf(stderr, "完美支持 set_pos/get_pos\n");
		}
	}

	{
		fprintf(stderr, "\n测试 set_zoom / get_zoom ...\n");
		visca_zoom_set_blocked(visca, 5000);
		Sleep(3000);	// FIXME: 貌似某些云台 ...
		{
			TimeUsed tu("");
			visca_zoom_set_blocked(visca, 0);
			fprintf(stderr, "\t zoom 从 5000 到 0 使用了 %.3f 秒\n", tu.duration());
			Sleep(3000); // FIXME: ...
		}

		visca_zoom_set(visca, Z);
		int n = 0;
		int z = 0;
		do {
			{
				TimeUsed tu("get");
				visca_zoom_get(visca, &z);
				fprintf(stderr, "\t\t get_zoom ret %d, 用时 %.3f 秒\n", z, tu,double());
				n++;
			}

			Sleep(100);
		} while (abs(z - Z) > 10 && n < 100);

		if (n >= 100) {
			fprintf(stderr, "嗯，这个云台的 set_zoom，必须等待执行完成后，才能发出 get_zoom 命令\n");
		}
		else if (n < 3) {
			fprintf(stderr, "嗯，这个云台不支持 set_zoom 未到位时，获取当前zoom值\n");
		}
		else {
			fprintf(stderr, "完美支持 set_zoom/get_zoom\n");
		}
	}

#if 0
	visca_left(visca, 1);
	Sleep(5000);
	visca_up(visca, 1);
	Sleep(5000);
	visca_right(visca, 1);
	Sleep(5000);
	visca_down(visca, 1);
	Sleep(5000);
	visca_stop(visca);
#endif 

	visca_close(visca);

	return 0;
}

#else
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
#endif

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
