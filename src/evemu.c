/*****************************************************************************
 *
 * evemu - Kernel device emulation
 *
 * Copyright (C) 2010-2012 Canonical Ltd.
 * Copyright (C) 2013 Red Hat, Inc.
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

#define _GNU_SOURCE
#include "evemu-impl.h"
#include <stdint.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <poll.h>
#include <ctype.h>
#include <unistd.h>

#include "version.h"
#include "event-names.h"

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

enum error_level {
	INFO,
	WARNING,
	FATAL,
};

static int error(enum error_level level, const char *format, ...)
{
	va_list args;
	const char *strlevel = NULL;

	switch (level) {
		case INFO: strlevel = "INFO"; break;
		case WARNING: strlevel = "WARNING"; break;
		case FATAL: strlevel = "FATAL"; break;
	}

	fprintf(stderr, "%s: ", strlevel);
	va_start(args, format);
	vfprintf(stderr, format, args);
	va_end(args);

	return -1;
}

static int is_comment(char *line)
{
	return line && strlen(line) > 0 && line[0] == '#';
}

static int next_line(FILE *fp, char **line, size_t *sz)
{
	while (getline(line, sz, fp) > 0)
		if (!is_comment(*line))
			return 1;
	return 0;
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

int evemu_has_bit(const struct evemu_device *dev, int type)
{
	return (dev->mask[0][type >> 3] >> (type & 7)) & 1;
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

/* Print an evtest-like description */
static void write_desc(const struct evemu_device *dev, FILE *fp)
{
	int i, j;
	fprintf(fp, "# Input device name: \"%s\"\n", dev->name);
	fprintf(fp, "# Input device ID: bus %#04x vendor %#04x product %#04x version %#04x\n",
		dev->id.bustype, dev->id.vendor,
		dev->id.product, dev->id.version);
	fprintf(fp, "# Supported events:\n");
	for (i = 0; i < EV_MAX; i++) {
		if (!evemu_has_bit(dev, i))
			continue;

		fprintf(fp, "#   Event type %d (%s)\n", i, event_get_type_name(i));
		for (j = 0; j < KEY_MAX; j++) {
			if (!evemu_has_event(dev, i, j))
				continue;

			fprintf(fp, "#     Event code %d (%s)\n",
				    j, event_get_code_name(i, j));
			if (i == EV_ABS) {
				fprintf(fp, "#       Value %6d\n"
					    "#       Min   %6d\n"
					    "#       Max   %6d\n"
					    "#       Fuzz  %6d\n"
					    "#       Flat  %6d\n"
					    "#       Resolution %d\n",
					    dev->abs[j].value,
					    dev->abs[j].minimum,
					    dev->abs[j].maximum,
					    dev->abs[j].fuzz,
					    dev->abs[j].flat,
					    dev->abs[j].resolution);
			}
		}
	}

#ifdef INPUT_PROP_MAX
	fprintf(fp, "# Properties:\n");
	for (i = 0; i < INPUT_PROP_MAX; i++) {
		if (!evemu_has_prop(dev, i))
			continue;
		fprintf(fp, "#   Property  type %d (%s)\n", i, input_prop_map[i]);
	}
#endif
}

