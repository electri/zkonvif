#include "PtzControling.h"
#include "../../common/log.h"
#include "../../common/utils.h"


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
}

PtzControllingVisca::~PtzControllingVisca(void)
{
}

int PtzControllingVisca::open()
{
	const char *serial_name = cfg()->get_value("ptz_serial_name", "COMX");
	if (VISCA_open_serial(&visca_, serial_name) == VISCA_SUCCESS) {
		int m;
		visca_.broadcast = 0;
		if (VISCA_set_address(&visca_, &m) == VISCA_SUCCESS) {
			cam_.address = m;
			VISCA_clear(&visca_, &cam_);
			return 0;
		} 
		else {
			log(LOG_ERROR, "ERR: %s: VISCA_set_address for %s err\n", __func__, serial_name);
			return -1;
		}
	}
	else {
		log(LOG_ERROR, "ERR: %s: VISCA_open_serial for %s err\n", __func__, serial_name);
		return -1;
	}
}

void PtzControllingVisca::close()
{
	VISCA_close_serial(&visca_);
}

void PtzControllingVisca::setpos(int x, int y, int speed_x, int speed_y)
{
	if (VISCA_set_pantilt_absolute_position_without_reply(&visca_, &cam_, speed_x, speed_y, x, y) == VISCA_FAILURE) {
		log(LOG_ERROR, "ERR: %s: VISCA_set_pantilt_absolute_position for %d-%d faulure!\n", __func__, x, y);
	}
	changed_pos_ = true;
}

int PtzControllingVisca::getpos(int &x, int &y)
{
	if (changed_pos_) {
		if (VISCA_get_pantilt_position(&visca_, &cam_, &x, &y) == VISCA_FAILURE) {
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
	VISCA_set_pantilt_stop(&visca_, &cam_, 0, 0);
}

void PtzControllingVisca::left(int s)
{
	VISCA_set_pantilt_left_without_reply(&visca_, &cam_, s, s);
	changed_pos_ = true;
}

void PtzControllingVisca::up(int s)
{
	VISCA_set_pantilt_up_without_reply(&visca_, &cam_, s, s);
	changed_pos_ = true;
}

void PtzControllingVisca::down(int s)
{
	VISCA_set_pantilt_down_without_reply(&visca_, &cam_, s, s);
	changed_pos_ = true;
}

void PtzControllingVisca::right(int s)
{
	VISCA_set_pantilt_right_without_reply(&visca_, &cam_, s, s);
	changed_pos_ = true;
}

void PtzControllingVisca::zoom_set(int z)
{
	VISCA_set_zoom_value_without_reply(&visca_, &cam_, z);
	changed_zoom_ = true;
}

int PtzControllingVisca::zoom_get(int &z)
{
	if (changed_zoom_) {
		unsigned short v;
		if (VISCA_get_zoom_value(&visca_, &cam_, &v) == VISCA_FAILURE) {
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
