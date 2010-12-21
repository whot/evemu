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

#include <evemu.h>
#include <stdio.h>
#include <fcntl.h>
#include <string.h>

static int describe_device(int fd)
{
	struct evemu_device *dev;
	int ret = -ENOMEM;

	dev = evemu_new(0);
	if (!dev)
		goto out;
	ret = evemu_extract(dev, fd);
	if (ret)
		goto out;

	evemu_write(dev, stdout);
out:
	evemu_delete(dev);
	return ret;
}

int main(int argc, char *argv[])
{
	int fd;
	if (argc < 2) {
		fprintf(stderr, "Usage: %s <device>\n", argv[0]);
		return -1;
	}
	fd = open(argv[1], O_RDONLY);
	if (fd < 0) {
		fprintf(stderr, "error: could not open device\n");
		return -1;
	}
	if (describe_device(fd)) {
		fprintf(stderr, "error: could not describe device\n");
	}
	close(fd);
	return 0;
}
