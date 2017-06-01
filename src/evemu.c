/*****************************************************************************
 *
 * evemu - Kernel device emulation
 *
 * Copyright (C) 2010-2012 Canonical Ltd.
 * Copyright (C) 2013-2015 Red Hat, Inc.
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
#include <sys/utsname.h>

#include "version.h"

/* File format version we write out
   NOTE: if you bump the version number, make sure you update README */
#define EVEMU_FILE_MAJOR 1
#define EVEMU_FILE_MINOR 3

#define SYSCALL(call) while (((call) == -1) && (errno == EINTR))

enum error_level {
	INFO,
	WARNING,
	FATAL,
};

static int error(enum error_level level, const char *format, ...)
	        __attribute__ ((format (printf, 2, 3)));

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

static int first_line(FILE *fp, char **line, size_t *sz)
{
	int rc = 1;
	do {
		if (getline(line, sz, fp) < 0) {
			rc = 0;
			break;
		}
	} while(*sz == 0 || strlen(*line) <= 1);

	return rc;
}

static int next_line(FILE *fp, char **line, size_t *sz)
{
	while (first_line(fp, line, sz)) {
		if (!is_comment(*line))
			return 1;
	}
	return 0;
}


struct evemu_device *evemu_new(const char *name)
{
	struct evemu_device *dev = calloc(1, sizeof(struct evemu_device));

	if (dev) {
		dev->evdev = libevdev_new();
		if (!dev->evdev) {
			free(dev);
			return NULL;
		}
		dev->version = EVEMU_VERSION;
		evemu_set_name(dev, name);
	}

	return dev;
}

void evemu_delete(struct evemu_device *dev)
{
	if (dev == NULL)
		return;

	if (dev->uidev)
		evemu_destroy(dev);
	libevdev_free(dev->evdev);
	free(dev);
}

unsigned int evemu_get_version(const struct evemu_device *dev)
{
	return dev->version;
}

const char *evemu_get_name(const struct evemu_device *dev)
{
	return libevdev_get_name(dev->evdev);
}

void evemu_set_name(struct evemu_device *dev, const char *name)
{
	if (name)
		libevdev_set_name(dev->evdev, name);
}

#define ID_GETTER(field) \
unsigned int evemu_get_id_##field(const struct evemu_device *dev) { \
	return libevdev_get_id_##field(dev->evdev); \
}

ID_GETTER(bustype)
ID_GETTER(version)
ID_GETTER(product)
ID_GETTER(vendor)

#define ID_SETTER(field) \
void evemu_set_id_##field(struct evemu_device *dev, unsigned int value) { \
	libevdev_set_id_##field(dev->evdev, value); \
}

ID_SETTER(bustype)
ID_SETTER(version)
ID_SETTER(product)
ID_SETTER(vendor)

#define ABS_GETTER(field) \
int evemu_get_abs_##field(const struct evemu_device *dev, int code) { \
	return libevdev_get_abs_##field(dev->evdev, code); \
}

ABS_GETTER(minimum)
ABS_GETTER(maximum)
ABS_GETTER(fuzz)
ABS_GETTER(flat)
ABS_GETTER(resolution)

#define ABS_SETTER(field) \
void evemu_set_abs_##field(struct evemu_device *dev, int code, int value) { \
	libevdev_set_abs_##field(dev->evdev, code, value); \
}

ABS_SETTER(minimum)
ABS_SETTER(maximum)
ABS_SETTER(fuzz)
ABS_SETTER(flat)
ABS_SETTER(resolution)

int evemu_get_abs_current_value(const struct evemu_device *dev, int code)
{
	return libevdev_get_event_value(dev->evdev, EV_ABS, code);
}

int evemu_has_prop(const struct evemu_device *dev, int code)
{
	return libevdev_has_property(dev->evdev, code);
}

int evemu_has_event(const struct evemu_device *dev, int type, int code)
{
	return libevdev_has_event_code(dev->evdev, type, code);
}

int evemu_has_bit(const struct evemu_device *dev, int type)
{
	return libevdev_has_event_type(dev->evdev, type);
}

