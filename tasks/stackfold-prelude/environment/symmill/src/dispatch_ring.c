#include <stdint.h>

uint32_t ring_dispatch(uint32_t lane)
{
    return (lane * 0x9E3779B1U) ^ 0xC3U;
}
