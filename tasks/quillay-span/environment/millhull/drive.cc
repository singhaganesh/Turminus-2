#include "bind.h"
#include "mesh.h"
#include "lay.h"

int go_scribe(void) {
  struct Lay lay;
  int reuse = op_bind("/app/hearthbin/span.elf", &lay);
  if (reuse < 0) return 1;
  if (op_mesh("/app/hearthbin/span.elf", &lay, reuse) != 0) return 1;
  return 0;
}
