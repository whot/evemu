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

static const char *name		= "N: " NAME "";
static const char *ident	= "I: 0003 0004 0005 0006";
static const char *ffversion	= "# EVEMU 1.0";
static const char *comment	= "# some multiline\n#comment";
static const char *eolcomment	= "# end-of-line-comment";
static const char *props	= "P: %02x %02x %02x %02x %02x %02x %02x %02x";
static const char *bits		= "B: %02x %02x %02x %02x %02x %02x %02x %02x %02x";
static const char *absinfo	= "A: %02x %d %d %d %d";

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
	ALLFLAGS	 = (EOLCOMMENT << 1) - 1
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

void check_evemu_read(int fd, const char *file, enum flags flags)
{
	FILE *fp;
	struct evemu_device *dev;

	ftruncate(fd, 0);
	lseek(fd, 0, SEEK_SET);

	if (flags & FFVERSION)
		println(fd, flags, "%s", ffversion);
	if (flags & HEADER_COMMENT)
		println(fd, flags, "%s", comment);

	println(fd, flags & ~EOLCOMMENT, "%s", name);
	if (flags & LINE_COMMENT)
		println(fd, flags, "%s", comment);

	println(fd, flags, "%s", ident);
	if (flags & LINE_COMMENT)
		println(fd, flags, "%s", comment);

	/* We always set all prop bits. Should probably be more selective
	   about this */
	if (flags & PROPS) {
		int i;
		for (i = 0; i < INPUT_PROP_CNT; i += 8) {
			println(fd, flags, props, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff);
		}
	}

	/* We always set all ev bits. Should probably be more selective
	   about this */
	if (flags & BITS) {
		int i;
		for (i = 0; i < EV_CNT; i++) {
			int j;
			for (j = 0; j < max[i]; j += 8) {
				println(fd, flags, bits, i, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff);
			}
		}
	}

	if (flags & ABSINFO) {
		int i;
		for (i = 0; i < ABS_CNT; i++) {
			println(fd, flags, absinfo, i, i + 1, i + 2, i + 3, i + 4);
		}
	}

	fsync(fd);

	fp = fopen(file, "r");
	assert(fp);

	dev = evemu_new("test device");
	assert(dev);

	assert(evemu_read(dev, fp) >= 0);
	assert(strcmp(NAME, evemu_get_name(dev)) == 0);
	assert(evemu_get_id_bustype(dev) == 0x0003);
	assert(evemu_get_id_vendor(dev) == 0x0004);
	assert(evemu_get_id_product(dev) == 0x0005);
	assert(evemu_get_id_version(dev) == 0x0006);

	if (flags & PROPS) {
		int i;
		for (i = 0; i < INPUT_PROP_CNT; i++)
			assert(evemu_has_prop(dev, i));
	}

	if (flags & BITS) {
		int i, j;
		for (i = 0; i < EV_CNT; i++)
			for (j = 0; j < max[i]; j++)
				assert(evemu_has_event(dev, i, j));
	}

	if (flags & ABSINFO) {
		int i;
		for (i = 0; i < ABS_CNT; i++) {
			assert(evemu_get_abs_minimum(dev, i) == i + 1);
			assert(evemu_get_abs_maximum(dev, i) == i + 2);
			assert(evemu_get_abs_fuzz(dev, i) == i + 3);
			assert(evemu_get_abs_flat(dev, i) == i + 4);
		}
	}

	evemu_delete(dev);
	fclose(fp);
}

int main(int argc UNUSED, char **argv UNUSED) {
	int fd = 0;
	int flags = 0;

	char tmpname[] = "evemu.tmp.XXXXXXX";

	if ((fd = mkstemp(tmpname)) == -1) {
		perror("");
		return 1;
	}

	while (flags < ALLFLAGS)
		check_evemu_read(fd, tmpname, flags++);

	close(fd);
	unlink(tmpname);
	return 0;
}
