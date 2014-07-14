#ifdef WIN32

/** TODO: 原来 windows 也有个 WMIC 接口啊，将来应该修改使用 wmic.exe + pipe 方式 */

#include "sysperf.h"
#include "../../../common/log.h"
#include <comutil.h>
#include <assert.h>
#include <stdio.h>

#pragma comment(lib, "comsuppw.lib")

SysPerf::SysPerf(const char *dp, const char *nic)
{
	dp_ = strdup(dp);
	nic_ = strdup(nic);

	last_stamp_ = -1;

	quit_ = false;
	disk_tot_ = 1000000000000.0, disk_used_ = 0.1;
	net_sr_ = net_rr_ = 0.0;
	start();
}

SysPerf::~SysPerf()
{
	quit_ = true;
	join();
	free(dp_);
	free(nic_);
}

void SysPerf::run()
{
	CoInitialize(0);
	IWbemLocator *locator = 0;
	IWbemServices *services = 0;

	HRESULT hr = CoCreateInstance(CLSID_WbemLocator, 0, CLSCTX_INPROC_SERVER, IID_IWbemLocator, (void**)&locator);
	if (hr != S_OK) {
		log(LOG_ERROR, "%s: can't create CLSID_WbemLocator objects, hr=%08x\n", __func__, hr);
	}

	CoInitializeSecurity(
		NULL,
		-1,                          // COM authentication
		NULL,                        // Authentication services
		NULL,                        // Reserved
		RPC_C_AUTHN_LEVEL_DEFAULT,   // Default authentication 
		RPC_C_IMP_LEVEL_IMPERSONATE, // Default Impersonation  
		NULL,                        // Authentication info
		EOAC_NONE,                   // Additional capabilities 
		NULL                         // Reserved
		);

	hr = locator->ConnectServer(BSTR(L"ROOT\\CIMV2"), 0, 0, 0, 0, 0, 0, &services);
	if (hr != S_OK) {
		log(LOG_ERROR, "%s: IWebLocator::ConnectServer err, hr=%08x\n", __func__, hr);
		locator->Release();
		locator = 0;
	}

	hr = CoSetProxyBlanket(services, RPC_C_AUTHN_WINNT, RPC_C_AUTHZ_NONE, 0, RPC_C_AUTHN_LEVEL_CALL, RPC_C_IMP_LEVEL_IMPERSONATE, 0, EOAC_NONE);
	if (hr != S_OK) {
		log(LOG_ERROR, "%s: CoSetProxyBlanket err, hr=%08x\n", __func__, hr);
		services->Release(), services = 0;
		locator->Release(), locator = 0;
	}

	while (!quit_) {
		once(services);
		sleep(1000);	// 每隔1秒刷新 ...
	}

	if (services)
		services->Release(), services = 0;

	if (locator)
		locator->Release(), locator = 0;

	CoUninitialize();
}

void SysPerf::once(IWbemServices *s)
{
	update_cpu(s);
	update_mem(s);
	update_disk(s);
	update_net(s);

	fprintf(stderr, "cpu: %%%.3f, mem: tot=%.3f, used=%.3f\n, \tdisk: tot=%.3f, used=%.3f\n, \tnet: sr=%.3f, rr=%.3f\n", cpurate_, 
			mem_tot_ / 1000000.0, mem_used_ / 1000000.0,
			disk_tot_ / 1000000.0, disk_used_ / 1000000.0,
			net_sr_, net_rr_);
}

void SysPerf::update_cpu(IWbemServices *s)
{
	IEnumWbemClassObject *em = 0;
	IWbemClassObject *obj = 0;

	// cpu
	HRESULT hr = s->ExecQuery(bstr_t("WQL"), bstr_t("SELECT PercentProcessorTime FROM Win32_PerfFormattedData_PerfOS_Processor where Name='_Total'"),
							  WBEM_FLAG_FORWARD_ONLY | WBEM_FLAG_RETURN_IMMEDIATELY, 0, &em);
	while (1) {
		ULONG got;
		hr = em->Next(WBEM_INFINITE, 1, &obj, &got);
		if (got == 0)
			break;

		VARIANT val;
		VariantInit(&val);

		hr = obj->Get(L"PercentProcessorTime", 0, &val, 0, 0);
		/// Note  When querying for property values with a uint64 or sint64 data type in a scripting language like VBScript, WMI returns string values.
		///    真扯淡！！ .
		assert(val.vt == VT_BSTR);

		cpurate_ = atof((char*)bstr_t(val.bstrVal));

		obj->Release();
	}

	em->Release();
}

