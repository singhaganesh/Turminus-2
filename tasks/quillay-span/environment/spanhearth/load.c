void ring_pump(void) {
  volatile int x = 1;
#if WAVE >= 2
  volatile char pad[4096];
  pad[0] = (char)x;
#endif
  (void)x;
}

void dusk_lamp(void) {
  volatile int y = 2;
  (void)y;
}

#if WAVE >= 3
void held_wick(void) {
  volatile int z = 3;
  (void)z;
}
#endif

int main(void) {
  ring_pump();
  dusk_lamp();
#if WAVE >= 3
  held_wick();
#endif
  return 0;
}
