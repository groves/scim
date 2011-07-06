Scim adds some simple functionality to Vim to make writing Scala easier. It scans directories of
Javadoc, Scaladoc, Java source, and Scala source, and allows lookup of the classes it finds there.
From that lookup, it handles adding imports for those classes, and navigating to either the source
or documentation of that class.

Installation
============
Install [Pathogen](http://www.vim.org/scripts/script.php?script_id=2332) and check this repo out
into your bundles directory eg `cd ~/.vim/bundles && git clone git://github.com/groves/scim.git`.

Usage
=====
Add directories of source and documentation to `g:scim_locations` in your `.vimrc`. Here's mine:

    let g:scim_locations = [
    \ "~/dev/docs/jdk6",
    \ "~/dev/docs/scala-2.9.0.1",
    \ "~/dev/fisy/src/main/java",
    \ "~/dev/ionic/src/main/scala"
    \ ]

With that lookup table hit `<LocalLeader>j` to jump to the documentation or source for the classname
under the curor, or hit `<LocalLeader>i` to import the classname under the cursor.

Scim rescans its locations if it can't find the classname or if `g:scim_locations` has changed since
the last time it ran. That should mean that you never have to ask it to manually rescan.

