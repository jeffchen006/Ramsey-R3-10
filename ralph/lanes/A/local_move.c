#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static int in_build_dir(const char *path, const char *root)
{
    char parent[PATH_MAX], resolved[PATH_MAX];
    if (!path || strlen(path) >= sizeof(parent)) return 0;
    strcpy(parent, path);
    char *slash = strrchr(parent, '/');
    if (slash && slash == parent) slash[1] = '\0';
    else if (slash) *slash = '\0';
    else strcpy(parent, ".");
    if (!realpath(parent, resolved)) return 0;
    size_t length = strlen(root);
    return strncmp(resolved, root, length) == 0 &&
           (resolved[length] == '\0' || resolved[length] == '/');
}

int rename(const char *source, const char *destination)
{
    int (*original)(const char *, const char *) = dlsym(RTLD_NEXT, "rename");
    int status = original(source, destination);
    if (status == 0 || errno != EXDEV) return status;
    const char *root = getenv("R310_RUST_BUILD_DIR");
    if (!root || root[0] != '/' || !in_build_dir(source, root) ||
        !in_build_dir(destination, root)) {
        errno = EXDEV;
        return -1;
    }
    struct stat attributes;
    int input = open(source, O_RDONLY | O_NOFOLLOW | O_NONBLOCK);
    if (input < 0) return -1;
    if (fstat(input, &attributes) < 0 || !S_ISREG(attributes.st_mode)) {
        close(input);
        errno = EXDEV;
        return -1;
    }
    int output = open(destination, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW,
                      attributes.st_mode & 0777);
    if (output < 0) {
        int error = errno;
        close(input);
        errno = error;
        return -1;
    }
    char buffer[65536];
    ssize_t length;
    int error = 0;
    while ((length = read(input, buffer, sizeof(buffer))) > 0 && !error) {
        for (ssize_t offset = 0; offset < length;) {
            ssize_t written = write(output, buffer + offset, length - offset);
            if (written <= 0) {
                error = written < 0 ? errno : EIO;
                break;
            }
            offset += written;
        }
    }
    if (!error && length < 0) error = errno;
    close(input);
    if (close(output) < 0 && !error) error = errno;
    if (!error && unlink(source) < 0) error = errno;
    if (error) unlink(destination);
    errno = error;
    return error ? -1 : 0;
}
