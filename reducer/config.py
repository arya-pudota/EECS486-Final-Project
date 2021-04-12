"""reducer development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# File Upload to var/uploads/
reducer_ROOT = pathlib.Path(__file__).resolve().parent.parent
