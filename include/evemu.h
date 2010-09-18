/*****************************************************************************
 *
 * evemu - Kernel device emulation
 *
 * Copyright (C) 2010 Henrik Rydberg <rydberg@euromail.se>
 * Copyright (C) 2010 Canonical Ltd.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice (including the next
 * paragraph) shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 ****************************************************************************/

#ifndef _EVPLAY_H
#define _EVPLAY_H

#include <linux/uinput.h>
#include <stdio.h>

#define EVPLAY_NBITS	KEY_CNT
#define EVPLAY_NBYTES	((EVPLAY_NBITS + 7) / 8)

struct evemu_device {
	char name[UINPUT_MAX_NAME_SIZE];
	struct input_id id;
	unsigned char mask[EV_CNT][EVPLAY_NBYTES];
	int bytes[EV_CNT];
	struct input_absinfo abs[ABS_CNT];
};

static inline int evemu_has(const struct evemu_device *dev,
			     int type, int code)
{
	return (dev->mask[type][code >> 3] >> (code & 7)) & 1;
}

int evemu_extract(struct evemu_device *dev, int fd);
int evemu_write(const struct evemu_device *dev, FILE *fp);
int evemu_read(struct evemu_device *dev, FILE *fp);

int evemu_write_event(FILE *fp, const struct input_event *ev);
int evemu_read_event(FILE *fp, struct input_event *ev);

int evemu_record(FILE *fp, int fd, int ms);
int evemu_play(FILE *fp, int fd);

int evemu_create(const struct evemu_device *dev, int fd);
void evemu_destroy(int fd);

#endif