int evemu_extract(struct evemu_device *dev, int fd)
{
	if (libevdev_get_fd(dev->evdev) != -1) {
		libevdev_free(dev->evdev);
		dev->evdev = libevdev_new();
		if (!dev->evdev)
			return -ENOMEM;
	}
	return libevdev_set_fd(dev->evdev, fd);
}

static inline int bit_is_set(unsigned char *mask, int bit)
{
	return !!(mask[bit/8] & (1 << (bit & 0x7)));
}

static inline void set_bit(unsigned char *mask, int bit)
{
	mask[bit/8] |= 1 << (bit & 0x7);
}

#define max(a, b) (a > b) ? a : b

static void write_prop(FILE * fp, const struct evemu_device *dev)
{
#ifdef INPUT_PROP_MAX
	int i;
	unsigned char mask[max(8, (INPUT_PROP_MAX + 7)/8)] = {0};

	for (i = 0; i < INPUT_PROP_CNT; i ++) {
		if (evemu_has_prop(dev, i))
			set_bit(mask, i);
	}

	for (i = 0; i < (INPUT_PROP_CNT + 7)/8; i +=8) {
		fprintf(fp, "P: %02x %02x %02x %02x %02x %02x %02x %02x\n",
			mask[i], mask[i + 1], mask[i + 2], mask[i + 3],
			mask[i + 4], mask[i + 5], mask[i + 6], mask[i + 7]);
	}
#endif
}

static void write_mask(FILE * fp, const struct evemu_device *dev)
{
	unsigned int type;

	/* Write EV_SYN/SYN_REPORT only. Just because older versions
	   printed out exactly that */
	fprintf(fp, "B: 00 0b 00 00 00 00 00 00 00\n");

	for (type = 1 /* don't write EV_SYN */; type < EV_CNT; type++) {
		int i;
		int max = libevdev_event_type_get_max(type);
		unsigned char mask[KEY_CNT] = {0};
		unsigned int code;

		if (max == -1)
			continue;

		for (code = 0; code <= (unsigned int)max; code++)
			if (evemu_has_event(dev, type, code))
				set_bit(mask, code);

		for (i = 0; i < ((max + 1) + 7)/8; i += 8) {
			fprintf(fp, "B: %02x %02x %02x %02x %02x %02x %02x %02x %02x\n",
				type, mask[i], mask[i + 1], mask[i + 2], mask[i + 3],
				mask[i + 4], mask[i + 5], mask[i + 6], mask[i + 7]);
		}
	}
}

static void write_abs(FILE *fp, int index, const struct input_absinfo *abs)
{
	fprintf(fp, "A: %02x %d %d %d %d %d\n", index,
		abs->minimum, abs->maximum, abs->fuzz, abs->flat, abs->resolution);
}

static void write_led(FILE *fp, int index, int state)
{
	fprintf(fp, "L: %02x %d\n", index, state);
}

static void write_sw(FILE *fp, int index, int state)
{
	fprintf(fp, "S: %02x %d\n", index, state);
}

