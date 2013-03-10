/*****************************************************************************
 *
 * evemu - Kernel device emulation
 *
 * Copyright (C) 2010-2012 Canonical Ltd.
 *
 * This library is free software: you can redistribute it and/or modify it 
 * under the terms of the GNU Lesser General Public License version 3
 * as published by the Free Software Foundation.
 *
 * This library is distributed in the hope that it will be useful, but 
 * WITHOUT ANY WARRANTY; without even the implied warranties of 
 * MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
 * PURPOSE.  See the GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Copyright (C) 2010 Henrik Rydberg <rydberg@euromail.se>
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

#include "evemu-impl.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <poll.h>
#include <ctype.h>
#include <unistd.h>

#include "version.h"

/* File format version we write out
   NOTE: if you bump the version number, make sure you update README */
#define EVEMU_FILE_MAJOR 1
#define EVEMU_FILE_MINOR 0

#ifndef UI_SET_PROPBIT
#define UI_SET_PROPBIT		_IOW(UINPUT_IOCTL_BASE, 110, int)
#define EVIOCGPROP(len)		_IOC(_IOC_READ, 'E', 0x09, len)
#define INPUT_PROP_POINTER		0x00
#define INPUT_PROP_DIRECT		0x01
#define INPUT_PROP_BUTTONPAD		0x02
#define INPUT_PROP_SEMI_MT		0x03
#define INPUT_PROP_MAX			0x1f
#define INPUT_PROP_CNT			(INPUT_PROP_MAX + 1)
#endif

#define SYSCALL(call) while (((call) == -1) && (errno == EINTR))

static void skip_comment_block(FILE *fp)
{
	int first_char;

	while ((first_char = getc(fp)) == '#') {
		char *line = NULL;
		size_t n = 0;
		getline(&line, &n, fp);
		free(line);
	}
	ungetc(first_char, fp);
}

static void copy_bits(unsigned char *mask, const unsigned long *bits, int bytes)
{
	int i;
	for (i = 0; i < bytes; i++) {
		int pos = 8 * (i % sizeof(long));
		mask[i] = (bits[i / sizeof(long)] >> pos) & 0xff;
	}
}

struct evemu_device *evemu_new(const char *name)
{
	struct evemu_device *dev = calloc(1, sizeof(struct evemu_device));

	if (dev) {
		dev->version = EVEMU_VERSION;
		evemu_set_name(dev, name);
	}

	return dev;
}

void evemu_delete(struct evemu_device *dev)
{
	free(dev);
}

unsigned int evemu_get_version(const struct evemu_device *dev)
{
	return dev->version;
}

const char *evemu_get_name(const struct evemu_device *dev)
{
	return dev->name;
}

void evemu_set_name(struct evemu_device *dev, const char *name)
{
	if (name && strlen(name) < sizeof(dev->name))
		strcpy(dev->name, name);
}

unsigned int evemu_get_id_bustype(const struct evemu_device *dev)
{
	return dev->id.bustype;
}

void evemu_set_id_bustype(struct evemu_device *dev,
			  unsigned int bustype)
{
	dev->id.bustype = bustype;
}

unsigned int evemu_get_id_vendor(const struct evemu_device *dev)
{
	return dev->id.vendor;
}

void evemu_set_id_vendor(struct evemu_device *dev,
			 unsigned int vendor)
{
	dev->id.vendor = vendor;
}

unsigned int evemu_get_id_product(const struct evemu_device *dev)
{
	return dev->id.product;
}

void evemu_set_id_product(struct evemu_device *dev,
			  unsigned int product)
{
	dev->id.product = product;
}

unsigned int evemu_get_id_version(const struct evemu_device *dev)
{
	return dev->id.version;
}

void evemu_set_id_version(struct evemu_device *dev,
			  unsigned int version)
{
	dev->id.version = version;
}

int evemu_get_abs_minimum(const struct evemu_device *dev, int code)
{
	return dev->abs[code].minimum;
}

void evemu_set_abs_minimum(struct evemu_device *dev, int code, int min)
{
	dev->abs[code].minimum = min;
}

int evemu_get_abs_maximum(const struct evemu_device *dev, int code)
{
	return dev->abs[code].maximum;
}

int evemu_get_abs_current_value(const struct evemu_device *dev, int code)
{
	return dev->abs[code].value;
}

void evemu_set_abs_maximum(struct evemu_device *dev, int code, int max)
{
	dev->abs[code].maximum = max;
}

int evemu_get_abs_fuzz(const struct evemu_device *dev, int code)
{
	return dev->abs[code].fuzz;
}

