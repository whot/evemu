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
#include <stdio.h>
#include <fcntl.h>
#include <string.h>

#define UINPUT_NODE "/dev/uinput"
#define MAX_EVENT_NODE 32

static void hold_device(const struct evemu_device *dev)
{
	char node[256], data[256];
	int fd, ret, i;

	memset(node, 0, sizeof(node));
	for (i = 0; i < MAX_EVENT_NODE; i++) {
		char path[256], name[256];
		sprintf(path, "/sys/class/input/event%d/device/name", i + 1);
		memset(name, 0, sizeof(name));
		fd = open(path, O_RDONLY);
		if (fd < 0)
			continue;
		ret = read(fd, name, sizeof(name));
		if (ret > 0)
			name[ret - 1] = 0;
		if (!strcmp(dev->name, name))
			sprintf(node, "/dev/input/event%d", i + 1);
		close(fd);
	}

	fd = open(node, O_RDONLY);
	if (fd < 0)
		return;
	fprintf(stdout, "%s: %s\n", dev->name, node);
	fflush(stdout);
	while ((ret = read(fd, data, sizeof(data))) > 0);
	close(fd);
}

static int evemu_device(FILE *fp)
{
	struct evemu_device dev;
	int ret, fd;

	ret = evemu_read(&dev, fp);
	if (ret <= 0)
		return ret;

	sprintf(dev.name, "evemu-%d", getpid());

	fd = open(UINPUT_NODE, O_WRONLY);
	if (fd < 0)
		return fd;
	ret = evemu_create(&dev, fd);
	if (ret < 0)
		return ret;

	hold_device(&dev);

	evemu_destroy(fd);
	close(fd);

	return 0;
}

int main(int argc, char *argv[])
{
	FILE *fp;
	int ret;
	if (argc < 2) {
		fprintf(stderr, "Usage: %s <dev.prop>\n", argv[0]);
		return -1;
	}
	fp = fopen(argv[1], "r");
	if (!fp) {
		fprintf(stderr, "error: could not open file\n");
		return -1;
	}
	if ((ret = evemu_device(fp))) {
		fprintf(stderr, "error: could not create device: %d\n", ret);
		return -1;
	}
	fclose(fp);
	return 0;
}