/* Print an evtest-like description */
static void write_desc(const struct evemu_device *dev, FILE *fp)
{
	int i, j;
	int state;
	fprintf(fp, "# Input device name: \"%s\"\n", evemu_get_name(dev));
	fprintf(fp, "# Input device ID: bus %#04x vendor %#04x product %#04x version %#04x\n",
		evemu_get_id_bustype(dev), evemu_get_id_vendor(dev),
		evemu_get_id_product(dev), evemu_get_id_version(dev));

	if (evemu_has_event(dev, EV_ABS, ABS_X) &&
	    evemu_has_event(dev, EV_ABS, ABS_Y)) {
		int min, max, res;
		int w = 0, h = 0;

		min = evemu_get_abs_minimum(dev, ABS_X);
		max = evemu_get_abs_maximum(dev, ABS_X);
		res = evemu_get_abs_resolution(dev, ABS_X);
		if (res != 0)
			w = (max - min)/res;

		min = evemu_get_abs_minimum(dev, ABS_Y);
		max = evemu_get_abs_maximum(dev, ABS_Y);
		res = evemu_get_abs_resolution(dev, ABS_Y);
		if (res != 0)
			h = (max - min)/res;

		if (w != 0 && h != 0)
			fprintf(fp, "# Size in mm: %dx%d\n", w, h);
	}

	fprintf(fp, "# Supported events:\n");
	for (i = 0; i < EV_CNT; i++) {
		if (!evemu_has_bit(dev, i))
			continue;

		fprintf(fp, "#   Event type %d (%s)\n", i, libevdev_event_type_get_name(i));
		for (j = 0; j <= libevdev_event_type_get_max(i); j++) {
			if (!evemu_has_event(dev, i, j))
				continue;

			fprintf(fp, "#     Event code %d (%s)\n",
				    j, libevdev_event_code_get_name(i, j));
			switch(i) {
				case EV_ABS:
					fprintf(fp,
						"#       Value   %6d\n"
						"#       Min     %6d\n"
						"#       Max     %6d\n"
						"#       Fuzz    %6d\n"
						"#       Flat    %6d\n"
						"#       Resolution %3d\n",
						evemu_get_abs_current_value(dev, j),
						evemu_get_abs_minimum(dev, j),
						evemu_get_abs_maximum(dev,j),
						evemu_get_abs_fuzz(dev, j),
						evemu_get_abs_flat(dev, j),
						evemu_get_abs_resolution(dev, j));
					break;
				case EV_LED:
				case EV_SW:
					state = libevdev_get_event_value(dev->evdev, i, j);
					fprintf(fp, "#        State %d\n", state);
					break;
				default:
					break;
			}
		}
	}

#ifdef INPUT_PROP_MAX
	fprintf(fp, "# Properties:\n");
	for (i = 0; i < INPUT_PROP_CNT; i++) {
		if (!evemu_has_prop(dev, i))
			continue;
		fprintf(fp, "#   Property  type %d (%s)\n", i,
				libevdev_property_get_name(i));
	}
#endif
}

static void
write_header(FILE *fp)
{
	struct utsname u;
	char modalias[2048];
	FILE *dmi;

	fprintf(fp, "# EVEMU %d.%d\n", EVEMU_FILE_MAJOR, EVEMU_FILE_MINOR);

	if (uname(&u) == -1)
		return;

	fprintf(fp, "# Kernel: %s\n", u.release);

	dmi = fopen("/sys/class/dmi/id/modalias", "r");
	if (dmi) {
		if (fgets(modalias, sizeof(modalias), dmi)) {
			fprintf(fp, "# DMI: %s", modalias);
		}
		fclose(dmi);
	}
}

int evemu_write(const struct evemu_device *dev, FILE *fp)
{
	int i;
	int state;

	write_header(fp);

	write_desc(dev, fp);

	fprintf(fp, "N: %s\n", evemu_get_name(dev));

	fprintf(fp, "I: %04x %04x %04x %04x\n",
		evemu_get_id_bustype(dev),
		evemu_get_id_vendor(dev),
		evemu_get_id_product(dev),
		evemu_get_id_version(dev));

	write_prop(fp, dev);
	write_mask(fp, dev);

	for (i = 0; i < ABS_CNT; i++)
		if (evemu_has_event(dev, EV_ABS, i))
			write_abs(fp, i, libevdev_get_abs_info(dev->evdev, i));

	for (i = 0; i < LED_CNT; i++)
		if (evemu_has_event(dev, EV_LED, i) &&
		    (state = libevdev_get_event_value(dev->evdev, EV_LED, i)) != 0)
			write_led(fp, i, state);

	for (i = 0; i < SW_CNT; i++)
		if (evemu_has_event(dev, EV_SW, i) &&
		    (state = libevdev_get_event_value(dev->evdev, EV_SW, i)) != 0)
			write_sw(fp, i, state);

	return 0;
}

static int parse_name(struct evemu_device *dev, const char *line)
{
	int matched;
	char *devname = NULL;

	if ((matched = sscanf(line, "N: %m[^\n\r]\n", &devname)) > 0) {
		if (strlen(evemu_get_name(dev)) == 0)
			evemu_set_name(dev, devname);
	}

	if (devname != NULL)
		free(devname);

	if (matched <= 0)
		error(FATAL, "Expected device name, but got: %s", line);

	return matched > 0;
}

