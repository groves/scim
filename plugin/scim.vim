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
    reload(scim)
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
