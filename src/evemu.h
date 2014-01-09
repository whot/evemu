/*****************************************************************************
 *
 * evemu - Kernel device emulation
 *
 * Copyright (C) 2010-2012 Canonical Ltd.
 *
 * This library is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License version 3
 * as published by the Free Software Foundation.
 *
 * This library is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranties of
 * MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library.  If not, see <http://www.gnu.org/licenses/>.
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

#ifndef EVEMU_H
#define EVEMU_H

#include <stdio.h>
#include <errno.h>
#include <linux/input.h>

#ifdef __cplusplus
extern "C" {
#endif

#define EVEMU_VERSION		0x00010000

/**
 * evemu_new() - allocate a new evemu device
 * @name: wanted input device name (or NULL to leave empty)
 *
 * This function allocates a new evemu device structure and
 * initializes all fields to zero. If name is non-null and the length
 * is sane, it is copied to the device name.
 *
 * Returns NULL in case of memory failure.
 */
struct evemu_device *evemu_new(const char *name);

/**
 * evemu_delete() - free and allocated evemu device
 * @dev: the device to free
 *
 * The device pointer is invalidated by this call.
 */
void evemu_delete(struct evemu_device *dev);

/**
 * evemu_get_version() - get library version
 * @dev: the device in use
 *
 * Returns the library version used to create this evemu instance. The
 * version may differ from the value of EVEMU_VERSION in this header
 * file.
 */
unsigned int evemu_get_version(const struct evemu_device *dev);

/**
 * evemu_get_name() - get device name
 * @dev: the device in use
 *
 * Returns the name of the device. The pointer is owned by the evemu
 * instance and has evemu scope.
 */
const char *evemu_get_name(const struct evemu_device *dev);

/**
 * evemu_set_name() - set device name
 * @dev: the device in use
 *
 * Sets the name of the device. If name is non-null and the length is
 * sane, it is copied to the device name.
 */
void evemu_set_name(struct evemu_device *dev, const char *name);

/**
 * evemu_get_id_bustype() - get kernel device bustype
 * @dev: the device in use
 *
 * Returns the kernel bus type used by the device.
 */
unsigned int evemu_get_id_bustype(const struct evemu_device *dev);

/**
 * evemu_set_id_bustype() - set kernel bustype
 *
 * @dev: the device in use
 * @bustype: the bustype value to set.
 */
void evemu_set_id_bustype(struct evemu_device *dev, unsigned int bustype);

/**
 * evemu_get_id_vendor() - get kernel device vendor id
 * @dev: the device in use
 *
 * Returns the kernel vendor id used by the device.
 */
unsigned int evemu_get_id_vendor(const struct evemu_device *dev);

/**
 * evemu_set_id_vendor() - set kernel device vendor id
 *
 * @dev: the device in use
 * @vendor: the vendor id value to set.
 */
void evemu_set_id_vendor(struct evemu_device *dev, unsigned int vendor);

/**
 * evemu_get_id_product() - get kernel device product id
 * @dev: the device in use
 *
 * Returns the kernel product id used by the device.
 */
unsigned int evemu_get_id_product(const struct evemu_device *dev);

/**
 * evemu_set_id_product() - set kernel device product id
 *
 * @dev: the device in use
 * @product: the product id value to set.
 */
void evemu_set_id_product(struct evemu_device *dev, unsigned int product);

/**
 * evemu_get_id_version() - get kernel device id version
 * @dev: the device in use
 *
 * Returns the kernel device id used by the device.
 */
unsigned int evemu_get_id_version(const struct evemu_device *dev);

/**
 * evemu_set_id_version() - set kernel device id version
 *
 * @dev: the device in use
 * @version: the version value to set.
 */
void evemu_set_id_version(struct evemu_device *dev, unsigned int version);

/**
 * evemu_get_abs_minimum() - get kernel minimum value of event type
 * @dev: the device in use
 * @code: the event type code to query
 *
 * Returns the range minimum of the specified event type.
 */
int evemu_get_abs_minimum(const struct evemu_device *dev, int code);

/**
 * evemu_set_abs_minimum() - set kernel minimum value of event type
 *
 * @dev: the device in use
 * @code: the event type code to set
 * @min: the minimum value to set
 */
