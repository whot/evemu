/*****************************************************************************
 * Copyright (C) 2013 Red Hat, Inc
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
#include <linux/input.h>
#include <dirent.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>


#define DEV_INPUT_EVENT "/dev/input"
#define EVENT_DEV_NAME "event"

static int is_event_device(const struct dirent *dir) {
	return strncmp(EVENT_DEV_NAME, dir->d_name, 5) == 0;
}

char* find_event_devices(void)
{
	struct dirent **namelist;
	int i, ndev, devnum;
	char *filename;
	int max_device = 0;
	int rc;

	ndev = scandir(DEV_INPUT_EVENT, &namelist, is_event_device, versionsort);
	if (ndev <= 0)
		return NULL;

	fprintf(stderr, "Available devices:\n");

	for (i = 0; i < ndev; i++)
	{
		char fname[PATH_MAX];
		int fd = -1;
		char name[256] = "???";

		snprintf(fname, sizeof(fname),
			 "%s/%s", DEV_INPUT_EVENT, namelist[i]->d_name);
		fd = open(fname, O_RDONLY);
		if (fd < 0)
			continue;
		ioctl(fd, EVIOCGNAME(sizeof(name)), name);

		fprintf(stderr, "%s:	%s\n", fname, name);
		close(fd);

		rc = sscanf(namelist[i]->d_name, "event%d", &devnum);
		if (rc == 1 && devnum > max_device)
			max_device = devnum;

		free(namelist[i]);
	}

	fprintf(stderr, "Select the device event number [0-%d]: ", max_device);
	rc = scanf("%d", &devnum);

	if (rc != 1 || devnum > max_device || devnum < 0)
		return NULL;

	rc = asprintf(&filename, "%s/%s%d",
		      DEV_INPUT_EVENT, EVENT_DEV_NAME,
		      devnum);

	return rc == -1 ? NULL : filename;
}
