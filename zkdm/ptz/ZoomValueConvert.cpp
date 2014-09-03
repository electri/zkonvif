#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "ZoomValueConvert.h"
#include <algorithm>

#ifdef WIN32
#	pragma warning(disable: 4996)
#endif

ZoomValueConvert::ZoomValueConvert(KVConfig *cfg)
	: cfg_(cfg)
{
	load_factors();
}

ZoomValueConvert::~ZoomValueConvert(void)
{
}

typedef std::vector<double> VD;
int ZoomValueConvert::load_factors()
{
	/*
			v =
			   0    5638    8529   10336   11445   12384   13011   13637   14119   14505   14914   15179   15493   15733   15950   16119   16288   16384
			z = 
			   1 	 2      3		4		5		6		7		8		9		10		11		12		13		14		15		16		17		18
	 */

	const char *_vz = "1,0;2,5638;3,8529;4,10336;5,11445;6,12384;7,13011;8,13637;9,14119;10,14505;11,14914;12,15179;13,15493;14,15733;15,15950;16,16119;17,16288;18,16384";

	// 从配置文件加载倍率与zoom value之间的关系，并且拟合出多项式的系数
	const char *s = cfg_->get_value("cam_trace_zm_factors", _vz);
	char *factors = strdup(s);

	VD vs, zs;

	char *p = strtok(factors, ";");
	while (p) {
		int v, z;
		if (sscanf(p, "%d,%d", &v, &z) == 2) {
			vs.push_back(v * 1.0);
			zs.push_back(z * 1.0);
		}

		p = strtok(0, ";");
	}
	free(factors);

	double *pzs = (double*)malloc(zs.size()*sizeof(double));
	double *pvs = (double*)malloc(vs.size()*sizeof(double));
	int i = 0;
	for (VD::const_iterator it = vs.begin(); it != vs.end(); ++it)
		pvs[i++] = *it;
	i = 0;
	for (VD::const_iterator it = zs.begin(); it != zs.end(); ++it)
		pzs[i++] = *it;

	polyfit(vs.size(), pzs, pvs, 5, factors_);

	return 6;
}

double ZoomValueConvert::mp_zoom(int value)
{
	double x = 0.0;
	double v = value;

	for (int i = 0; i < 6; i++) {
		x += factors_[i] * pow(v, i);
	}

	return x;
}