int evemu_write(const struct evemu_device *dev, FILE *fp)
{
	int i;

	fprintf(fp, "# EVEMU %d.%d\n", EVEMU_FILE_MAJOR, EVEMU_FILE_MINOR);

	write_desc(dev, fp);

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

static int parse_name(struct evemu_device *dev, const char *line, struct version *fversion)
{
	int matched;
	char *devname = NULL;

	if ((matched = sscanf(line, "N: %m[^\n]\n", &devname)) > 0) {
		strncpy(dev->name, devname, sizeof(dev->name));
		dev->name[sizeof(dev->name)-1] = '\0';
	}

	if (devname != NULL)
		free(devname);

	if (matched <= 0)
		error(FATAL, "Expected device name, but got: %s", line);

	return matched > 0;
}

static int parse_bus_vid_pid_ver(struct evemu_device *dev, const char *line, struct version *fversion)
{
	int matched;
	unsigned bustype, vendor, product, version;

	if ((matched = sscanf(line, "I: %04x %04x %04x %04x\n",
				    &bustype, &vendor, &product, &version)) > 0) {
		dev->id.bustype = bustype;
		dev->id.vendor = vendor;
		dev->id.product = product;
		dev->id.version = version;
	}

	if (matched != 4)
		error(FATAL, "Expected bus/vendor/product/version, got: %s", line);

	return matched == 4;
}

static int parse_prop(struct evemu_device *dev, const char *line, struct version *fversion)
{
	int matched;
	unsigned int mask[8];
	int i;

	if (strlen(line) <= 2 || strncmp(line, "P:", 2) != 0)
		return 0;

	matched = sscanf(line, "P: %02x %02x %02x %02x %02x %02x %02x %02x\n",
				mask + 0, mask + 1, mask + 2, mask + 3,
				mask + 4, mask + 5, mask + 6, mask + 7);

	if (matched != 8) {
		error(WARNING, "Invalid INPUT_PROP line. Parsed %d numbers, expected 8: %s", matched, line);
		return -1;
	}

	for (i = 0; i < 8; i++)
		dev->prop[dev->pbytes++] = mask[i];

	return 1;
}

static int parse_mask(struct evemu_device *dev, const char *line, struct version *fversion)
{
	int matched;
	unsigned int mask[8];
	unsigned int index, i;

	if (strlen(line) <= 2 || strncmp(line, "B:", 2) != 0)
		return 0;

	matched = sscanf(line, "B: %02x %02x %02x %02x %02x %02x %02x %02x %02x\n",
				&index, mask + 0, mask + 1, mask + 2, mask + 3,
				mask + 4, mask + 5, mask + 6, mask + 7);

	if (matched != 9) {
		error(WARNING, "Invalid EV_BIT line. Parsed %d numbers, expected 9: %s", matched, line);
		return -1;
	}

	for (i = 0; i < 8; i++)
		dev->mask[index][dev->mbytes[index]++] = mask[i];

	return 1;
}

static int parse_abs(struct evemu_device *dev, const char *line, struct version *fversion)
{
	int matched;
	struct input_absinfo abs;
	unsigned int index;

	if (strlen(line) <= 2 || strncmp(line, "A:", 2) != 0)
		return 0;

	matched = sscanf(line, "A: %02x %d %d %d %d\n",
				&index, &abs.minimum, &abs.maximum,
				&abs.fuzz, &abs.flat);
	if (matched != 5) {
		error(WARNING, "Invalid EV_ABS line. Parsed %d numbers, expected 5: %s", matched, line);
		return -1;
	}

	dev->abs[index] = abs;

	return 1;
}

static struct version parse_file_format_version(const char *line)
{
	struct version v;
	uint16_t major, minor;

	if (sscanf(line, "# EVEMU %hd.%hd\n", &major, &minor) != 2) {
		major = 1;
		minor = 0;
	}


	v = version(major, minor);

	if (version_cmp(v, version(EVEMU_FILE_MAJOR, EVEMU_FILE_MINOR)) > 0)
		fprintf(stderr, "Warning: file format %d.%d is newer than "
				"supported version %d.%d.\n",
			major, minor, EVEMU_FILE_MAJOR, EVEMU_FILE_MINOR);

	return v;
}

int evemu_read(struct evemu_device *dev, FILE *fp)
{
	int rc = -1;
	struct version file_version; /* file format version */
	size_t size;
	char *line = NULL;

	memset(dev, 0, sizeof(*dev));

	/* first line _may_ be version */
	if (getline(&line, &size, fp) < 0)
		return -1;

	file_version = parse_file_format_version(line);

	if (is_comment(line) && !next_line(fp, &line, &size))
		goto out;

	if (!parse_name(dev, line, &file_version))
		goto out;

	if (!next_line(fp, &line, &size))
		goto out;

	if (!parse_bus_vid_pid_ver(dev, line, &file_version))
		goto out;

	/* devices without prop/mask/abs bits are valid */
	if (!next_line(fp, &line, &size)) {
		rc = 1;
		goto out;
	}

	while((rc = parse_prop(dev, line, &file_version)) > 0)
		if (!next_line(fp, &line, &size))
			break;
	if (rc == -1)
		goto out;

	while((rc = parse_mask(dev, line, &file_version)) > 0)
		if (!next_line(fp, &line, &size))
			break;
	if (rc == -1)
		goto out;

	while((rc = parse_abs(dev, line, &file_version)) > 0)
		if (!next_line(fp, &line, &size))
			break;
	if (rc == -1)
		goto out;

	rc = 1;

out:
	free(line);
	return rc;
}

static void write_event_desc(FILE *fp, const struct input_event *ev)
{
	if (ev->type == EV_SYN) {
		if (ev->code == SYN_MT_REPORT)
			fprintf(fp, "# ++++++++++++ %s (%d) ++++++++++\n",
				event_get_code_name(ev->type, ev->code),
				ev->value);
		else
			fprintf(fp, "# ------------ %s (%d) ----------\n",
				event_get_code_name(ev->type, ev->code),
				ev->value);
	} else {
		fprintf(fp, "# %s / %-20s %d\n",
			event_get_type_name(ev->type),
			event_get_code_name(ev->type, ev->code),
			ev->value);
	}
}

int evemu_write_event(FILE *fp, const struct input_event *ev)
{
	return fprintf(fp, "E: %lu.%06u %04x %04x %04d	",
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
			write_event_desc(fp, &ev);
			fflush(fp);
	}

	return 0;
}

int evemu_read_event(FILE *fp, struct input_event *ev)
{
	unsigned long sec;
	unsigned usec, type, code;
	int value;
	int matched = 0;
	char *line = NULL;
	size_t size = 0;

	if (!next_line(fp, &line, &size))
		goto out;

	if (strlen(line) <= 2 || strncmp(line, "E:", 2) != 0)
		goto out;

	matched = sscanf(line, "E: %lu.%06u %04x %04x %d\n",
			 &sec, &usec, &type, &code, &value);
	if (matched != 5) {
		error(FATAL, "Invalid event format: %s\n", line);
		return -1;
	}

	ev->time.tv_sec = sec;
	ev->time.tv_usec = usec;
	ev->type = type;
	ev->code = code;
	ev->value = value;

out:
	free(line);
	return matched > 0;
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
