#ifndef TOKEN_H
#define TOKEN_H
enum { ROW_MAX = 128, NAME_MAX = 64, PATH_MAX_X = 256 };
typedef struct {
    char name[NAME_MAX];
    char path[PATH_MAX_X];
    int lo;
    int hi;
} Row;
int parse_unit(const char *path, Row *rows, int max);
int parse_lot(const char *path, char *name, char *orig, int *line);
int load_tbl(const char *path, Row *rows, int max);
int save_tbl(const char *path, Row *rows, int n);
int walk_units(const char *root, char paths[][PATH_MAX_X], int max);
int extract_span(const char *path, int lo, int hi, char *out, int cap);
int file_here(const char *path);
#endif
