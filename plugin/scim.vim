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
    import scim, vimsbt
else:
    vimsbt.exit()
    reload(scim)
    reload(vimsbt)
EOF

function! ScimJumpOver()
    python scim.i.jump(over=True)
endfunction

function! ScimJump()
    python scim.i.jump()
endfunction

function! ScimImport()
    python scim.i.addimport()
endfunction

function! ScimCompile()
    wall
    python vimsbt.run("compile")
endfunction

function! ScimTest()
    wall
    python vimsbt.run("test:compile")
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
    python vimsbt.loadrunresults()
    let &errorformat=l:oldefm
endfunction

function! ScimVimExit()
    python vimsbt.exit()
endfunction

function! ScimBindings()
    " Add mappings, unless the user didn't want this.
    if exists("b:did_scimplugin")
        return
    endif
    let b:did_scimplugin = 1

    if !hasmapto('<Plug>ScimJump')
        map <buffer> <unique> <LocalLeader>j <Plug>ScimJump
    endif
    noremap <buffer> <silent> <unique> <Plug>ScimJump :call ScimJump()<CR>

    if !hasmapto('<Plug>ScimJumpOver')
        map <buffer> <unique> <LocalLeader>J <Plug>ScimJumpOver
    endif
    noremap <buffer> <silent> <unique> <Plug>ScimJumpOver :call ScimJumpOver()<CR>

    if !hasmapto('<Plug>ScimImport')
        map <buffer> <unique> <LocalLeader>i <Plug>ScimImport
    endif
    noremap <buffer> <silent> <unique> <Plug>ScimImport :call ScimImport()<CR>

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

autocmd scim VimLeave * call ScimVimExit()

augroup END
