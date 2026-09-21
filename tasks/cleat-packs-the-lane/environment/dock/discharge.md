# Discharge seats

Search order is on the lane cards. Seat plates in increasing `BOARD`, then
plate name. Remaining length, lane kilograms, paired deck kilograms, and sister
trim are those of plates already seated.

Remaining length includes the neighbour keep-clear and, for a hazmat plate, a
100 cm ramp keep-clear beyond its own length. The ramp keep-clear is empty of
other plates and does not move that plate's ramp-facing station. A clean plate
does not take a ramp keep-clear.

If a previous plate already sits in that lane and either plate has `HAZ=1`,
leave 100 cm empty before the new length. If both plates have `HAZ=1`, leave a
second 100 cm. The first plate in a lane never takes a leading gap.

A plate's `station` is centimetres from the ramp to its ramp-facing face. On a
2000 cm lane a 400 cm earliest plate sits at station 1600. The earliest packed
plate in a lane sits deepest. Later plates sit nearer the ramp. Chalk rows stay
in listing order.