void evemu_set_abs_minimum(struct evemu_device *dev, int code, int min);

/**
 * evemu_get_abs_maximum() - get kernel maximum value of event type
 * @dev: the device in use
 * @code: the event type code to query
 *
 * Returns the range maximum of the specified event type.
 */
int evemu_get_abs_maximum(const struct evemu_device *dev, int code);

/**
 * evemu_get_abs_current_value() - get kernel current value of event type
 * @dev: the device in use
 * @code: the event type code to query
 *
 * Returns the current value of the specified event type.
 */
int evemu_get_abs_current_value(const struct evemu_device *dev, int code);


/**
 * evemu_set_abs_maximum() - set kernel maximum value of event type
 *
 * @dev: the device in use
 * @code: the event type code to set
 * @max: the maximum value to set
 */
void evemu_set_abs_maximum(struct evemu_device *dev, int code, int max);

/**
 * evemu_get_abs_maximum() - get kernel filter fuzz of event type
 * @dev: the device in use
 * @code: the event type code to query
 *
 * Returns the filter fuzz of the specified event type.
 */
int evemu_get_abs_fuzz(const struct evemu_device *dev, int code);

/**
 * evemu_set_abs_fuzz() - set kernel filter fuzz of event type
 *
 * @dev: the device in use
 * @code: the event type code to set
 * @fuzz: the fuzz value to set
 */
void evemu_set_abs_fuzz(struct evemu_device *dev, int code, int fuzz);

/**
 * evemu_get_abs_maximum() - get kernel flat value of event type
 * @dev: the device in use
 * @code: the event type code to query
 *
 * Returns the flat value of the specified event type. Only used for
 * joysticks.
 */
int evemu_get_abs_flat(const struct evemu_device *dev, int code);

/**
 * evemu_set_abs_flat() - set kernel filter flat of event type
 *
 * @dev: the device in use
 * @code: the event type code to set
 * @flat: the flat value to set
 */
void evemu_set_abs_flat(struct evemu_device *dev, int code, int flat);

/**
 * evemu_get_abs_resolution() - get kernel resolution of event type
 * @dev: the device in use
 * @code: the event type code to query
 *
 * Returns the resolution of the specified event type. Resolution is
 * specified in units per millimeter (units/mm), or units per radian
 * where appropriate.
 */
int evemu_get_abs_resolution(const struct evemu_device *dev, int code);

/**
 * evemu_set_abs_resolution() - set kernel resolution of event type
 * @dev: the device in use
 * @code: the event type code to set
 * @res: the resolution value to set.
 *
 * Resolution is specified in units per millimeter (units/mm), or units per
 * radian where appropriate.
 */
void evemu_set_abs_resolution(struct evemu_device *dev, int code, int res);

/**
 * evemu_has_prop() - check if device has a certain property
 * @dev: the device in use
 * @code: the property type code to query
 *
 * Returns true if the device has the given property.
 */
int evemu_has_prop(const struct evemu_device *dev, int code);

/**
 * evemu_has_event() - check if device has a certain event type
 * @dev: the device in use
 * @code: the event type code to query
 *
 * Returns true if the event type is supported by the device.
 */
int evemu_has_event(const struct evemu_device *dev, int type, int code);

/**
 * evemu_has_bit() - check if a device has a certain EV_* bit set
 * @dev: the device in use
 * @type: the EV_* bit to query
 *
 * Returns true if the event bit is supported by the device.
 */
int evemu_has_bit(const struct evemu_device *dev, int type);

/**
 * evemu_extract() - configure evemu instance directly from the kernel device
 * @dev: the device in use
 * @fd: file descriptor of the kernel device to query
 *
 * Returns zero if successful, negative error otherwise.
 */
int evemu_extract(struct evemu_device *dev, int fd);

/**
 * evemu_write() - write evemu configuration to a file
 * @dev: the device in use
 * @fp: file pointer to write the evemu configuration to
 *
 * Returns zero if successful, negative error otherwise.
 */
int evemu_write(const struct evemu_device *dev, FILE *fp);

