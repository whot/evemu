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
#define _GNU_SOURCE

#include "evemu.h"
#include <getopt.h>
#include <limits.h>
#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <linux/input.h>
#include <libevdev/libevdev.h>

static struct option opts[] = {
	{ "type", required_argument, 0, 't'},
	{ "code", required_argument, 0, 'c'},
	{ "value", required_argument, 0, 'v'},
	{ "sync", no_argument, 0, 's'},
	{ "device", required_argument, 0, 'd'}
};

static int parse_arg(const char *arg, long int *value)
{
	char *endp;

	*value = strtol(arg, &endp, 0);
	if (*arg == '\0' || *endp != '\0')
		return 1;
	return 0;
}

static int parse_type(const char *arg, long int *value)
{
	*value = libevdev_event_type_from_name(arg);
	if (*value != -1)
		return 0;

	return parse_arg(arg, value);
}

static int parse_code(long int type, const char *arg, long int *value)
{
	*value = libevdev_event_code_from_name(type, arg);
	if (*value != -1)
		return 0;

	return parse_arg(arg, value);
}

static void usage(void)
{
	fprintf(stderr, "Usage: %s [--sync] <device> --type <type> --code <code> --value <value>\n", program_invocation_short_name);
}

int main(int argc, char *argv[])
{
	int rc = -1;
	int fd = -1;
	long int type, code, value = LONG_MAX;
	struct input_event ev;
	int sync = 0;
	const char *path = NULL;
	const char *code_arg = NULL, *type_arg = NULL;

	if (argc < 5) {
		usage();
		goto out;
	}

	while(1) {
		int option_index = 0;
		int c;

		c = getopt_long(argc, argv, "", opts, &option_index);
		if (c == -1) /* we only do long options */
			break;

		switch(c) {
			case 't': /* type */
				type_arg = optarg;
				break;
			case 'c': /* code */
				code_arg = optarg;
				break;
			case 'v': /* value */
				if (parse_arg(optarg, &value) || value < INT_MIN || value > INT_MAX) {
					fprintf(stderr, "error: invalid value argument '%s'\n", optarg);
					goto out;
				}
				break;
			case 'd': /* device */
				path = optarg;
				break;
			case 's': /* sync */
				sync = 1;
				break;
			default:
				usage();
				goto out;
		}
	}

	if (!type_arg || !code_arg || value == LONG_MAX) {
		usage();
		goto out;
	}

	if (parse_type(type_arg, &type)) {
		fprintf(stderr, "error: invalid type argument '%s'\n", type_arg);
		goto out;
	}

	if (parse_code(type, code_arg, &code)) {
		fprintf(stderr, "error: invalid code argument '%s'\n", code_arg);
		goto out;
	}

	/* if device wasn't specified as option, take the remaining arg */
	if (optind < argc) {
		if (argc - optind != 1 || path) {
			usage();
			goto out;
		}
		path = argv[optind];
	}

	if (!path) {
		fprintf(stderr, "error: missing device path\n");
		usage();
		goto out;
	}

	fd = open(path, O_WRONLY);
	if (fd < 0) {
		fprintf(stderr, "error: could not open device (%m)\n");
		goto out;
	}

	if (evemu_create_event(&ev, type, code, value)) {
		fprintf(stderr, "error: failed to create event\n");
		goto out;
	}

	if (evemu_play_one(fd, &ev)) {
		fprintf(stderr, "error: could not play event\n");
		goto out;
	}

	if (sync) {
		if (evemu_create_event(&ev, EV_SYN, SYN_REPORT, 0)) {
			fprintf(stderr, "error: could not create SYN event\n");
			goto out;
		}
		if (evemu_play_one(fd, &ev)) {
			fprintf(stderr, "error: could not play SYN event\n");
			goto out;
		}
	}

	rc = 0;
out:
	if (fd > -1)
		close(fd);
	return rc;
}
