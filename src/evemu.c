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

#include "evemu.h"
#include <string.h>
#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <poll.h>

#define SYSCALL(call) while (((call) == -1) && (errno == EINTR))

static void copy_bits(unsigned char *mask, const unsigned long *bits, int bytes)
{
	int i;
	for (i = 0; i < bytes; i++) {
		int pos = 8 * (i % sizeof(long));
		mask[i] = (bits[i / sizeof(long)] >> pos) & 0xff;
	}
}

int evemu_extract(struct evemu_device *dev, int fd)
{
	unsigned long bits[64];
	int rc, i;

	memset(dev, 0, sizeof(*dev));

	SYSCALL(rc = ioctl(fd, EVIOCGNAME(sizeof(dev->name)), dev->name));
	if (rc < 0)
		return rc;
	for (i = 0; i < sizeof(dev->name); i++)
		if (isspace(dev->name[i]))
			dev->name[i] = '-';

	SYSCALL(rc = ioctl(fd, EVIOCGID, &dev->id));
	if (rc < 0)
		return rc;

	for (i = 0; i < EV_CNT; i++) {
		SYSCALL(rc = ioctl(fd, EVIOCGBIT(i, sizeof(bits)), bits));
		if (rc < 0)
			continue;
		copy_bits(dev->mask[i], bits, rc);
		dev->bytes[i] = rc;
	}

	for (i = 0; i < ABS_CNT; i++) {
		if (!evemu_has(dev, EV_ABS, i))
			continue;
		SYSCALL(rc = ioctl(fd, EVIOCGABS(i), &dev->abs[i]));
		if (rc < 0)
			return rc;
	}

	return 0;
}

static void write_mask(FILE * fp, int index,
		       const unsigned char *mask, int bytes)
{
	int i;
	for (i = 0; i < bytes; i += 8)
		fprintf(fp, "B: %02x %02x %02x %02x %02x %02x %02x %02x %02x\n",
			index, mask[i], mask[i + 1], mask[i + 2], mask[i + 3],
			mask[i + 4], mask[i + 5], mask[i + 6], mask[i + 7]);
}

static void write_abs(FILE *fp, int index, const struct input_absinfo *abs)
{
	fprintf(fp, "A: %02x %d %d %d %d\n", index,
		abs->minimum, abs->maximum, abs->fuzz, abs->flat);
}

int evemu_write(const struct evemu_device *dev, FILE *fp)
{
	int i;

	fprintf(fp, "N: %s\n", dev->name);

	fprintf(fp, "I: %04x %04x %04x %04x\n",
		dev->id.bustype, dev->id.vendor,
		dev->id.product, dev->id.version);

	for (i = 0; i < EV_CNT; i++)
		write_mask(fp, i, dev->mask[i], dev->bytes[i]);

	for (i = 0; i < ABS_CNT; i++)
		if (evemu_has(dev, EV_ABS, i))
			write_abs(fp, i, &dev->abs[i]);
}

static void read_mask(struct evemu_device *dev, FILE *fp)
{
	unsigned int mask[8];
	int index, i;
	while (fscanf(fp, "B: %02x %02x %02x %02x %02x %02x %02x %02x %02x\n",
		      &index, mask + 0, mask + 1, mask + 2, mask + 3,
		      mask + 4, mask + 5, mask + 6, mask + 7) > 0) {
		for (i = 0; i < 8; i++)
			dev->mask[index][dev->bytes[index]++] = mask[i];
	}
}

static void read_abs(struct evemu_device *dev, FILE *fp)
{
	struct input_absinfo abs;
	int index;
	while (fscanf(fp, "A: %02x %d %d %d %d\n", &index,
		      &abs.minimum, &abs.maximum, &abs.fuzz, &abs.flat) > 0)
		dev->abs[index] = abs;
}

int evemu_read(struct evemu_device *dev, FILE *fp)
{
	unsigned bustype, vendor, product, version;
	int ret;

	memset(dev, 0, sizeof(*dev));

	ret = fscanf(fp, "N: %s\n", dev->name);
	if (ret <= 0)
		return ret;

	ret = fscanf(fp, "I: %04x %04x %04x %04x\n",
		     &bustype, &vendor, &product, &version);
	if (ret <= 0)
		return ret;

	dev->id.bustype = bustype;
	dev->id.vendor = vendor;
	dev->id.product = product;
	dev->id.version = version;

	read_mask(dev, fp);

	read_abs(dev, fp);

	return 1;
}

