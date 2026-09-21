#include "elfbits.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint16_t u16(const unsigned char *p) {
  return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

static uint32_t u32(const unsigned char *p) {
  return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) |
         ((uint32_t)p[3] << 24);
}

static uint64_t u64(const unsigned char *p) {
  uint64_t v = 0;
  for (int i = 7; i >= 0; i--) v = (v << 8) | p[i];
  return v;
}

static int slurp(const char *path, unsigned char **out, size_t *n) {
  FILE *fp = fopen(path, "rb");
  if (!fp) return -1;
  fseek(fp, 0, SEEK_END);
  long sz = ftell(fp);
  if (sz < 64) {
    fclose(fp);
    return -1;
  }
  rewind(fp);
  unsigned char *buf = new unsigned char[sz];
  if (fread(buf, 1, sz, fp) != (size_t)sz) {
    delete[] buf;
    fclose(fp);
    return -1;
  }
  fclose(fp);
  *out = buf;
  *n = (size_t)sz;
  return 0;
}

int fill_text(const char *path, unsigned long long *vma, unsigned long long *off,
               unsigned long long *sz) {
  unsigned char *buf = 0;
  size_t n = 0;
  if (slurp(path, &buf, &n) != 0) return -1;
  if (n < 64 || buf[0] != 0x7f || buf[1] != 'E' || buf[2] != 'L' || buf[3] != 'F') {
    delete[] buf;
    return -1;
  }
  uint64_t phoff = u64(buf + 32);
  uint16_t phentsize = u16(buf + 54);
  uint16_t phnum = u16(buf + 56);
  int found = 0;
  for (uint16_t i = 0; i < phnum; i++) {
    unsigned char *ph = buf + phoff + (size_t)i * phentsize;
    uint32_t type = u32(ph);
    uint32_t flags = u32(ph + 4);
    if (type == 1 && (flags & 1)) {
      *off = u64(ph + 8);
      *vma = u64(ph + 16);
      *sz = u64(ph + 32);
      found = 1;
      break;
    }
  }
  delete[] buf;
  return found ? 0 : -1;
}

int name_at(const char *path, unsigned long long pc, char *out, int ncap) {
  unsigned char *buf = 0;
  size_t n = 0;
  if (slurp(path, &buf, &n) != 0) return -1;
  uint64_t shoff = u64(buf + 40);
  uint16_t shentsize = u16(buf + 58);
  uint16_t shnum = u16(buf + 60);
  unsigned char *sym = 0, *str = 0;
  uint64_t symsz = 0;
  for (uint16_t i = 0; i < shnum; i++) {
    unsigned char *sh = buf + shoff + (size_t)i * shentsize;
    uint32_t type = u32(sh + 4);
    if (type == 2) {
      uint32_t link = u32(sh + 24);
      uint64_t offset = u64(sh + 24 + 8);
      uint64_t size = u64(sh + 32);
      unsigned char *strsh = buf + shoff + (size_t)link * shentsize;
      uint64_t stroff = u64(strsh + 24);
      sym = buf + offset;
      str = buf + stroff;
      /* ELF64 SHT_SYMTAB: sh_offset at 24, sh_size at 32, sh_link at 40? */
      (void)size;
      symsz = u64(sh + 32);
      (void)link;
    }
  }
  /* Re-parse with correct ELF64 section header offsets. */
  sym = 0;
  str = 0;
  symsz = 0;
  for (uint16_t i = 0; i < shnum; i++) {
    unsigned char *sh = buf + shoff + (size_t)i * shentsize;
    uint32_t type = u32(sh + 4);
    if (type != 2) continue;
    uint32_t link = u32(sh + 40);
    uint64_t offset = u64(sh + 24);
    uint64_t size = u64(sh + 32);
    unsigned char *strsh = buf + shoff + (size_t)link * shentsize;
    uint64_t stroff = u64(strsh + 24);
    sym = buf + offset;
    str = buf + stroff;
    symsz = size;
  }
  const char *best = "?";
  unsigned long long best_v = 0;
  if (sym && str) {
    for (uint64_t i = 0; i + 24 <= symsz; i += 24) {
      unsigned char *sy = sym + i;
      uint32_t name = u32(sy);
      unsigned char info = sy[4];
      uint64_t value = u64(sy + 8);
      uint64_t size = u64(sy + 16);
      int bind = info >> 4;
      int stype = info & 0xf;
      if (stype != 2 || value == 0) continue;
      (void)bind;
      unsigned long long lo = value;
      unsigned long long hi = value + (size ? size : 1);
      if (pc >= lo && pc < hi && lo >= best_v) {
        best_v = lo;
        best = (const char *)(str + name);
      }
    }
  }
  snprintf(out, ncap, "%s", best);
  delete[] buf;
  return 0;
}
