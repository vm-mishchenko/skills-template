.PHONY: setup clean

setup:
	@python3 -m venv .venv
	@.venv/bin/python -m pip install --upgrade pip
	@.venv/bin/python -m pip install -e .
	@echo ""
	@echo "Add to ~/.zshrc:"
	@echo '  export PATH="$(CURDIR)/bin:$(CURDIR)/.venv/bin:$$PATH"'
	@echo "Reload shell:"
	@echo "  source ~/.zshrc"

clean:
	rm -rf .venv .cursor-rules build dist src/*.egg-info
