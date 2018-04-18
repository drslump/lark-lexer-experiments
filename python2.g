// Python 2 grammar for Lark

// NOTE: Work in progress!!! (XXX TODO)
// This grammar should parse all python 2.x code successfully,
// but the resulting parse-tree is still not well-organized.

// Adapted from: https://docs.python.org/2/reference/grammar.html
// Adapted by: Erez Shinan

// Start symbols for the grammar:
//       single_input is a single interactive statement;
//       file_input is a module or sequence of commands read from an input file;
//       eval_input is the input for the eval() and input() functions.
// NB: compound_stmt in single_input is followed by extra _NEWLINE!
single_input: _NEWLINE | simple_stmt | compound_stmt _NEWLINE
?file_input: (_NEWLINE | stmt)*
eval_input: testlist _NEWLINE?

decorator: "@" dotted_name [ "(" [arglist] ")" ] _NEWLINE
decorators: decorator+
decorated: decorators (classdef | funcdef)
funcdef: "def" NAME "(" parameters ")" ":" suite
parameters: [paramlist]
paramlist: param ("," param)* ["," [star_params ["," kw_params] | kw_params]]
           | star_params ["," kw_params]
           | kw_params
star_params: "*" NAME
kw_params: "**" NAME
param: fpdef ["=" test]
fpdef: NAME | "(" fplist ")"
fplist: fpdef ("," fpdef)* [","]

?stmt: simple_stmt | compound_stmt
?simple_stmt: small_stmt (";" small_stmt)* [";"] _NEWLINE
?small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt
          |  import_stmt | global_stmt | exec_stmt | assert_stmt)
expr_stmt: testlist augassign (yield_expr|testlist) -> augassign2
         | testlist ("=" (yield_expr|testlist))+    -> assign
         | testlist

augassign: ("+=" | "-=" | "*=" | "/=" | "%=" | "&=" | "|=" | "^=" | "<<=" | ">>=" | "**=" | "//=")
// For normal assignments, additional restrictions enforced by the interpreter
print_stmt: "print" ( [ test ("," test)* [","] ] | ">>" test [ ("," test)+ [","] ] )
del_stmt: "del" exprlist
pass_stmt: "pass"
?flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
break_stmt: "break"
continue_stmt: "continue"
return_stmt: "return" [testlist]
yield_stmt: yield_expr
raise_stmt: "raise" [test ["," test ["," test]]]
import_stmt: import_name | import_from
import_name: "import" dotted_as_names
import_from: "from" ("."* dotted_name | "."+) "import" ("*" | "(" import_as_names ")" | import_as_names)
?import_as_name: NAME ["as" NAME]
?dotted_as_name: dotted_name ["as" NAME]
import_as_names: import_as_name ("," import_as_name)* [","]
dotted_as_names: dotted_as_name ("," dotted_as_name)*
dotted_name: NAME ("." NAME)*
global_stmt: "global" NAME ("," NAME)*
exec_stmt: "exec" expr ["in" test ["," test]]
assert_stmt: "assert" test ["," test]

?compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
if_stmt: "if" test ":" suite ("elif" test ":" suite)* ["else" ":" suite]
while_stmt: "while" test ":" suite ["else" ":" suite]
for_stmt: "for" exprlist "in" testlist ":" suite ["else" ":" suite]
try_stmt: ("try" ":" suite ((except_clause ":" suite)+ ["else" ":" suite] ["finally" ":" suite] | "finally" ":" suite))
with_stmt: "with" with_item ("," with_item)*  ":" suite
with_item: test ["as" expr]
// NB compile.c makes sure that the default except clause is last
except_clause: "except" [test [("as" | ",") test]]
suite: simple_stmt | _NEWLINE _INDENT _NEWLINE? stmt+ _DEDENT _NEWLINE?

// Backward compatibility cruft to support:
// [ x for x in lambda: True, lambda: False if x() ]
// even while also allowing:
// lambda x: 5 if x else 2
// (But not a mix of the two)
testlist_safe: old_test [("," old_test)+ [","]]
old_test: or_test | old_lambdef
old_lambdef: "lambda" [paramlist] ":" old_test

