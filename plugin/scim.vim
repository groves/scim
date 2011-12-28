" Vim plugin for navigating to and importing Scala and Java classes

if exists("g:loaded_scim")
    finish
endif
let g:loaded_scim = 1

python << EOF
import sys, vim
scimdir = vim.eval('expand("<sfile>:h")')
if not scimdir in sys.path:
    sys.path.append(scimdir)
    import scim
else:
    try:
        scim.sbtrun("exit")
    except:
        pass
    reload(scim)
EOF

function! ScimJumpOver()
    python scim.i.jump(over=True)
endfunction

function! ScimJumpCurrent()
    python scim.i.jump()
endfunction

function! ScimImport()
    python scim.i.addimport()
endfunction

function! ScimClearLookupCache()
    python del scim.i.choices[scim.i.lastchoice]
    python print "Cleared %s. Try again!" % scim.i.lastchoice
endfunction

function! ScimRun(cmd)
    wall
    python scim.sbtrun(vim.eval("a:cmd"))
endfunction

function! ScimOpenClass()
    call s:ScimLoadCommandT()
    python vim.command('let paths=%s' % scim.i.list_classes())
    ruby $command_t.show_finder ClassFinder.new(ListScanner.new VIM::evaluate("paths"))
endfunction

function! ScimPostRun()
    let l:oldefm=&efm
    set errorformat=%E\ %#[error]\ %f:%l:\ %m,%C\ %#[error]\ %p^,%-C%.%#,%Z,
       \%W\ %#[warn]\ %f:%l:\ %m,%C\ %#[warn]\ %p^,%-C%.%#,%Z,
       \%-G%.%#
    cfile /tmp/sbtout
    let &errorformat=l:oldefm
    redraw
endfunction

function! ScimBindings()
    " Add mappings, unless the user didn't want this.
    if exists("b:did_scimplugin")
        return
    endif
    let b:did_scimplugin = 1

    if !hasmapto('<Plug>ScimJumpCurrent')
        map <buffer> <unique> <LocalLeader>j <Plug>ScimJumpCurrent
    endif
    noremap <buffer> <unique> <Plug>ScimJumpCurrent :call ScimJumpCurrent()<CR>

    if !hasmapto('<Plug>ScimJumpOver')
        map <buffer> <unique> <LocalLeader>J <Plug>ScimJumpOver
    endif
    noremap <buffer> <unique> <Plug>ScimJumpOver :call ScimJumpOver()<CR>

    if !hasmapto('<Plug>ScimImport')
        map <buffer> <unique> <LocalLeader>i <Plug>ScimImport
    endif
    noremap <buffer> <unique> <Plug>ScimImport :call ScimImport()<CR>

    if !hasmapto('<Plug>ScimCompile')
        map <buffer> <unique> <LocalLeader>c <Plug>ScimCompile
    endif
    noremap <buffer> <silent> <unique> <Plug>ScimCompile :call ScimCompile()<CR>

    if !hasmapto('<Plug>ScimTest')
        map <buffer> <unique> <LocalLeader>u <Plug>ScimTest
    endif
    noremap <buffer> <silent> <unique> <Plug>ScimTest :call ScimTest()<CR>

    if !hasmapto('<Plug>ScimOpenClass')
        map <buffer> <unique> <LocalLeader>o <Plug>ScimOpenClass
    endif
    noremap <buffer> <silent> <unique> <Plug>ScimOpenClass :call ScimOpenClass()<CR>

    if !hasmapto('<Plug>ScimClearLookupCache')
        map <buffer> <unique> <LocalLeader>r <Plug>ScimClearLookupCache
    endif
    noremap <buffer> <silent> <unique> <Plug>ScimClearLookupCache :call ScimClearLookupCache()<CR>
endfunction

function! s:ScimLoadCommandT()
    if exists("g:loaded_scim_command_t")
        return
    endif
    let g:loaded_scim_command_t = 1
ruby << EOF
require 'command-t/scanner'
require 'command-t/finder/basic_finder'

class ClassFinder < CommandT::BasicFinder
    def open selection, options
        ::VIM::command("python scim.i.open('#{selection}')")
    end

    def bufferBased?
        false
    end
end

class ListScanner < CommandT::Scanner
    attr_accessor :paths
    def initialize paths
        @paths = paths
    end
end
EOF
endfunction

augroup scim
autocmd!

autocmd scim VimLeave * call s:ScimRun("exit")

augroup END