static int parse_bus_vid_pid_ver(struct evemu_device *dev, const char *line)
{
	int matched;
	unsigned bustype, vendor, product, version;

	if ((matched = sscanf(line, "I: %04x %04x %04x %04x\n",
				    &bustype, &vendor, &product, &version)) > 0) {
		evemu_set_id_bustype(dev, bustype);
		evemu_set_id_vendor(dev, vendor);
		evemu_set_id_product(dev, product);
		evemu_set_id_version(dev, version);
	}

	if (matched != 4)
		error(FATAL, "Expected bus/vendor/product/version, got: %s", line);

	return matched == 4;
}

static int parse_prop(struct evemu_device *dev, const char *line)
{
	int matched;
	unsigned char mask[8];
	size_t i;

	if (strlen(line) <= 2 || strncmp(line, "P:", 2) != 0)
		return 0;

	matched = sscanf(line, "P: %02hhx %02hhx %02hhx %02hhx %02hhx %02hhx %02hhx %02hhx\n",
				mask + 0, mask + 1, mask + 2, mask + 3,
				mask + 4, mask + 5, mask + 6, mask + 7);

	if (matched != 8) {
		error(WARNING, "Invalid INPUT_PROP line. Parsed %d numbers, expected 8: %s", matched, line);
		return -1;
	}

	for (i = 0; i < sizeof(mask) * 8; i++) {
		if (bit_is_set(mask, i))
			libevdev_enable_property(dev->evdev, dev->pbytes * 8 + i);
	}

	dev->pbytes += 8;

	return 1;
}

static int parse_mask(struct evemu_device *dev, const char *line)
{
	int matched;
	unsigned char mask[8];
	unsigned int index, i;

	if (strlen(line) <= 2 || strncmp(line, "B:", 2) != 0)
		return 0;

	matched = sscanf(line, "B: %02x %02hhx %02hhx %02hhx %02hhx %02hhx %02hhx %02hhx %02hhx\n",
				&index, mask + 0, mask + 1, mask + 2, mask + 3,
				mask + 4, mask + 5, mask + 6, mask + 7);

	if (matched != 9) {
		error(FATAL, "Invalid EV_BIT line. Parsed %d numbers, expected 9: %s", matched, line);
		return -1;
	}

	if (index >= EV_CNT) {
		error(FATAL, "Invalid EV_* index %#x in line: %s", index, line);
		return -1;
	}

	for (i = 0; i < sizeof(mask) * 8; i++) {
		if (bit_is_set(mask, i)) {
			struct input_absinfo abs = {0}; /* dummy */

			abs.minimum = 0;
			abs.maximum = 1;

			unsigned int code = dev->mbytes[index] * 8 + i;
			libevdev_enable_event_code(dev->evdev, index, code, (index == EV_ABS) ? &abs : NULL);
		}
	}

	dev->mbytes[index] += 8;

	return 1;
}

static int parse_abs(struct evemu_device *dev, const char *line, struct version *fversion)
{
	int matched;
	struct input_absinfo abs = {0};
	unsigned int index;
	int needed = 5;

	if (version_cmp(*fversion, version(1, 1)) > 0)
			needed = 6; /* resolution field */

	if (strlen(line) <= 2 || strncmp(line, "A:", 2) != 0)
		return 0;

	matched = sscanf(line, "A: %02x %d %d %d %d %d\n",
				&index, &abs.minimum, &abs.maximum,
				&abs.fuzz, &abs.flat, &abs.resolution);

	if (matched != needed) {
		error(FATAL, "Invalid EV_ABS line. Parsed %d numbers, expected %d: %s", matched, needed, line);
		return -1;
	}

	evemu_set_abs_minimum(dev, index, abs.minimum);
	evemu_set_abs_maximum(dev, index, abs.maximum);
	evemu_set_abs_fuzz(dev, index, abs.fuzz);
	evemu_set_abs_flat(dev, index, abs.flat);
	evemu_set_abs_resolution(dev, index, abs.resolution);

	return 1;
}

static int parse_led(const char *line)
{
	int matched;
	unsigned int index;
	int state;

	if (strlen(line) <= 2 || strncmp(line, "L:", 2) != 0)
		return 0;

	matched = sscanf(line, "L: %02x %d\n", &index, &state);

	if (matched != 2) {
		error(FATAL, "Invalid EV_LED line. Parsed %d numbers, expected 2: %s", matched, line);
		return -1;
	}

	/* We can't set the LEDs directly, we'd have to send an event
	 * through the device but that's potentially racy */

	return 1;
}

