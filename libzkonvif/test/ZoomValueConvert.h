#pragma once

#include "../../common/KVConfig.h"
#include "polyfit.h"

/** 云台倍率与 ptz_zoom_get 结果之间的关系 */
class ZoomValueConvert
{
	KVConfig *cfg_;
	double factors_[6];	// 多项式系数

public:
	ZoomValueConvert(KVConfig *cfg);
	~ZoomValueConvert(void);

	// 根据 zv (ptz_zoom_get()的返回) ，计算倍率
	double mp_zoom(int zv);

private:
	// 加载系数
	int load_factors();
};