?test: or_test ["if" or_test "else" test] | lambdef
?or_test: and_test ("or" and_test)*
?and_test: not_test ("and" not_test)*
?not_test: "not" not_test | comparison
?comparison: expr (comp_op expr)*
comp_op: "<"|">"|"=="|">="|"<="|"<>"|"!="|"in"|"not" "in"|"is"|"is" "not"
?expr: xor_expr ("|" xor_expr)*
?xor_expr: and_expr ("^" and_expr)*
?and_expr: shift_expr ("&" shift_expr)*
?shift_expr: arith_expr (("<<"|">>") arith_expr)*
?arith_expr: term (("+"|"-") term)*
?term: factor (("*"|"/"|"%"|"//") factor)*
?factor: ("+"|"-"|"~") factor | power
?power: molecule ["**" factor]
// _trailer: "(" [arglist] ")" | "[" subscriptlist "]" | "." NAME
?molecule: molecule "(" [arglist] ")" -> func_call
         | molecule "[" [subscriptlist] "]" -> getitem
         | molecule "." NAME -> getattr
         | atom
?atom: "(" [yield_expr|testlist_comp] ")" -> tuple
    |   "[" [listmaker] "]"
    |   "{" [dictorsetmaker] "}"
    |   "`" testlist1 "`"
    |   "(" test ")"
    |   NAME | number | string+
listmaker: test ( list_for | ("," test)* [","] )
?testlist_comp: test ( comp_for | ("," test)+ [","] | ",")
lambdef: "lambda" [paramlist] ":" test
?subscriptlist: subscript ("," subscript)* [","]
subscript: "." "." "." | test | [test] ":" [test] [sliceop]
sliceop: ":" [test]
?exprlist: expr ("," expr)* [","]
?testlist: test ("," test)* [","]
dictorsetmaker: ( (test ":" test (comp_for | ("," test ":" test)* [","])) | (test (comp_for | ("," test)* [","])) )

classdef: "class" NAME ["(" [testlist] ")"] ":" suite

arglist: (argument ",")* (argument [","]
                         | star_args ["," kw_args]
                         | kw_args)

star_args: "*" test
kw_args: "**" test


// The reason that keywords are test nodes instead of NAME is that using NAME
// results in an ambiguity. ast.c makes sure it's a NAME.
argument: test [comp_for] | test "=" test

list_iter: list_for | list_if
list_for: "for" exprlist "in" testlist_safe [list_iter]
list_if: "if" old_test [list_iter]

comp_iter: comp_for | comp_if
comp_for: "for" exprlist "in" or_test [comp_iter]
comp_if: "if" old_test [comp_iter]

testlist1: test ("," test)*

yield_expr: "yield" [testlist]

number: DEC_NUMBER | HEX_NUMBER | OCT_NUMBER | FLOAT | IMAG_NUMBER
string: STRING | LONG_STRING
// Tokens

COMMENT: /#[^\n]*/
_NEWLINE: ( /\r?\n[\t ]*/ | COMMENT )+

%ignore /[\t \f]+/  // WS
%ignore /\\[\t \f]*\r?\n/   // LINE_CONT
%ignore COMMENT

STRING : /[uUbBfF]?[rR]?("(\\.|[^\\\n"])*"|'(\\.|[^\\\n'])*')/
LONG_STRING.2: /[uUbBfF]?[rR]?("""("?"?(\\.|[^"\\]))*"""|'''('?'?(\\.|[^'\\]))*''')/s

DEC_NUMBER: /[1-9]\d*[lL]?/
HEX_NUMBER: /0[xX][\da-fA-F]*[lL]?/
OCT_NUMBER: /0[oO]?[0-7]*[lL]?/
%import common.FLOAT -> FLOAT
%import common.INT -> _INT
%import common.CNAME -> NAME
IMAG_NUMBER: (_INT | FLOAT) ("j"|"J")

_DEDENT: "<DEDENT>"
_INDENT: "<INDENT>"