static int parse_sw(const char *line)
{
	int matched;
	unsigned int index;
	int state;

	if (strlen(line) <= 2 || strncmp(line, "S:", 2) != 0)
		return 0;

	matched = sscanf(line, "S: %02x %d\n", &index, &state);

	if (matched != 2) {
		error(FATAL, "Invalid EV_SW line. Parsed %d numbers, expected 2: %s", matched, line);
		return -1;
	}

	/* We can't set the switches directly, we'd have to send an event
	 * through the device but that's potentially racy */

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
	size_t size = 0;
	char *line = NULL;

	memset(dev->mbytes, 0, sizeof(*dev->mbytes));
	dev->pbytes = 0;
	dev->version = EVEMU_VERSION;

	/* first line _may_ be version */
	if (!first_line(fp, &line, &size)) {
		error(WARNING, "This appears to be an empty file\n");
		return -1;
	}

	file_version = parse_file_format_version(line);

	if (is_comment(line) && !next_line(fp, &line, &size)) {
		error(WARNING, "This appears to be an empty file\n");
		goto out;
	}

	if (!parse_name(dev, line))
		goto out;

	if (!next_line(fp, &line, &size))
		goto out;

	if (!parse_bus_vid_pid_ver(dev, line))
		goto out;

	/* devices without prop/mask/abs bits are valid */
	if (!next_line(fp, &line, &size)) {
		rc = 1;
		goto out;
	}

	while((rc = parse_prop(dev, line)) > 0)
		if (!next_line(fp, &line, &size))
			break;
	if (rc == -1)
		goto out;

	while((rc = parse_mask(dev, line)) > 0)
		if (!next_line(fp, &line, &size))
			break;
	if (rc == -1)
		goto out;

	while((rc = parse_abs(dev, line, &file_version)) > 0)
		if (!next_line(fp, &line, &size))
			break;
	if (rc == -1)
		goto out;

	while((rc = parse_led(line)) > 0)
		if (!next_line(fp, &line, &size))
			break;
	if (rc == -1)
		goto out;

	while((rc = parse_sw(line)) > 0)
		if (!next_line(fp, &line, &size))
			break;
	if (rc == -1)
		goto out;

	rc = 1;

	fseek(fp, -strlen(line), SEEK_CUR);

out:
	free(line);
	return rc;
}

static inline unsigned long millis(const struct timeval *tv)
{
	return tv->tv_sec * 1000 + tv->tv_usec/1000;
}

static int write_event_desc(FILE *fp, const struct input_event *ev)
{
	int rc;
	static unsigned long last_ms = 0;
	unsigned long time, dt;

	if (ev->type == EV_SYN) {
		if (ev->code == SYN_MT_REPORT) {
			rc = fprintf(fp, "# ++++++++++++ %s (%d) ++++++++++\n",
				     libevdev_event_code_get_name(ev->type, ev->code),
				     ev->value);
		} else {
			time = millis(&ev->time);
			dt = time - last_ms;
			last_ms = time;
			rc = fprintf(fp, "# ------------ %s (%d) ---------- %+ldms\n",
				     libevdev_event_code_get_name(ev->type, ev->code),
				     ev->value,
				     dt);
		}
	} else {
		rc = fprintf(fp, "# %s / %-20s %d\n",
			     libevdev_event_type_get_name(ev->type),
			     libevdev_event_code_get_name(ev->type, ev->code),
			     ev->value);
	}
	return rc;
}

int evemu_write_event(FILE *fp, const struct input_event *ev)
{
	int rc;
	rc = fprintf(fp, "E: %lu.%06u %04x %04x %04d	",
		     ev->time.tv_sec, (unsigned)ev->time.tv_usec,
		     ev->type, ev->code, ev->value);
	rc += write_event_desc(fp, ev);
	return rc;
}

static inline long time_to_long(const struct timeval *tv) {
	return tv->tv_sec * 1000000L + tv->tv_usec;
}

static inline struct timeval long_to_time(long time) {
	struct timeval tv;
	tv.tv_sec = time/1000000L;
	tv.tv_usec = time % 1000000L;
	return tv;
}

