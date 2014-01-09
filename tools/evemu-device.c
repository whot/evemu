/*****************************************************************************
 *
 * evemu - Kernel device emulation
 *
 * Copyright (C) 2010-2012 Canonical Ltd.
 *
 * This program is free software: you can redistribute it and/or modify it 
 * under the terms of the GNU General Public License version 3 as published 
 * by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program.  If not, see <http://www.gnu.org/licenses/>.
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

#include "evemu.h"
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

/*
 * Finds the newly created device node and holds it open.
 */
static void hold_device(struct evemu_device *dev)
{
	char data[256];
	int ret;
	int fd;

	const char *device_node = evemu_get_devnode(dev);
	if (!device_node)
	{
		fprintf(stderr, "can not determine device node\n");
		return;
	}

	fd = open(device_node, O_RDONLY);
	if (fd < 0)
	{
		fprintf(stderr, "error %d opening %s: %s\n",
			errno, device_node, strerror(errno));
	  return;
	}
	fprintf(stdout, "%s: %s\n", evemu_get_name(dev), device_node);
	fflush(stdout);
	while ((ret = read(fd, data, sizeof(data))) > 0);
	close(fd);
}

static int evemu_device(FILE *fp)
{
	struct evemu_device *dev;
	int ret = -ENOMEM;

	dev = evemu_new(NULL);
	if (!dev)
		goto out;
	ret = evemu_read(dev, fp);
	if (ret <= 0)
		goto out;

	if (strlen(evemu_get_name(dev)) == 0) {
		char name[64];
		sprintf(name, "evemu-%d", getpid());
		evemu_set_name(dev, name);
	}

	ret = evemu_create_managed(dev);
	if (ret < 0)
		goto out;
	hold_device(dev);
	evemu_destroy(dev);

out:
	evemu_delete(dev);

	return ret;
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
	ret = evemu_device(fp);
	if (ret <= 0) {
		fprintf(stderr, "error: could not create device: %d\n", ret);
		return -1;
	}
	fclose(fp);
	return 0;
}
