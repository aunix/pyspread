.\"                                      Hey, EMACS: -*- nroff -*-
.\" First parameter, NAME, should be all caps
.\" Second parameter, SECTION, should be 1-8, maybe w/ subsection
.\" other parameters are allowed: see man(7), man(1)
.TH PYSPREAD 1 "December 12, 2008"
.\" Please adjust this date whenever revising the manpage.
.\"
.\" Some roff macros, for reference:
.\" .nh        disable hyphenation
.\" .hy        enable hyphenation
.\" .ad l      left justify
.\" .ad b      justify to both left and right margins
.\" .nf        disable filling
.\" .fi        enable filling
.\" .br        insert line break
.\" .sp <n>    insert n+1 empty lines
.\" for manpage-specific macros, see man(7)
.SH NAME
pyspread \- A wx.Python-based cross-platform spreadsheet
.SH SYNOPSIS
.B pyspread
.RI [ options ] " files" ...
.br
.B bar
.RI [ options ] " files" ...
.SH DESCRIPTION
.B pyspread
provides an arbitrary size, three-dimensional grid for spreadsheet calculations.
Each grid cell accepts a Python expression.
Python modules are usable from the spreadsheet table without external scripts.
.PP
.SH OPTIONS
No options yet.
.\" These programs follow the usual GNU command line syntax, with long
.\" options starting with two dashes (`-').
.\" A summary of options is included below.
.\" For a complete description, see the Info files.
.\" .TP
.\" .B \-h, \-\-help
.\" Show summary of options.
.\" .TP
.\" .B \-v, \-\-version
.\" Show version of program.
.\" .SH SEE ALSO
.\" .BR bar (1),
.\" .BR baz (1).
.\" .br
.\" The programs are documented fully by
.\" .IR "The Rise and Fall of a Fooish Bar" ,
.\" available via the Info system.
.SH AUTHOR
pyspread was written by Martin Manns.
.PP
This manual page was written by Martin Manns <mmanns@gmx.net>,
for the Debian project (but may be used by others).
