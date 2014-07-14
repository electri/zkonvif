#include "PtzControling.h"
#include "../../common/log.h"
#include "../../common/utils.h"
#include <assert.h>

PtzControllingVisca::CAMERAS PtzControllingVisca::_all_cams;
PtzControllingVisca::PtzControllingVisca(KVConfig *cfg) : cfg_(cfg), zvc_(cfg)
{
	changed_zoom_ = true;
	changed_pos_ = true;

	param_.f = atof(cfg_->get_value("cam_trace_f", "3.5"));
	param_.ccd_size_width = atof(cfg_->get_value("cam_trace_ccd_w", "5.1326"));
	param_.ccd_size_height = atof(cfg_->get_value("cam_trace_ccd_h", "2.8852"));
	param_.pan_min_angle = atof(cfg_->get_value("cam_trace_min_hangle", "0.075"));
	param_.tilt_min_angle = atof(cfg_->get_value("cam_trace_min_vangle", "0.075"));
	param_.pan_max_va = atof(cfg_->get_value("cam_trace_view_hangle", "72.5"));
	param_.tilt_max_va = atof(cfg_->get_value("cam_trace_view_vangle", "44.8"));

	const char *name = cfg_->get_value("ptz_name", 0);
	if (!name)
		name = cfg_->get_value("ptz_serial_name", "COMX");

	name_ = name;

	ptz_name_ = cfg_->get_value("ptz_serial_name", "COMX");
	ptz_addr_ = atoi(cfg_->get_value("ptz_addr", "1"));
}

PtzControllingVisca::~PtzControllingVisca(void)
{
}

int PtzControllingVisca::open()
{
	// FIXME: 需要加锁 ...
	if (_all_cams.find(ptz_name_) == _all_cams.end()) {
		// 打开串口 ...
		SerialDevices *sd = new SerialDevices;
		sd->opened = false;
		
		if (VISCA_open_serial(&sd->com, ptz_name_.c_str()) == VISCA_SUCCESS) {
			sd->opened = true;

			_all_cams[ptz_name_] = sd;

			for (int i = 0; i < 8; i++)
				sd->cams[i].address = -1;

			int m;
			sd->com.broadcast = 0;
			if (VISCA_set_address(&sd->com, &m) == VISCA_SUCCESS) {
				for (int i = 1; i <= m; i++) {
					sd->cams[i].address = m;
					if (VISCA_clear(&sd->com, &sd->cams[i]) == VISCA_SUCCESS) {
						log(LOG_DEBUG, "DEBUG: %s: find ptz addr=%d, com=%s\n", __func__, i, ptz_name_.c_str());
					}
				}
			}
		}
		else {
			_all_cams[ptz_name_] = sd; // 失败了，也填充，此时 opened = false;
		}
	}

	SerialDevices *sd = _all_cams[ptz_name_];
	assert(sd);
	if (sd->opened) {
		if (ptz_addr_ < 8 && sd->cams[ptz_addr_].address == ptz_addr_) {
			// ok
			return 0;
		}
		else {
			log(LOG_ERROR, "ERR: %s: com '%s' opened, but addr %d err\n", __func__, ptz_name_.c_str(), ptz_addr_);
		}
	}
	else {
		log(LOG_ERROR, "ERR: %s: com '%s' NOT opened!!!\n", __func__, ptz_name_.c_str());
	}

	return -1;
}

void PtzControllingVisca::close()
{
	SerialDevices *sd = _all_cams[ptz_name_];
	VISCA_close_serial(&sd->com);

	// TODO: 释放 ...
}

void PtzControllingVisca::setpos(int x, int y, int speed_x, int speed_y)
{
	SerialDevices *sd = _all_cams[ptz_name_];
	if (VISCA_set_pantilt_absolute_position_without_reply(&sd->com, &sd->cams[ptz_addr_], speed_x, speed_y, x, y) == VISCA_FAILURE) {
		log(LOG_ERROR, "ERR: %s: VISCA_set_pantilt_absolute_position for %d-%d faulure!\n", __func__, x, y);
	}
	changed_pos_ = true;
}

