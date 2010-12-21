#ifndef _EVEMU_IMPL_H
#define _EVEMU_IMPL_H

#include <evemu.h>
#include <linux/uinput.h>

#define EVPLAY_NBITS	KEY_CNT
#define EVPLAY_NBYTES	((EVPLAY_NBITS + 7) / 8)

struct evemu_device {
	int version_major, version_minor;
	char name[UINPUT_MAX_NAME_SIZE];
	struct input_id id;
	unsigned char mask[EV_CNT][EVPLAY_NBYTES];
	int bytes[EV_CNT];
	struct input_absinfo abs[ABS_CNT];
};

#endif
