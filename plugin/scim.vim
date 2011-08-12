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
    python scim.jump(over=True)
endfunction

function! ScimJump()
    python scim.jump()
endfunction

function! ScimOpen()
    python scim.open()
endfunction

function! ScimImport()
    python scim.addimport()
endfunction

function! ScimCompile()
    wall
    python vimsbt.run("compile")
endfunction

function! ScimTest()
    wall
    python vimsbt.run("test:compile")
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

function! ScimOpenClass()
    call ScimLoadCommandT()
    python vim.command('let paths=%s' % scim.list_classes())
    ruby $command_t.show_finder ClassFinder.new(ListScanner.new VIM::evaluate("paths"))
endfunction

function! ScimLoadCommandT()
    if exists("g:loaded_scim_command_t")
        return
    endif
    let g:loaded_scim_command_t = 1
ruby << EOF
require 'command-t/scanner'
require 'command-t/finder/basic_finder'

class ClassFinder < CommandT::BasicFinder
    def open selection, options
        ::VIM::command("python scim.open_full_class('#{selection}')")
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
