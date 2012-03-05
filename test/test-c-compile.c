/*
 * Test that compiling+linking works with a C compiler.
 */

#include <stdio.h>
#include <evemu.h>

#define UNUSED __attribute__((unused))

int main(int argc UNUSED, char **argv UNUSED) {
    struct evemu_device *dummy = evemu_new("dummy");
    if(!dummy) {
        printf("This should really not be happening.\n");
        return 1;
    }
    return 0;
}