void SysPerf::update_mem(IWbemServices *s)
{
	IEnumWbemClassObject *em = 0;
	IWbemClassObject *obj = 0;

	HRESULT hr = s->ExecQuery(bstr_t("WQL"), bstr_t("SELECT CommittedBytes,CommitLimit FROM Win32_PerfFormattedData_PerfOS_Memory"),
							  WBEM_FLAG_FORWARD_ONLY | WBEM_FLAG_RETURN_IMMEDIATELY, 0, &em);
	while (1) {
		ULONG got;
		hr = em->Next(WBEM_INFINITE, 1, &obj, &got);
		if (got == 0)
			break;

		VARIANT val;
		VariantInit(&val);

		hr = obj->Get(L"CommittedBytes", 0, &val, 0, 0);
		assert(val.vt == VT_BSTR);
		mem_used_ = atof((char*)bstr_t(val.bstrVal));

		VariantInit(&val);
		hr = obj->Get(L"CommitLimit", 0, &val, 0, 0);
		assert(val.vt == VT_BSTR);
		mem_tot_ = atof((char*)bstr_t(val.bstrVal));

		obj->Release();
	}

	em->Release();
}

void SysPerf::update_net(IWbemServices *s)
{
#if 0
	IEnumWbemClassObject *em = 0;
	IWbemClassObject *obj = 0;

	// TODO: 需要指定网卡名字， ....
	// XXX：崩溃了，在 Win32_PerfFormattedData_Tcpip_NetworkInterface 中的 name 是
	//		"Intel[R] Centrino[R] Advanced-N 6205"
	//		而 GetAdapterInfo 得到的，是
	//		"Intel(R) Centrino(R) Advanced-N 6205" 
	//		直接到 util_get_nic_name() 设置环境变量吧，！！！！！！ 
	//		
	//		感觉这里是：intel 的驱动名字设置了一份，但写入性能计数器，有用了另一套名字，狗屎 ....
	// 
	char query[512];
	//snprintf(query, sizeof(query), "select BytesReceivedPersec, BytesSentPersec from Win32_PerfFormattedData_Tcpip_NetworkInterface where Name='%s'", nic_);
	snprintf(query, sizeof(query), "select BytesReceivedPersec,BytesSentPersec,Name from Win32_PerfFormattedData_Tcpip_NetworkInterface");
	HRESULT hr = s->ExecQuery(bstr_t("WQL"), bstr_t(query), WBEM_FLAG_FORWARD_ONLY | WBEM_FLAG_RETURN_IMMEDIATELY, 0, &em);
	while (1) {
		ULONG got;
		hr = em->Next(WBEM_INFINITE, 1, &obj, &got);
		if (got == 0)
			break;

		VARIANT val;
		VariantInit(&val);

		hr = obj->Get(L"Name", 0, &val, 0, 0);
		if (hr == S_OK) {
			assert(val.vt == VT_BSTR);

			std::string p = (char*)bstr_t(val.bstrVal);
			if (strcmp(p.c_str(), nic_) == 0) {
				VariantInit(&val);
				hr = obj->Get(L"BytesReceivedPersec", 0, &val, 0, 0);

				hr = obj->Get(L"BytesSentPersec", 0, &val, 0, 0);
			}
		}

		obj->Release();
	}
	em->Release();
#else
	const char *cmd = "chcp 437& netstat -e";
	__int64 sent = -1, recv;

	FILE *fp = _popen(cmd, "r");
	if (fp) {
		while (!feof(fp)) {
			char buf[256];
			char *p = fgets(buf, sizeof(buf), fp);
			if (!p) continue;

			char name[64];
			if (sscanf(p, "%s %I64d %I64d", name, &recv, &sent) == 3) {
				if (!stricmp("Bytes", name)) {
					break;
				}
			}
		}
		_pclose(fp);
	}

	if (sent > 0) {
		double curr = GetTickCount() / 1000.0;
		if (last_stamp_ > 0) {
			net_rr_ = (recv - last_r_) / (curr - last_stamp_);
			net_sr_ = (sent - last_s_) / (curr - last_stamp_);
		}

		last_stamp_ = curr;
		last_r_ = recv;
		last_s_ = sent;
	}

#endif // 
}

void SysPerf::update_disk(IWbemServices *s)
{
	// 检查哪个分区？
	char query[512];
	ULARGE_INTEGER tot, freed;
	if (GetDiskFreeSpaceEx(this->dp_, 0, &tot, &freed)) {
		disk_tot_ = tot.QuadPart;
		disk_used_ = tot.QuadPart - freed.QuadPart;
	}
}

#endif // 
