#!/bin/bash
for i in * ; do wc -l $i; grep %Y $i | wc -l ; echo "" ; done