int evemu_record(FILE *fp, int fd, int ms)
{
	struct pollfd fds = { fd, POLLIN, 0 };
	struct input_event ev;
	int ret;
	long offset = 0;

	while (poll(&fds, 1, ms) > 0) {
		SYSCALL(ret = read(fd, &ev, sizeof(ev)));
		if (ret < 0)
			return ret;
		if (ret == sizeof(ev)) {
			long time;

			if (offset == 0)
				offset = time_to_long(&ev.time) - 1;

			time = time_to_long(&ev.time);
			ev.time = long_to_time(time - offset);
			evemu_write_event(fp, &ev);
			fflush(fp);
		}
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

	do {
		if (!next_line(fp, &line, &size))
			goto out;
	} while(strlen(line) > 2 && strncmp(line, "E:", 2) != 0);

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

static inline unsigned long s2us(unsigned long s)
{
	return s * 1000000L;
}

static inline unsigned long us2s(unsigned long us)
{
	return us / 1000000L;
}

int evemu_read_event_realtime(FILE *fp, struct input_event *ev,
			      struct timeval *evtime)
{
	unsigned long usec;
	const unsigned long ERROR_MARGIN = 150; /* µs */
	int ret;

	ret = evemu_read_event(fp, ev);
	if (ret <= 0)
		return ret;

	if (evtime) {
		if (evtime->tv_sec == 0 && evtime->tv_usec == 0)
			*evtime = ev->time;
		usec = time_to_long(&ev->time) - time_to_long(evtime);
		if (usec > ERROR_MARGIN * 2) {
			if (usec > s2us(10))
				error(INFO, "Sleeping for %lds.\n", us2s(usec));
			usleep(usec - ERROR_MARGIN);
			*evtime = ev->time;
		}
	}

	return ret;
}

int evemu_play_one(int fd, const struct input_event *ev)
{
	int ret;
	SYSCALL(ret = write(fd, ev, sizeof(*ev)));
	return (ret == -1 || (size_t)ret < sizeof(*ev)) ? -1 : 0;
}

static void evemu_warn_about_incompatible_event(struct input_event *ev)
{
	const int max_warnings = 3;
	static int warned = 0;

	if (++warned <= max_warnings) {
		if (warned == 1)
			error(WARNING, "You are trying to play events incompatbile with this device. "
					"Is this the right device/recordings file?\n");
		error(WARNING, "%s %s is not supported by this device.\n",
				libevdev_event_type_get_name(ev->type),
				libevdev_event_code_get_name(ev->type, ev->code));
	} else if (warned == max_warnings + 1) {
		error(INFO, "warned about incompatible events %d times. Will be quiet now.\n",
				warned - 1);
	}
}

int evemu_play(FILE *fp, int fd)
{
	struct input_event ev;
	struct timeval evtime;
	int ret;
	struct evemu_device *dev;

	dev = evemu_new(NULL);
	if (dev) {
		if (evemu_extract(dev, fd) != 0) {
			evemu_delete(dev);
			dev = NULL;
		}
	}

	memset(&evtime, 0, sizeof(evtime));
	while (evemu_read_event_realtime(fp, &ev, &evtime) > 0) {
		if (dev &&
		    (ev.type != EV_SYN || ev.code != SYN_MT_REPORT) &&
		    !evemu_has_event(dev, ev.type, ev.code))
			evemu_warn_about_incompatible_event(&ev);
		SYSCALL(ret = write(fd, &ev, sizeof(ev)));
	}

	if (dev)
		evemu_delete(dev);
	return 0;
}

int evemu_create(struct evemu_device *dev, int fd)
{
	return libevdev_uinput_create_from_device(dev->evdev, fd, &dev->uidev);
}

int evemu_create_managed(struct evemu_device *dev)
{
	return libevdev_uinput_create_from_device(dev->evdev,
		LIBEVDEV_UINPUT_OPEN_MANAGED, &dev->uidev);
}

const char *evemu_get_devnode(struct evemu_device *dev)
{
	return libevdev_uinput_get_devnode(dev->uidev);
}

void evemu_destroy(struct evemu_device *dev)
{
	if (dev->uidev) {
		libevdev_uinput_destroy(dev->uidev);
		dev->uidev = NULL;
	}
}
