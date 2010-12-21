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

#ifndef _EVEMU_H
#define _EVEMU_H

#include <stdio.h>
#include <errno.h>
#include <linux/input.h>

#define EVEMU_VERSION_MAJOR	1
#define EVEMU_VERSION_MINOR	1

struct evemu_device *evemu_new(const char *name);
void evemu_delete(struct evemu_device *dev);

int evemu_get_version_major(const struct evemu_device *dev);
int evemu_get_version_minor(const struct evemu_device *dev);

const char *evemu_get_name(const struct evemu_device *dev);

unsigned int evemu_get_id_bustype(const struct evemu_device *dev);
unsigned int evemu_get_id_vendor(const struct evemu_device *dev);
unsigned int evemu_get_id_product(const struct evemu_device *dev);
unsigned int evemu_get_id_version(const struct evemu_device *dev);

int evemu_get_abs_minimum(const struct evemu_device *dev, int code);
int evemu_get_abs_maximum(const struct evemu_device *dev, int code);
int evemu_get_abs_fuzz(const struct evemu_device *dev, int code);
int evemu_get_abs_flat(const struct evemu_device *dev, int code);
int evemu_get_abs_resolution(const struct evemu_device *dev, int code);

int evemu_has_prop(const struct evemu_device *dev, int code);
int evemu_has_event(const struct evemu_device *dev, int type, int code);

int evemu_extract(struct evemu_device *dev, int fd);
int evemu_write(const struct evemu_device *dev, FILE *fp);
int evemu_read(struct evemu_device *dev, FILE *fp);

int evemu_write_event(FILE *fp, const struct input_event *ev);
int evemu_read_event(FILE *fp, struct input_event *ev);

int evemu_record(FILE *fp, int fd, int ms);
int evemu_play(FILE *fp, int fd);

int evemu_create(const struct evemu_device *dev, int fd);
void evemu_destroy(int fd);

#endif
