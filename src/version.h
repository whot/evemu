/*****************************************************************************
 *
 * evemu - Kernel device emulation
 *
 * Copyright (C) 2013 Red Hat, Inc.
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

#ifndef __VERSION_H__
#define __VERSION_H__

#include <stdint.h>

typedef struct {
	uint32_t _v; /* major << 16  | minor */
} version_t;

static inline uint16_t version_major(version_t* v) {
	return (v->_v >> 16) & 0xFFFF;
}

static inline uint16_t version_minor(version_t* v) {
	return v->_v & 0xFFFF;
}

static inline version_t version_new(uint16_t major, uint16_t minor)
{
	version_t v = { ._v = major << 16 | minor };
	return v;
}

/**
 * Compare a to b, return
 * - a negative value if a is less than b
 * - zero if a is equal b
 * - a positive value if a is reater than b
 */
static inline int
version_compare(version_t *version_a, version_t *version_b)
{
	return  version_a->_v - version_b->_v;
}

static inline int
version_compare_numeric(version_t *version, uint16_t major, uint16_t minor)
{
	version_t b = version_new(major, minor);
	return version_compare(version, &b);
}


#endif /* __VERSION_H__ */
