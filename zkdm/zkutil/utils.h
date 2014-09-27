#pragma once

#ifdef __cplusplus
extern "C" {
#endif // c++


#		ifdef DLL_EXPORT
#			define LIBZKUTIL_SCOPE	__declspec(dllexport)
#		endif

#ifndef LIBZKUTIL_SCOPE
#	define LIBZKUTIL_SCOPE
#endif 

LIBZKUTIL_SCOPE const char *util_get_myip_real();
LIBZKUTIL_SCOPE const char *util_get_myip();
LIBZKUTIL_SCOPE const char *util_get_mymac();
LIBZKUTIL_SCOPE const char *util_get_nic_name();

#ifdef __cplusplus
}
#endif // c++

