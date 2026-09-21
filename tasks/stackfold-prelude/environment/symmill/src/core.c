#include <stdint.h>

uint32_t legacy_worker(uint32_t seed);

int main(void)
{
    return (int)legacy_worker(0x11U);
}

int runtime_entry(uint32_t seed)
{
    uint32_t base = legacy_worker(seed);
    return base + 17U;
}
