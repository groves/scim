" Add mappings, unless the user didn't want this.
if !exists("b:did_scimplugin")
    let b:did_scimplugin = 1
    if !hasmapto('<Plug>ScimOpen')
        map <buffer> <unique> <LocalLeader>o <Plug>ScimOpen
    endif
    noremap <buffer> <silent> <unique> <Plug>ScimOpen :call ScimOpen()<CR>

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
endif
