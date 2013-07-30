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

#define UINPUT_NODE "/dev/uinput"
#define MAX_EVENT_NODE 32
#define SYS_INPUT_DIR "/sys/class/input"


/*
 * Extracts the device number from the event file name.
 */
static int _device_number_from_event_file_name(const char *event_file_name)
{
  int device_number = -1;
  sscanf(event_file_name, "event%d", &device_number);
  return device_number;
}


/*
 * A filter that passes only input event file names.
 */
static int _filter_event_files(const struct dirent *d)
{
  return 0 == strncmp("event", d->d_name, sizeof("event")-1);
}


/*
 * A strict weak ordering function to compare two event file names.
 */
static int _sort_event_files(const struct dirent **lhs, const struct dirent **rhs)
{
  int d1 = _device_number_from_event_file_name((*lhs)->d_name);
  int d2 = _device_number_from_event_file_name((*rhs)->d_name);
  return (d1 > d2) ? -1 : (d1 == d2) ? 0 : 1;
}


/*
 * Finds the device node that has a matching device name and the most recent
 * creation time.
 */
static char * _find_newest_device_node_with_name(const char *device_name)
{
  struct dirent **event_file_list;
  time_t  newest_node_time = 0;
  char   *newest_node_name = NULL;
  int i;

  int event_file_count = scandir(SYS_INPUT_DIR,
                                 &event_file_list,
                                 _filter_event_files,
                                 _sort_event_files);
  if (event_file_count < 0)
  {
    fprintf(stderr, "error %d opening %s: %s\n",
            errno, SYS_INPUT_DIR, strerror(errno));
    return NULL;
  }

  for (i = 0; i < event_file_count; ++i)
  {
    int device_number = _device_number_from_event_file_name(event_file_list[i]->d_name);

    char name_file_name[48];
    FILE *name_file;
    char name[128];
    size_t name_length;

    /* get the name of the device */
    sprintf(name_file_name, SYS_INPUT_DIR "/event%d/device/name", device_number);
    name_file = fopen(name_file_name, "r");
    if (!name_file)
    {
      fprintf(stderr, "error %d opening %s: %s\n",
              errno, name_file_name, strerror(errno));
      goto next_file;
    }
    name_length = fread(name, sizeof(char), sizeof(name)-1, name_file);
    fclose(name_file);

    if (name_length <= 1)
      goto next_file;

    /* trim the trailing newline */
    name[name_length-1] = 0;

    /* if the device name matches, compare the creation times */
    if (0 == strcmp(name, device_name))
    {
      char input_name[32];
      struct stat sbuf;
      int sstat;

      sprintf(input_name, "/dev/input/event%d", device_number);
      sstat = stat(input_name, &sbuf);
      if (sstat < 0)
      {
        fprintf(stderr, "error %d stating %s: %s\n",
                errno, name_file_name, strerror(errno));
        goto next_file;
      }

      if (sbuf.st_ctime > newest_node_time)
      {
        newest_node_time = sbuf.st_ctime;
        free(newest_node_name);
        newest_node_name = strdup(input_name);
      }
    }

next_file:
    free(event_file_list[i]);
  }
  free(event_file_list);

  return newest_node_name;
}


/*
 * Finds the newly created device node and holds it open.
 */
static void hold_device(const struct evemu_device *dev)
{
	char data[256];
	int ret;
	int fd;

        char *device_node = _find_newest_device_node_with_name(evemu_get_name(dev));
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
	free(device_node);
}

static int evemu_device(FILE *fp)
{
	struct evemu_device *dev;
	char name[64];
	int ret = -ENOMEM;
	int fd;

	sprintf(name, "evemu-%d", getpid());

	dev = evemu_new(name);
	if (!dev)
		goto out;
	ret = evemu_read(dev, fp);
	if (ret <= 0)
		goto out;

	ret = fd = open(UINPUT_NODE, O_WRONLY);
	if (ret < 0)
		goto out;

	ret = evemu_create(dev, fd);
	if (ret < 0)
		goto out_close;
	hold_device(dev);
	evemu_destroy(dev, fd);

out_close:
	close(fd);
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