/**
 * evemu_read() - read evemu configuration from a file
 * @dev: the device in use
 * @fp: file pointer to read the evemu configuration from
 *
 * Returns a positive number if successful, zero or negative error
 * otherwise.
 */
int evemu_read(struct evemu_device *dev, FILE *fp);

/**
 * evemu_write_event() - write kernel event to file
 * @fp: file pointer to write the event to
 * @ev: pointer to the kernel event to write
 *
 * Writes the kernel event to the file.
 *
 * Returns a positive number if successful, zero or negative error
 * otherwise.
 */
int evemu_write_event(FILE *fp, const struct input_event *ev);

/**
 * evemu_create_event() - Create a single event
 * @ev: pointer to the kernel event to be filled
 * @type: the event type to set
 * @code: the event code to set
 * @value: the event value to set
 */
int evemu_create_event(struct input_event *ev, int type, int code, int value);

/**
 * evemu_read_event() - read kernel event from file
 * @fp: file pointer to read the event from
 * @ev: pointer to the kernel event to be filled
 *
 * Reads a kernel event from the file.
 *
 * Returns a positive number if successful, zero or negative error
 * otherwise.
 */
int evemu_read_event(FILE *fp, struct input_event *ev);

/**
 * evemu_read_event_realtime() - read kernel events in realtime
 * @fp: file pointer to read the event from
 * @ev: pointer to the kernel event to be filled
 * @evtime: pointer to a timeval struct
 *
 * The evtime struct should be cleared (zeroed) before the first call
 * to this function. This function reads a kernel event from the file,
 * and performs the microsleep necessary to deliver the event with the
 * same timings as originally received.
 *
 * Returns a positive number if successful, zero or negative error
 * otherwise.
 */
int evemu_read_event_realtime(FILE *fp, struct input_event *ev,
			      struct timeval *evtime);

/**
 * evemu_record() - read events directly from a kernel device
 * @fp: file pointer to write the events to
 * @fd: file descriptor of kernel device to read from
 * @ms: maximum time to wait for an event to appear before reading (ms)
 *
 * Continuously reads events from the kernel device and writes them to
 * the file. The function terminates after ms milliseconds of
 * inactivity.
 *
 * Returns zero if successful, negative error otherwise.
 */
int evemu_record(FILE *fp, int fd, int ms);


/**
 * evemu_play_one() - play one event to kernel device
 * @fd: file descriptor of kernel device to write to
 * @ev: pointer to the kernel event to be played
 *
 * Returns zero if successful, negative error otherwise.
 */
int evemu_play_one(int fd, const struct input_event *ev);

/**
 * evemu_play() - replay events from file to kernel device in realtime
 * @fp: file pointer to read the events from
 * @fd: file descriptor of kernel device to write to
 *
 * Contiuously reads events from the file and writes them to the
 * kernel device, in realtime. The function terminates when end of
 * file has been reached.
 *
 * Returns zero if successful, negative error otherwise.
 */
int evemu_play(FILE *fp, int fd);

/**
 * evemu_create() - create a kernel device from the evemu configuration
 * @dev: the device in use
 * @fd: file descriptor of the special kernel uinput device
 *
 * Creates a new device with all the properties of the evemu device.
 *
 * Returns zero if successful, negative error otherwise.
 */
int evemu_create(struct evemu_device *dev, int fd);

/**
 * evemu_create_managed() - create a kernel device from the evemu configuration
 * @dev: the device in use
 *
 * Creates a new device with all the properties of the evemu device.
 * Compared to evemu_create, evemu will take care of the handling of the uinput
 * file descriptor.
 *
 * Returns zero if successful, negative error otherwise.
 */
int evemu_create_managed(struct evemu_device *dev);

/**
 * evemu_get_devnode() - get device node
 * @dev: the device in use
 *
 * Returns the input device node of the virtual device. The pointer is owned by
 * the evemu instance and has evemu scope.
 */
const char *evemu_get_devnode(struct evemu_device *dev);

/**
 * evemu_destroy() - destroy all created kernel devices
 * @dev: the device to destroy
 *
 * Destroys all devices created using this file descriptor.
 */
void evemu_destroy(struct evemu_device *dev);

#ifdef __cplusplus
}
#endif

#endif
