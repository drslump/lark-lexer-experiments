/*!re2c
    re2c:yyfill:enable = 0;
    re2c:indent:string = '  ';
    re2c:indent:top = 1;
    re2c:define:YYCTYPE = char;


    ( "\r"? "\n" )+ ( " " | "\t" )* { NL }
    "/" [^/] ( "\\/" | "\\\\" | [^/\n] )* "/" [imslux]*  { REGEXP }
    "\"" ( "\\\"" | "\\\\" | [^"\n] )* "\"" "i"?  { STRING }
    "!"? [_?]? [a-z][_a-z0-9]*  { RULE }
    "_"? [A-Z] [_A-Z0-9]*       { TOKEN }
    "//" [^\n]+                 { COMMENT }
    [ \t]+                      { WS }
    [\d]+                       { NUMBER }
    "%ignore"                   { IGNORE }
    "%import"                   { IMPORT }
    [+*][?]? | "?" [^a-z]?      { OP }
    "->"                        { TO }
    "."                         { DOT }
    "["                         { LBRA }
    "("                         { LPAR }
    "|"                         { OR }
    "]"                         { RBRA }
    ")"                         { RPAR }
    "~"                         { TILDE }
    ":"                         { COLON }
    [+*][?]? | "?" / [a-z]      { OP }
    *                           { }

*/