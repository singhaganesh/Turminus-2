from pathlib import Path

path = Path("/app/symmill/Makefile")
text = path.read_text()
needle = "emitmap: $(PROFILE)\n\t@:"
replacement = "emitmap: $(PROFILE)\n\t$(PCFOLD) check $(TARGET) $(SYMAP)"
if needle in text:
    path.write_text(text.replace(needle, replacement))
