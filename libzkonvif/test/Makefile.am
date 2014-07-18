bin_PROGRAMS= test_target_dm test_client_dm test_normal_service

test_target_dm_CFLAGS=-Wno-psabi -Wall
test_target_dm_SOURCES= test_target_dm.cpp \
						../../common/utils.cpp ../../common/KVConfig.cpp \
						../src/linux/sysperf.cpp MyDevice.cpp \
						MyDeviceDiscovery.cpp MyPtz.cpp \
						MyEvent.cpp PtzControling.cpp \
						ZoomValueConvert.cpp polyfit.cpp
test_target_dm_LDADD= ../src/libzkonvif.a -lccgnu2 -lssl -lcrypto -lvisca

test_client_dm_SOURCES= test_client_dm.cpp \
						../../common/utils.cpp ../../common/KVConfig.cpp \
						test_client_devicemgrt.cpp \
						test_client_dm.event.cpp \
						test_client_dm.ptz.cpp
test_client_dm_LDADD= ../src/libzkonvif.a -lccgnu2


test_normal_service_SOURCES=test_normal_service.cpp ../../common/utils.cpp
test_normal_service_LDADD=	../libzkreg/libzkreg.a ../src/libzkonvif.a -lccgnu2
