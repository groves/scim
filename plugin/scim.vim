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
    python vimsbt.compile()
endfunction

function! ScimPostCompile()
    let l:oldefm=&efm
    set errorformat=%E\ %#[error]\ %f:%l:\ %m,%C\ %#[error]\ %p^,%-C%.%#,%Z,
       \%W\ %#[warn]\ %f:%l:\ %m,%C\ %#[warn]\ %p^,%-C%.%#,%Z,
       \%-G%.%#
    python vimsbt.loadcompileresults()
    let &errorformat=l:oldefm
endfunction
