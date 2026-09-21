package main

import "loft.local/wickpane/celltyp"
import "loft.local/wickpane/spoolkit"
import "loft.local/wickpane/wicksrc"

func pipeFront(rows []celltyp.Row) []celltyp.Row {
	return wicksrc.Nest(spoolkit.Clip(rows))
}