int evemu_write_event(FILE *fp, const struct input_event *ev)
{
	return fprintf(fp, "E: %lu.%06u %04x %04x %d\n",
		       ev->time.tv_sec, (unsigned)ev->time.tv_usec,
		       ev->type, ev->code, ev->value);
}

int evemu_record(FILE *fp, int fd, int ms)
{
        struct pollfd fds = { fd, POLLIN, 0 };
	struct input_event ev;
	int ret;

	while (poll(&fds, 1, ms) > 0) {
		SYSCALL(ret = read(fd, &ev, sizeof(ev)));
		if (ret < 0)
			return ret;
		if (ret == sizeof(ev))
			evemu_write_event(fp, &ev);
	}

	return 0;
}

int evemu_read_event(FILE *fp, struct input_event *ev)
{
	unsigned long sec;
	unsigned usec, type, code;
	int value;
	int ret = fscanf(fp, "E: %lu.%06u %04x %04x %d\n",
			 &sec, &usec, &type, &code, &value);
	ev->time.tv_sec = sec;
	ev->time.tv_usec = usec;
	ev->type = type;
	ev->code = code;
	ev->value = value;
	return ret;
}

int evemu_play(FILE *fp, int fd)
{
	struct input_event prev, ev;
	long check = 0, usec;
	int ret;

	memset(&prev, 0, sizeof(prev));
	while (evemu_read_event(fp, &ev) > 0) {
		if (!prev.time.tv_sec)
			prev = ev;
		usec = 1000000L * (ev.time.tv_sec - prev.time.tv_sec);
		usec += ev.time.tv_usec - prev.time.tv_usec;
		if (usec - check > 500) {
			usleep(usec - check);
			check = usec;
		}
		SYSCALL(ret = write(fd, &ev, sizeof(ev)));
	}

	return 0;
}

static int set_bit(int fd, int type, int code)
{
	int ret = 0;

	switch(type) {
	case EV_SYN:
		SYSCALL(ret = ioctl(fd, UI_SET_EVBIT, code));
		break;
	case EV_KEY:
		SYSCALL(ret = ioctl(fd, UI_SET_KEYBIT, code));
		break;
	case EV_REL:
		SYSCALL(ret = ioctl(fd, UI_SET_RELBIT, code));
		break;
	case EV_ABS:
		SYSCALL(ret = ioctl(fd, UI_SET_ABSBIT, code));
		break;
	case EV_MSC:
		SYSCALL(ret = ioctl(fd, UI_SET_MSCBIT, code));
		break;
	case EV_LED:
		SYSCALL(ret = ioctl(fd, UI_SET_LEDBIT, code));
		break;
	case EV_SND:
		SYSCALL(ret = ioctl(fd, UI_SET_SNDBIT, code));
		break;
	case EV_FF:
		SYSCALL(ret = ioctl(fd, UI_SET_FFBIT, code));
		break;
	case EV_SW:
		SYSCALL(ret = ioctl(fd, UI_SET_SWBIT, code));
		break;
	}

	return ret;
}

static int set_mask(const struct evemu_device *dev, int type, int fd)
{
	int bits = 8 * dev->bytes[type];
	int ret, i;
	for (i = 0; i < bits; i++) {
		if (!evemu_has(dev, type, i))
			continue;
		ret = set_bit(fd, type, i);
		if (ret < 0)
			return ret;
	}
	return 0;
}

int evemu_create(const struct evemu_device *dev, int fd)
{
	struct uinput_user_dev udev;
	int ret, i;

	memset(&udev, 0, sizeof(udev));
	memcpy(udev.name, dev->name, sizeof(udev.name));
	udev.id = dev->id;
	for (i = 0; i < ABS_CNT; i++) {
		if (!evemu_has(dev, EV_ABS, i))
			continue;
		udev.absmax[i] = dev->abs[i].maximum;
		udev.absmin[i] = dev->abs[i].minimum;
		udev.absfuzz[i] = dev->abs[i].fuzz;
		udev.absflat[i] = dev->abs[i].flat;
	}

	for (i = 0; i < EV_CNT; i++) {
		ret = set_mask(dev, i, fd);
		if (ret < 0)
			return ret;
	}

	SYSCALL(ret = write(fd, &udev, sizeof(udev)));
	if (ret < 0)
		return ret;

	SYSCALL(ret = ioctl(fd, UI_DEV_CREATE, NULL));
	return ret;
}

void evemu_destroy(int fd)
{
	int ret;
	SYSCALL(ret = ioctl(fd, UI_DEV_DESTROY, NULL));
}
