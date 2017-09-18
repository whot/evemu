/*
 * Test that device creation works.
 */

#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <assert.h>
#include "evemu.h"
#include <linux/input.h>

#define UNUSED __attribute__((unused))

#define NAME "evemu test device"
#define CUSTOM_NAME "custom evemu test device"

static const char *name		= "N: " NAME "";
static const char *ident	= "I: 0003 0004 0005 0006";
static const char *ffversion	= "# EVEMU 1.0";
static const char *comment	= "# some multiline\n#comment";
static const char *emptyline	= "\n";
static const char *eolcomment	= "# end-of-line-comment";
static const char *props	= "P: %02x %02x %02x %02x %02x %02x %02x %02x";
static const char *bits		= "B: %02x %02x %02x %02x %02x %02x %02x %02x %02x";
static const char *absinfo	= "A: %02x %d %d %d %d";
static const char *event	= "E: %lu.%06u %04x %04x %d";

/* Set of flags used to specify what parts of the evemu file description
   gets written into the input file.
 */
enum flags {
	MINIMUM		 = 0,
	FFVERSION	 = (1 << 0), /* file format version */
	HEADER_COMMENT	 = (1 << 1), /* multi-line header comment */
	LINE_COMMENT	 = (1 << 2), /* multi-line comment between other lines */
	BITS		 = (1 << 3), /* some bits are set */
	ABSINFO		 = (1 << 4), /* has absinfo */
	PROPS		 = (1 << 5), /* has props */
	EOLCOMMENT	 = (1 << 6), /* end-of-line comment */
	EVENT		 = (1 << 7), /* event line */
	EMPTYLINE	 = (1 << 8),
	WITHNAME	 = (1 << 9), /* use evemu_new(custom name) */
	ALLFLAGS	 = (WITHNAME << 1) - 1
};

static int max[EV_CNT] = {
	0,	 /* EV_SYN */
	KEY_MAX, /* EV_KEY */
	REL_MAX, /* EV_REL */
	ABS_MAX, /* EV_ABS */
	MSC_MAX, /* EV_MSC */
	SW_MAX,  /* EV_SW */
	LED_MAX, /* EV_LED */
	SND_MAX, /* EV_SND */
	REP_MAX, /* EV_REP */
	FF_MAX   /* EV_FF */
};

static void println(int fd, int flags, const char *format, ...)
{
	va_list args;
	va_start(args, format);
	vdprintf(fd, format, args);
	dprintf(fd, "%s\n", (flags & EOLCOMMENT) ? eolcomment : "");
	va_end(args);
}

static void check_evemu_read(int fd, const char *file, enum flags flags)
{
	FILE *fp;
	struct evemu_device *dev;
	const char *device_name;
	int rc;

	rc = ftruncate(fd, 0);
	assert(rc == 0);
	lseek(fd, 0, SEEK_SET);

	if (flags & EMPTYLINE)
		println(fd, flags, "%s", emptyline);
	if (flags & FFVERSION)
		println(fd, flags, "%s", ffversion);
	if (flags & EMPTYLINE)
		println(fd, flags, "%s", emptyline);
	if (flags & HEADER_COMMENT)
		println(fd, flags, "%s", comment);
	if (flags & EMPTYLINE)
		println(fd, flags, "%s", emptyline);

	println(fd, flags & ~EOLCOMMENT, "%s", name);
	if (flags & LINE_COMMENT)
		println(fd, flags, "%s", comment);
	if (flags & EMPTYLINE)
		println(fd, flags, "%s", emptyline);

	println(fd, flags, "%s", ident);
	if (flags & LINE_COMMENT)
		println(fd, flags, "%s", comment);
	if (flags & EMPTYLINE)
		println(fd, flags, "%s", emptyline);

#ifdef INPUT_PROP_MAX
	/* We always set all prop bits. Should probably be more selective
	   about this */
	if (flags & PROPS) {
		int i;
		for (i = 0; i < INPUT_PROP_CNT; i += 8) {
			println(fd, flags, props, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff);
			if (flags & EMPTYLINE)
				println(fd, flags, "%s", emptyline);
		}
	}
#endif

	/* We always set all ev bits. Should probably be more selective
	   about this */
	if (flags & BITS) {
		int i;
		for (i = 0; i < EV_CNT; i++) {
			int j;
			for (j = 0; j <= max[i]; j += 8) {
				println(fd, flags, bits, i, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff);
				if (flags & EMPTYLINE)
					println(fd, flags, "%s", emptyline);
			}
		}
	}

	if (flags & ABSINFO) {
		int i;
		for (i = 0; i < ABS_CNT; i++) {
			println(fd, flags, absinfo, i, i + 1, i + 2, i + 3, i + 4);
			if (flags & EMPTYLINE)
				println(fd, flags, "%s", emptyline);
		}
	}

	if (flags & EVENT) {
		int i;
		for (i = 0; i < 20; i++) {
			println(fd, flags, event, 1, 2, 3, 4 ,5);
			if (flags & EMPTYLINE)
				println(fd, flags, "%s", emptyline);
		}
	}

	fsync(fd);

	fp = fopen(file, "r");
	assert(fp);

	if (flags & WITHNAME) {
		dev = evemu_new(CUSTOM_NAME);
		device_name = CUSTOM_NAME;
	} else {
		dev = evemu_new(NULL);
		device_name = NAME;
	}
	assert(dev);
	assert(evemu_read(dev, fp) >= 0);
	assert(strcmp(device_name, evemu_get_name(dev)) == 0);
	assert(evemu_get_id_bustype(dev) == 0x0003);
	assert(evemu_get_id_vendor(dev) == 0x0004);
	assert(evemu_get_id_product(dev) == 0x0005);
	assert(evemu_get_id_version(dev) == 0x0006);

#ifdef INPUT_PROP_MAX
	if (flags & PROPS) {
		int i;
		for (i = 0; i < INPUT_PROP_CNT; i++)
			assert(evemu_has_prop(dev, i));
	}
#endif

	if (flags & BITS) {
		int i, j;
		for (i = 1; i < EV_CNT; i++) {
			if (!evemu_has_bit(dev, i))
				continue;

			for (j = 0; j <= max[i]; j++)
				assert(evemu_has_event(dev, i, j));
		}
	}

	if (flags & ABSINFO) {
		int i;
		for (i = 0; i < ABS_CNT; i++) {
			if (!evemu_has_event(dev, EV_ABS, i))
				continue;
			assert(evemu_get_abs_minimum(dev, i) == i + 1);
			assert(evemu_get_abs_maximum(dev, i) == i + 2);
			assert(evemu_get_abs_fuzz(dev, i) == i + 3);
			assert(evemu_get_abs_flat(dev, i) == i + 4);
		}
	}

	evemu_delete(dev);
	fclose(fp);
}

static void check_valid_formats(int fd, const char *file)
{
	int flags = 0;
	while (flags < ALLFLAGS)
		check_evemu_read(fd, file, flags++);
}

int main(int argc UNUSED, char **argv UNUSED) {
	int fd = 0;

	char tmpname[] = "evemu.tmp.XXXXXXX";

	if ((fd = mkstemp(tmpname)) == -1) {
		perror("");
		return 1;
	}

	check_valid_formats(fd, tmpname);

	close(fd);
	unlink(tmpname);
	return 0;
}
