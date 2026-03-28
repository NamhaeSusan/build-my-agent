"""Allow running guard as: python -m guard check <path>."""

import sys

from guard.cli import main

sys.exit(main())
