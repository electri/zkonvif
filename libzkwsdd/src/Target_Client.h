/** 声明 Target/Client 的接口，删除工作线程与 Impl 直接的耦合
 */

#pragma once

class Target
{
public:
	virtual const char *id() const = 0;
	virtual const char *type() const = 0;
	virtual const char *url() const = 0;
};

class Client
{
public:
	virtual int hello() = 0;
	virtual int bye() = 0;
};