#pragma once

/** 这个用于方便 MyDevice 支持更多的服务 ...
注意： 这里的接口，需要根据 MyDevice 的 GetServices 实际需要进行扩展 .....
*/
class ServiceInf
{
public:
	virtual const char *url() const = 0;	// 所有的服务，都必须有个 url .
	virtual const char *desc() const { return ""; }	// 可选有个描述信息 ..
};
