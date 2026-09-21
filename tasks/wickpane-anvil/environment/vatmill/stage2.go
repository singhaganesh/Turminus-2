package main

import "loft.local/wickpane/celltyp"
import "loft.local/wickpane/pantryc"

func pipeBack(rows []celltyp.Row) []celltyp.Row {
	return pantryc.Drop(rows)
}
