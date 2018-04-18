REGEXP: "/" ( /\\[\\\/]/ | /[^\\\/\n]/ )+ "/" /[imslux]*/
NL: ( "\r"? "\n" )+ /\s*/
STRING: "\"" ( /\\[\\"]/ | /[^\\"\n]/ )* "\"" "i"?
RULE: "!"? /[_?]/? /[a-z][_a-z0-9]*/
TOKEN: "_"? /[A-Z][_A-Z0-9]*/
WS: /[ \t]+/
NUMBER: /\d+/
_IGNORE: "%ignore"
_IMPORT: "%import"
OP: /[+*]/ "?"? | "?"
_TO: "->"
_DOT: "."
_LBRA: "["
_LPAR: "("
_OR: "|"
_RBRA: "]"
_RPAR: ")"
TILDE: "~"
_COLON: ":"