void evemu_set_abs_fuzz(struct evemu_device *dev, int code, int fuzz)
{
	dev->abs[code].fuzz = fuzz;
}

int evemu_get_abs_flat(const struct evemu_device *dev, int code)
{
	return dev->abs[code].flat;
}

void evemu_set_abs_flat(struct evemu_device *dev, int code, int flat)
{
	dev->abs[code].flat = flat;
}

int evemu_get_abs_resolution(const struct evemu_device *dev, int code)
{
	return dev->abs[code].resolution;
}

void evemu_set_abs_resolution(struct evemu_device *dev, int code, int res)
{
	dev->abs[code].resolution = res;
}

int evemu_has_prop(const struct evemu_device *dev, int code)
{
	return (dev->prop[code >> 3] >> (code & 7)) & 1;
}

int evemu_has_event(const struct evemu_device *dev, int type, int code)
{
	return (dev->mask[type][code >> 3] >> (code & 7)) & 1;
}

int evemu_extract(struct evemu_device *dev, int fd)
{
	unsigned long bits[64];
	int rc, i;

	memset(dev, 0, sizeof(*dev));

	SYSCALL(rc = ioctl(fd, EVIOCGNAME(sizeof(dev->name)-1), dev->name));
	if (rc < 0)
		return rc;

	SYSCALL(rc = ioctl(fd, EVIOCGID, &dev->id));
	if (rc < 0)
		return rc;

	SYSCALL(rc = ioctl(fd, EVIOCGPROP(sizeof(bits)), bits));
	if (rc >= 0) {
		copy_bits(dev->prop, bits, rc);
		dev->pbytes = rc;
	}

	for (i = 0; i < EV_CNT; i++) {
		SYSCALL(rc = ioctl(fd, EVIOCGBIT(i, sizeof(bits)), bits));
		if (rc < 0)
			continue;
		copy_bits(dev->mask[i], bits, rc);
		dev->mbytes[i] = rc;
	}

	for (i = 0; i < ABS_CNT; i++) {
		if (!evemu_has_event(dev, EV_ABS, i))
			continue;
		SYSCALL(rc = ioctl(fd, EVIOCGABS(i), &dev->abs[i]));
		if (rc < 0)
			return rc;
	}

	return 0;
}

static void write_prop(FILE * fp, const unsigned char *mask, int bytes)
{
	int i;
	for (i = 0; i < bytes; i += 8)
		fprintf(fp, "P: %02x %02x %02x %02x %02x %02x %02x %02x\n",
			mask[i], mask[i + 1], mask[i + 2], mask[i + 3],
			mask[i + 4], mask[i + 5], mask[i + 6], mask[i + 7]);
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

	fprintf(fp, "# EVEMU %d.%d\n", EVEMU_FILE_MAJOR, EVEMU_FILE_MINOR);

	fprintf(fp, "N: %s\n", dev->name);

	fprintf(fp, "I: %04x %04x %04x %04x\n",
		dev->id.bustype, dev->id.vendor,
		dev->id.product, dev->id.version);

	write_prop(fp, dev->prop, dev->pbytes);

	for (i = 0; i < EV_CNT; i++)
		write_mask(fp, i, dev->mask[i], dev->mbytes[i]);

	for (i = 0; i < ABS_CNT; i++)
		if (evemu_has_event(dev, EV_ABS, i))
			write_abs(fp, i, &dev->abs[i]);

	return 0;
}

static void read_prop(struct evemu_device *dev, FILE *fp, version_t *fversion)
{
	unsigned int mask[8];
	int i;
	while (fscanf(fp, "P: %02x %02x %02x %02x %02x %02x %02x %02x\n",
		      mask + 0, mask + 1, mask + 2, mask + 3,
		      mask + 4, mask + 5, mask + 6, mask + 7) > 0) {
		for (i = 0; i < 8; i++)
			dev->prop[dev->pbytes++] = mask[i];
	}
}

static void read_mask(struct evemu_device *dev, FILE *fp, version_t *fversion)
{
	unsigned int mask[8];
	unsigned int index, i;
	while (fscanf(fp, "B: %02x %02x %02x %02x %02x %02x %02x %02x %02x\n",
		      &index, mask + 0, mask + 1, mask + 2, mask + 3,
		      mask + 4, mask + 5, mask + 6, mask + 7) > 0) {
		for (i = 0; i < 8; i++)
			dev->mask[index][dev->mbytes[index]++] = mask[i];
	}
}