int PtzControllingVisca::getpos(int &x, int &y)
{
	SerialDevices *sd = _all_cams[ptz_name_];
	if (changed_pos_) {
		if (VISCA_get_pantilt_position(&sd->com, &sd->cams[ptz_addr_], &x, &y) == VISCA_FAILURE) {
			log(LOG_ERROR, "ERR: %s: VISCA_get_pantilt_position failure!\n", __func__);
			return -1;
		}
		else {
			last_x_ = x, last_y_ = y;
			changed_pos_ = false;
			return 0;
		}
	}
	else {
		x = last_x_, y = last_y_;
		return 0;
	}
}

void PtzControllingVisca::reset()
{
	int x = atoi(cfg()->get_value("ptz_init_x", "0"));
	int y = atoi(cfg()->get_value("ptz_init_y", "0"));
	int z = atoi(cfg()->get_value("ptz_init_z", "5000"));
	setpos(x, y, 30, 30);
	zoom_set(z);
}

void PtzControllingVisca::stop()
{
	SerialDevices *sd = _all_cams[ptz_name_];
	VISCA_set_pantilt_stop(&sd->com, &sd->cams[ptz_addr_], 0, 0);
}

void PtzControllingVisca::left(int s)
{
	SerialDevices *sd = _all_cams[ptz_name_];
	VISCA_set_pantilt_left_without_reply(&sd->com, &sd->cams[ptz_addr_], s, s);
	changed_pos_ = true;
}

void PtzControllingVisca::up(int s)
{
	SerialDevices *sd = _all_cams[ptz_name_];
	VISCA_set_pantilt_up_without_reply(&sd->com, &sd->cams[ptz_addr_], s, s);
	changed_pos_ = true;
}

void PtzControllingVisca::down(int s)
{
	SerialDevices *sd = _all_cams[ptz_name_];
	VISCA_set_pantilt_down_without_reply(&sd->com, &sd->cams[ptz_addr_], s, s);
	changed_pos_ = true;
}

void PtzControllingVisca::right(int s)
{
	SerialDevices *sd = _all_cams[ptz_name_];
	VISCA_set_pantilt_right_without_reply(&sd->com, &sd->cams[ptz_addr_], s, s);
	changed_pos_ = true;
}

void PtzControllingVisca::zoom_set(int z)
{
	SerialDevices *sd = _all_cams[ptz_name_];
	VISCA_set_zoom_value_without_reply(&sd->com, &sd->cams[ptz_addr_], z);
	changed_zoom_ = true;
}

int PtzControllingVisca::zoom_get(int &z)
{
	if (changed_zoom_) {
		unsigned short v;
		SerialDevices *sd = _all_cams[ptz_name_];
		if (VISCA_get_zoom_value(&sd->com, &sd->cams[ptz_addr_], &v) == VISCA_FAILURE) {
			log(LOG_ERROR, "ERR: %s: VISCA_get_zoom_value faulure!\n", __func__);
			return -1;
		}
		z = v;
		last_zoom_ = z;
		changed_zoom_ = false;
		return 0;
	}
	else {
		z = last_zoom_;
		return 0;
	}
}

double PtzControllingVisca::getScales()
{
	int zoom;
	if (zoom_get(zoom) == 0)
		return zvc_.mp_zoom(zoom);
	else
		return 1.0;
}

void PtzControllingVisca::preset_set(int n)
{
	SerialDevices *sd = _all_cams[ptz_name_];
	VISCA_memory_set_without_reply(&sd->com, &sd->cams[ptz_addr_], n);
}

void PtzControllingVisca::preset_get(int n)
{
	SerialDevices *sd = _all_cams[ptz_name_];
	VISCA_memory_recall_without_reply(&sd->com, &sd->cams[ptz_addr_], n);
}

void PtzControllingVisca::preset_del(int n)
{
	SerialDevices *sd = _all_cams[ptz_name_];
	VISCA_memory_reset_without_reply(&sd->com, &sd->cams[ptz_addr_], n);
}
