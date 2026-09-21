#include <stdint.h>

uint32_t ring_dispatch(uint32_t lane);

uint32_t legacy_worker(uint32_t seed)
{
    uint32_t lane = (seed ^ 0xA5A5A5A5U) & 0xFFU;
    return ring_dispatch(lane) + seed;
}