static void read_abs(struct evemu_device *dev, FILE *fp, version_t *fversion)
{
	struct input_absinfo abs;
	unsigned int index;
	while (fscanf(fp, "A: %02x %d %d %d %d\n", &index,
		      &abs.minimum, &abs.maximum, &abs.fuzz, &abs.flat) > 0)
		dev->abs[index] = abs;

static version_t read_file_format_version(FILE *fp)
{
	uint16_t major, minor;

	if (fscanf(fp, "# EVEMU %hd.%hd\n", &major, &minor) != 2) {
		major = 1;
		minor = 0;
	}

	return version_new(major, minor);
}

int evemu_read(struct evemu_device *dev, FILE *fp)
{
	unsigned bustype, vendor, product, version;
	version_t file_version; /* file format version */
	int ret;
	char *devname = NULL;

	memset(dev, 0, sizeof(*dev));

	file_version = read_file_format_version(fp);

	skip_comment_block(fp);

	ret = fscanf(fp, "N: %m[^\n]\n", &devname);
	if (ret <= 0) {
		if (devname != NULL)
			free(devname);
		return ret;
	}
	strncpy(dev->name, devname, sizeof(dev->name));
	dev->name[sizeof(dev->name)-1] = '\0';
	free(devname);

	ret = fscanf(fp, "I: %04x %04x %04x %04x\n",
		     &bustype, &vendor, &product, &version);
	if (ret <= 0)
		return ret;

	dev->id.bustype = bustype;
	dev->id.vendor = vendor;
	dev->id.product = product;
	dev->id.version = version;

	read_prop(dev, fp, &file_version);

	read_mask(dev, fp, &file_version);

	read_abs(dev, fp, &file_version);

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
			fflush(fp);
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

int evemu_create_event(struct input_event *ev, int type, int code, int value)
{
	ev->time.tv_sec = 0;
	ev->time.tv_usec = 0;
	ev->type = type;
	ev->code = code;
	ev->value = value;
	return 0;
}

int evemu_read_event_realtime(FILE *fp, struct input_event *ev,
			      struct timeval *evtime)
{
	unsigned long usec;
	int ret;

	ret = evemu_read_event(fp, ev);
	if (ret <= 0)
		return ret;

	if (evtime) {
		if (!evtime->tv_sec)
			*evtime = ev->time;
		usec = 1000000L * (ev->time.tv_sec - evtime->tv_sec);
		usec += ev->time.tv_usec - evtime->tv_usec;
		if (usec > 500) {
			usleep(usec);
			*evtime = ev->time;
		}
	}

	return ret;
}

int evemu_play_one(int fd, const struct input_event *ev)
{
	int ret;
	SYSCALL(ret = write(fd, ev, sizeof(*ev)));
	return (ret < sizeof(*ev));
}

int evemu_play(FILE *fp, int fd)
{
	struct input_event ev;
	struct timeval evtime;
	int ret;

	skip_comment_block(fp);

	memset(&evtime, 0, sizeof(evtime));
	while (evemu_read_event_realtime(fp, &ev, &evtime) > 0)
		SYSCALL(ret = write(fd, &ev, sizeof(ev)));

	return 0;
}

static int set_prop_bit(int fd, int code)
{
	int ret;
	SYSCALL(ret = ioctl(fd, UI_SET_PROPBIT, code));
	return ret;
}

static int set_event_bit(int fd, int type, int code)
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

static int set_prop(const struct evemu_device *dev, int fd)
{
	int bits = 8 * dev->pbytes;
	int ret, i;
	int success = 0;
	for (i = 0; i < bits; i++) {
		if (!evemu_has_prop(dev, i))
			continue;
		ret = set_prop_bit(fd, i);
		/* Older kernels aways return errors on UI_SET_PROPBIT.
		   Assume that if we only get failures, it may be an older
		   kernel and report success anyway. */
		if (ret < 0) {
			if (success)
				return ret;
		} else if (!success)
			success = 1;
	}
	return 0;
}

static int set_mask(const struct evemu_device *dev, int type, int fd)
{
	int bits = 8 * dev->mbytes[type];
	int ret, i;
	for (i = 0; i < bits; i++) {
		if (!evemu_has_event(dev, type, i))
			continue;

		/* kernel doesn't like those */
		if (type == EV_ABS &&
			dev->abs[i].maximum == 0 && dev->abs[i].minimum == 0)
			continue;

		ret = set_event_bit(fd, type, i);
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
		if (!evemu_has_event(dev, EV_ABS, i))
			continue;
		udev.absmax[i] = dev->abs[i].maximum;
		udev.absmin[i] = dev->abs[i].minimum;
		udev.absfuzz[i] = dev->abs[i].fuzz;
		udev.absflat[i] = dev->abs[i].flat;
	}

	ret = set_prop(dev, fd);
	if (ret < 0)
		return ret;

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
