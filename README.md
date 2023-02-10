
# `ct600-fill`

## Overview

This project is retro technology.  It takes as input a file containing UK
corporation tax values in YAML form.  It then takes HMRC's CT600
form in PDF and annotates the computations into the form, outputting a new
PDF.

The output is a PDF file which could in theory be filed with HMRC, if HMRC
were still accepting CT600 forms, which they are mostly not.

## Input file format

If you know what YAML is, the input file is a YAML file containing a
single `ct600` object.  The object's fields have the CT600 box number as
key, and the value is whatever goes in the box.

If you don't what YAML is, the input is a text file, the
first line is `ct600:` subsequent lines are the CT600 box data, each
subsequent line is two spaces followed by the CT600 box number followed by
whatever goes in the CT600 box.

Extra rules:
- Dates should be ISO YYYY-MM-DD format
- Bank sort code is just 6 digits, no dashes.
- For 'put an X in the box if...' boxes, use `true` to indicate an
  X goes in the box.

See `all-values.yaml` for an example which fills in every form box in the
form.

Simple example input:
```
ct600:
  1: Example Biz Ltd.
  2: 12345678
  30: 2020-01-01
  35: 2020-12-31
  70: true
  75: true
  160: 103951
  90: Dog ate the accounts
```

## Things to know

- There is no warranty.
- This is likely incomplete - it does what I want, but you shouldn't be
  playing with this project unless you're prepared to do some work checking
  the values are right for you, and possibly adding extra annotations to the
  form which aren't covered.
- The CT600 form changes periodically, which will invalidate the annotations
  specification.  The annotations spec here has absolute PDF form positions.

## Usage

```
  scripts/ct600-fill --input all-values.yaml --output output.pdf
```