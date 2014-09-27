/** 设备中服务注册到本级的 dm . */

#pragma once

#ifdef __cplusplus
extern "C" {
#endif // c++

typedef struct lc_regdesc_t
{
	const char *ns; // 服务类别，如 media, ptz, recording ...
	const char *url; // url 
	const char *desc; // 服务描述，必须使用 utf8 ...，或者 null
	const char *service_name;	// 如果是“服务”必须为服务名字，如果不是服务，为 null
} lc_regdesc_t;

/** 注册到本级 dm：
  		assert(desc->ns && desc->url);
 */
void lc_reg(const lc_regdesc_t *desc);
void lc_unreg();

#ifdef __cplusplus
}
#endif // c++

