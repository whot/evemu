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
#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>

#define WAIT_MS 10000

FILE *output;

static void handler (int sig __attribute__((unused)))
{
	fflush(output);
	if (output != stdout) {
		fclose(output);
		output = stdout;
	}
}

int main(int argc, char *argv[])
{
	int fd;
	struct sigaction act;

	if (argc < 2) {
		fprintf(stderr, "Usage: %s <device> [output file]\n", argv[0]);
		return -1;
	}
	fd = open(argv[1], O_RDONLY | O_NONBLOCK);
	if (fd < 0) {
		fprintf(stderr, "error: could not open device\n");
		return -1;
	}

	if (ioctl(fd, EVIOCGRAB, (void*)1) < 0) {
		fprintf(stderr, "error: this device is grabbed and I cannot record events\n");
		return -1;
	} else
		ioctl(fd, EVIOCGRAB, (void*)0);

	memset (&act, '\0', sizeof(act));
	act.sa_handler = &handler;

	if (sigaction(SIGTERM, &act, NULL) < 0) {
		fprintf (stderr, "Could not attach TERM signal handler.\n");
		return 1;
	}
	if (sigaction(SIGINT, &act, NULL) < 0) {
		fprintf (stderr, "Could not attach INT signal handler.\n");
		return 1;
	}

	if (argc < 3)
		output = stdout;
	else {
		output = fopen(argv[2], "w");
		if (!output) {
			fprintf(stderr, "error: could not open output file");
		}
	}

	if (evemu_record(output, fd, WAIT_MS)) {
		fprintf(stderr, "error: could not describe device\n");
	}
	close(fd);
	if (output != stdout) {
		fclose(output);
		output = stdout;
	}
	return 0;
}
