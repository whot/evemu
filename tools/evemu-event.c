/*****************************************************************************
 *
 * evemu - Kernel device emulation
 *
 * Copyright (C) 2011 Red Hat, Inc.
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 ****************************************************************************/

#include "evemu.h"
#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <linux/input.h>

int main(int argc, char *argv[])
{
	int fd;
	long int type, code, value;
	struct input_event ev;
	int idx = 1;
	int sync = 0;

	if (argc < 5) {
		fprintf(stderr, "Usage: %s [--sync] <device> <type> <code> <value>\n", argv[0]);
		return -1;
	}

	if (!strcmp(argv[1], "--sync")) {
		idx = 2;
		sync = 1;
	}

	fd = open(argv[idx++], O_WRONLY);
	if (fd < 0) {
		fprintf(stderr, "error: could not open device\n");
		return -1;
	}

	type = strtol(argv[idx++], NULL, 0);
	code = strtol(argv[idx++], NULL, 0);
	value = strtol(argv[idx++], NULL, 0);

	if (evemu_create_event(&ev, type, code, value)) {
		fprintf(stderr, "error: failed to create event\n");
		return -1;
	}

	if (evemu_play_one(fd, &ev)) {
		fprintf(stderr, "error: could not play event\n");
		return -1;
	}

	if (sync) {
		evemu_create_event(&ev, EV_SYN, SYN_REPORT, 0);
		evemu_play_one(fd, &ev);
	}

	close(fd);
	return 0;
}
