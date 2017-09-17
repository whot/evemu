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

#define _GNU_SOURCE
#include "evemu.h"
#include <assert.h>
#include <getopt.h>
#include <limits.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>

#include "find_event_devices.h"

#define INFINITE -1

static FILE *output;
static bool autorestart = false;

static int describe_device(FILE *output, int fd)
{
	struct evemu_device *dev;
	int ret = -ENOMEM;

	dev = evemu_new(NULL);
	if (!dev)
		goto out;
	ret = evemu_extract(dev, fd);
	if (ret)
		goto out;

	evemu_write(dev, output);
	fflush(output);
out:
	evemu_delete(dev);
	return ret;
}

static void handler (int sig __attribute__((unused)))
{
	fflush(output);
	if (output != stdout) {
		fclose(output);
		output = stdout;
	}
	autorestart = false;
}

static inline bool safe_atoi(const char *str, int *val)
{
	char *endptr;
	long v;

	v = strtol(str, &endptr, 10);
	if (str == endptr)
		return false;
	if (*str != '\0' && *endptr != '\0')
		return false;

	if (v > INT_MAX || v < INT_MIN)
		return false;

	*val = v;
	return true;
}

static inline void usage()
{
	fprintf(stderr, "Usage: %s [--autorestart=s] <device> [output file]\n",
		program_invocation_short_name);
	fprintf(stderr, "Options:\n");
	fprintf(stderr, "    --autorestart=s\n");
	fprintf(stderr, "	Terminate the current recording after <s> seconds\n"
			"	of inactivity and restart a new recording. This option requires\n"
			"	an output file, the file is suffixed with the date and time of \n"
			"	the recording's start.\n"
			"	The timeout must be greater than 0.\n"
			"	This option is only valid for evemu-record.\n");
}

static inline char* make_filename(const char *prefix)
{
	char *filename;
	struct tm *tm;
	time_t t;
	int rc;
	char buf[64];

	t = time(NULL);
	tm = localtime(&t);
	rc = strftime(buf, sizeof(buf), "%F-%T", tm);
	if (rc < 0)
		return NULL;

	rc = asprintf(&filename, "%s.%s", prefix, buf);
	if (rc < 0)
		return NULL;

	return filename;
}

static bool record_device(int fd, unsigned int timeout, const char *prefix)
{
	char *filename = NULL;
	bool rc = false;
	long ftell_start = 0 , ftell_end = 1;

	assert(!autorestart || prefix != NULL);

	do {
		free(filename);

		if (prefix == NULL) {
			output = stdout;
		} else {
			if (autorestart)
				filename = make_filename(prefix);
			else
				filename = strdup(prefix);
			if (filename == NULL) {
				fprintf(stderr, "error: failed to init the filename\n");
				goto out;
			}
			output = fopen(filename, "w");
			if (!output) {
				fprintf(stderr, "error: could not open output file (%m)");
				goto out;
			}
		}

		if (describe_device(output, fd)) {
			fprintf(stderr, "error: could not describe device\n");
			goto out;
		}

		fprintf(output,  "################################\n");
		fprintf(output,  "#      Waiting for events      #\n");
		fprintf(output,  "################################\n");
		if (autorestart) {
			fprintf(output, "# Autorestart timeout: %d\n", timeout);
			ftell_start = ftell(output);
		}

		if (evemu_record(output, fd, timeout)) {
			fprintf(stderr, "error: could not record device\n");
		} else if (autorestart) {
			ftell_end = ftell(output);
			fprintf(output, "# Closing after %ds inactivity\n",
				timeout/1000);
		}

		fflush(output);
		if (output != stdout) {
			fclose(output);
			output = stdout;

			if (autorestart && ftell_start == ftell_end)
				unlink(filename);
		}
	} while (autorestart);

	rc = true;

out:
	free(filename);
	return rc;
}

static inline bool test_grab_device(int fd)
{
	if (ioctl(fd, EVIOCGRAB, (void*)1) < 0) {
		fprintf(stderr, "error: this device is grabbed and I cannot record events\n");
		fprintf(stderr, "see the evemu-record man page for more information\n");
		return false;
	} else {
		ioctl(fd, EVIOCGRAB, (void*)0);
	}

	return true;
}

enum mode {
	EVEMU_RECORD,
	EVEMU_DESCRIBE
};

enum options {
	OPT_AUTORESTART,
};

int main(int argc, char *argv[])
{
	enum mode mode = EVEMU_RECORD;
	int fd = -1;
	struct sigaction act;
	char *prgm_name = program_invocation_short_name;
	char *device = NULL;
	int timeout = INFINITE;
	struct option opts[] = {
		{ "autorestart", required_argument, 0, OPT_AUTORESTART },
		{ 0, 0, 0, 0},
	};
	const char *prefix = NULL;
	int rc = 1;

	output = stdout;

	if (prgm_name && (strcmp(prgm_name, "evemu-describe") == 0 ||
			/* when run directly from the sources (not installed) */
			strcmp(prgm_name, "lt-evemu-describe") == 0))
		mode = EVEMU_DESCRIBE;

	while (1) {
		int c;
		int option_index = 0;

		c = getopt_long(argc, argv, "", opts, &option_index);
		if (c == -1)
			break;

		switch (c) {
			case OPT_AUTORESTART:
				if (!safe_atoi(optarg, &timeout) ||
				    timeout <= 0) {
					usage();
					goto out;
				}
				timeout *= 1000; /* sec to ms */
				autorestart = true;
				break;
			default:
				usage();
				goto out;
		}
	}

	device = (optind >= argc) ? find_event_devices() : strdup(argv[optind++]);

	if (device == NULL) {
		usage();
		goto out;
	}
	fd = open(device, O_RDONLY | O_NONBLOCK);
	if (fd < 0) {
		fprintf(stderr, "error: could not open device (%m)\n");
		goto out;
	}

	memset (&act, '\0', sizeof(act));
	act.sa_handler = &handler;

	if (sigaction(SIGTERM, &act, NULL) < 0) {
		fprintf (stderr, "Could not attach TERM signal handler (%m)\n");
		goto out;
	}
	if (sigaction(SIGINT, &act, NULL) < 0) {
		fprintf (stderr, "Could not attach INT signal handler (%m)\n");
		goto out;
	}

	if (optind >= argc) {
		if (autorestart) {
			fprintf(stderr, "Option --autoresume requires an output file\n");
			goto out;
		}
	} else {
		prefix = argv[optind++];
	}

	if (mode == EVEMU_RECORD) {
#ifdef EVIOCSCLOCKID
		int clockid = CLOCK_MONOTONIC;
		ioctl(fd, EVIOCSCLOCKID, &clockid);
#endif
		if (!test_grab_device(fd))
			goto out;

		record_device(fd, timeout,  prefix);

	} else if (mode == EVEMU_DESCRIBE) {
		if (prefix) {
			output = fopen(prefix, "w");
			if (!output) {
				fprintf(stderr, "error: could not open output file (%m)\n");
				goto out;
			}
		}

		if (describe_device(output, fd)) {
			fprintf(stderr, "error: could not describe device\n");
			goto out;
		}
	}

	rc = 0;
out:
	free(device);
	close(fd);
	if (output && output != stdout) {
		fclose(output);
		output = stdout;
	}
	return rc;
}
