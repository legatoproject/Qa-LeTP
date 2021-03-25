# Minimal makefile for Sphinx documentation
#
SPHINXOPTS    =
SPHINXBUILD   = LD_LIBRARY_PATH=$$LEGATO_ROOT/build/localhost/framework/lib/:$$LD_LIBRARY_PATH python3 -msphinx
SOURCEDIR     = source
BUILDDIR      = _sphinx

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
pdf: default
	make -C latex
	ln -s $(CURDIR)/latex/refman.pdf letp.pdf

clean:
	rm -rf html
	rm -rf latex
	rm -f ../../../build/doc/letp/html
	rm -rf _sphinx
	rm letp.pdf