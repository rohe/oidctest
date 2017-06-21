#!/usr/bin/env python3
import importlib
import sys
from fedoidc import test_utils

sys.path.insert(0, ".")
config = importlib.import_module(sys.argv[1])

_liss = []
_liss.extend(list(config.FO.values()))
_liss.extend(list(config.OA.values()))
_liss.extend(list(config.IA.values()))
_liss.extend(list(config.EO.values()))

signer, keybundle = test_utils.setup(config.KEY_DEFS, config.TOOL_ISS, _liss,
                                     'ms_path', config.SMS_DEF, 'ms_dir',
                                     base_url=sys.argv[2])
