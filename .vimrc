syntax enable
set cindent
set smartindent
set ai
set bg=dark
set showmatch
set ruler
set incsearch
set hlsearch
set ts=4
set backspace=indent,eol,start

" set tags=tags;

" 光标左右键用于切换 tab
map <left> <ESC>:tabp<RETURN>
map <right> <ESC>:tabn<RETURN>
map <up> <ESC><C-W>k
map <down> <ESC><C-W>j

if has("cscope")
	set csto=0
	set cst
	set nocsverb
	if filereadable("cscope.out")
		cs add cscope.out
	endif
	set csverb
endif

