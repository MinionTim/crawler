#!/usr/bin/env python
# -*- coding' : 'utf-8 -*-
import logging

logger=logging.getLogger()
logger.setLevel(logging.INFO)
ch=logging.StreamHandler()
ch.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
logger.addHandler(ch)