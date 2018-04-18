/*!rules:re2c

    re2c:yyfill:enable = 0;
    re2c:indent:string = '    ';
    re2c:indent:top = 1;

    // "#" [^\n]*                                                   { *cursor = YYCURSOR; return Py_BuildValue("s", "COMMENT"); }  // u'#[^\n]*'
    // ( "\r"? "\n" [\t ]* | "#" [^\n]* )+                          { *cursor = YYCURSOR; return Py_BuildValue("s", "_NEWLINE"); }  // u'(?:(?:\r?\n[\t ]*|#[^\n]*))+'
    // [ubf]? "r"? ("\"" ( "\\" . | [^\\\n"] )* "\"" | "'" ( "\\" . | [^\\\n'] )* "'") { *cursor = YYCURSOR; return Py_BuildValue("s", "STRING"); }  // u'(?i)[ubf]?r?("(\\\\.|[^\\\\\n"])*"|\'(\\\\.|[^\\\\\n\'])*\')'
    // [ubf]? "r"? ("\"\"\"" ( "\""? "\""? ("\\" . | [^"\\]) )* "\"\"\"" | "'''" ( "'"? "'"? ("\\" . | [^'\\]) )* "'''") { *cursor = YYCURSOR; return Py_BuildValue("s", "LONG_STRING"); }  // u'(?s)(?i)[ubf]?r?("""("?"?(\\\\.|[^"\\\\]))*"""|\'\'\'(\'?\'?(\\\\.|[^\'\\\\]))*\'\'\')'
    // [1-9] [0-9]* "l"?                                            { *cursor = YYCURSOR; return Py_BuildValue("s", "DEC_NUMBER"); }  // u'(?i)[1-9]\\d*l?'
    // "0x" [0-9a-f]* "l"?                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "HEX_NUMBER"); }  // u'(?i)0x[\\da-f]*l?'
    // "0" "o"? [0-7]* "l"?                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "OCT_NUMBER"); }  // u'(?i)0o?[0-7]*l?'
    // ([0-9]+ | ([0-9]+ [eE] [+\-]? [0-9]+ | ([0-9]+ "." [0-9]+? | "." [0-9]+) ( [eE] [+\-]? [0-9]+ )?)) [jJ] { *cursor = YYCURSOR; return Py_BuildValue("s", "IMAG_NUMBER"); }  // u'(?:(?:[0-9])+|(?:(?:[0-9])+(?:e|E)(?:(?:\\+|\\-))?(?:[0-9])+|(?:(?:[0-9])+\\.(?:(?:[0-9])+)?|\\.(?:[0-9])+)(?:(?:e|E)(?:(?:\\+|\\-))?(?:[0-9])+)?))(?:j|J)'
    // "<DEDENT>"                                                   { *cursor = YYCURSOR; return Py_BuildValue("s", "_DEDENT"); }  // u'\\<DEDENT\\>'
    // "<INDENT>"                                                   { *cursor = YYCURSOR; return Py_BuildValue("s", "_INDENT"); }  // u'\\<INDENT\\>'
    // [0-9]+ [eE] [+\-]? [0-9]+                                    { *cursor = YYCURSOR; return Py_BuildValue("s", "FLOAT"); }  // u'(?:(?:[0-9])+(?:e|E)(?:(?:\\+|\\-))?(?:[0-9])+|(?:(?:[0-9])+\\.(?:(?:[0-9])+)?|\\.(?:[0-9])+)(?:(?:e|E)(?:(?:\\+|\\-))?(?:[0-9])+)?)'
    // ([0-9]+ "." [0-9]+? | "." [0-9]+) ( [eE] [+\-]? [0-9]+ )?    { *cursor = YYCURSOR; return Py_BuildValue("s", "FLOAT"); }  // u'(?:(?:[0-9])+(?:e|E)(?:(?:\\+|\\-))?(?:[0-9])+|(?:(?:[0-9])+\\.(?:(?:[0-9])+)?|\\.(?:[0-9])+)(?:(?:e|E)(?:(?:\\+|\\-))?(?:[0-9])+)?)'
    // [0-9]+                                                       { *cursor = YYCURSOR; return Py_BuildValue("s", "_INT"); }  // u'(?:[0-9])+'
    // ("_" | ([A-Z] | [a-z])) ( ("_" | ([A-Z] | [a-z])) | [0-9] )* { *cursor = YYCURSOR; return Py_BuildValue("s", "NAME"); }  // u'(?:\\_|(?:[A-Z]|[a-z]))(?:(?:(?:\\_|(?:[A-Z]|[a-z]))|[0-9]))*'
    // [\t \f]+                                                     { *cursor = YYCURSOR; return Py_BuildValue("s", "__IGNORE_0"); }  // u'[\t \x0c]+'
    // "\\" [\t \f]* "\r"? "\n"                                     { *cursor = YYCURSOR; return Py_BuildValue("s", "__IGNORE_1"); }  // u'\\\\[\t \x0c]*\r?\n'
    // "@"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__AT"); }  // u'\\@'
    // "("                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__LPAR"); }  // u'\\('
    // ")"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__RPAR"); }  // u'\\)'
    // "def"                                                        { *cursor = YYCURSOR; return Py_BuildValue("s", "__DEF0"); }  // u'def'
    // ":"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__COLON"); }  // u'\\:'
    // ","                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__COMMA"); }  // u'\\,'
    // "*"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__STAR"); }  // u'\\*'
    // "**"                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_1"); }  // u'\\*\\*'
    // "="                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__EQUAL"); }  // u'\\='
    // ";"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__SEMICOLON"); }  // u'\\;'
    // "+="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_2"); }  // u'\\+\\='
    // "-="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_3"); }  // u'\\-\\='
    // "*="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_4"); }  // u'\\*\\='
    // "/="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_5"); }  // u'\\/\\='
    // "%="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_6"); }  // u'\\%\\='
    // "&="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_7"); }  // u'\\&\\='
    // "|="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_8"); }  // u'\\|\\='
    // "^="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_9"); }  // u'\\^\\='
    // "<<="                                                        { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_10"); }  // u'\\<\\<\\='
    // ">>="                                                        { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_11"); }  // u'\\>\\>\\='
    // "**="                                                        { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_12"); }  // u'\\*\\*\\='
    // "//="                                                        { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_13"); }  // u'\\/\\/\\='
    // "print"                                                      { *cursor = YYCURSOR; return Py_BuildValue("s", "__PRINT14"); }  // u'print'
    // ">>"                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_15"); }  // u'\\>\\>'
    // "del"                                                        { *cursor = YYCURSOR; return Py_BuildValue("s", "__DEL16"); }  // u'del'
    // "pass"                                                       { *cursor = YYCURSOR; return Py_BuildValue("s", "__PASS17"); }  // u'pass'
    // "break"                                                      { *cursor = YYCURSOR; return Py_BuildValue("s", "__BREAK18"); }  // u'break'
    // "continue"                                                   { *cursor = YYCURSOR; return Py_BuildValue("s", "__CONTINUE19"); }  // u'continue'
    // "return"                                                     { *cursor = YYCURSOR; return Py_BuildValue("s", "__RETURN20"); }  // u'return'
    // "raise"                                                      { *cursor = YYCURSOR; return Py_BuildValue("s", "__RAISE21"); }  // u'raise'
    // "import"                                                     { *cursor = YYCURSOR; return Py_BuildValue("s", "__IMPORT22"); }  // u'import'
    // "from"                                                       { *cursor = YYCURSOR; return Py_BuildValue("s", "__FROM23"); }  // u'from'
    // "."                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__DOT"); }  // u'\\.'
    // "as"                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__AS24"); }  // u'as'
    // "global"                                                     { *cursor = YYCURSOR; return Py_BuildValue("s", "__GLOBAL25"); }  // u'global'
    // "exec"                                                       { *cursor = YYCURSOR; return Py_BuildValue("s", "__EXEC26"); }  // u'exec'
    // "in"                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__IN27"); }  // u'in'
    // "assert"                                                     { *cursor = YYCURSOR; return Py_BuildValue("s", "__ASSERT28"); }  // u'assert'
    // "if"                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__IF29"); }  // u'if'
    // "elif"                                                       { *cursor = YYCURSOR; return Py_BuildValue("s", "__ELIF30"); }  // u'elif'
    // "else"                                                       { *cursor = YYCURSOR; return Py_BuildValue("s", "__ELSE31"); }  // u'else'
    // "while"                                                      { *cursor = YYCURSOR; return Py_BuildValue("s", "__WHILE32"); }  // u'while'
    // "for"                                                        { *cursor = YYCURSOR; return Py_BuildValue("s", "__FOR33"); }  // u'for'
    // "try"                                                        { *cursor = YYCURSOR; return Py_BuildValue("s", "__TRY34"); }  // u'try'
    // "finally"                                                    { *cursor = YYCURSOR; return Py_BuildValue("s", "__FINALLY35"); }  // u'finally'
    // "with"                                                       { *cursor = YYCURSOR; return Py_BuildValue("s", "__WITH36"); }  // u'with'
    // "except"                                                     { *cursor = YYCURSOR; return Py_BuildValue("s", "__EXCEPT37"); }  // u'except'
    // "lambda"                                                     { *cursor = YYCURSOR; return Py_BuildValue("s", "__LAMBDA38"); }  // u'lambda'
    // "or"                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__OR39"); }  // u'or'
    // "and"                                                        { *cursor = YYCURSOR; return Py_BuildValue("s", "__AND40"); }  // u'and'
    // "not"                                                        { *cursor = YYCURSOR; return Py_BuildValue("s", "__NOT41"); }  // u'not'
    // "<"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__LESSTHAN"); }  // u'\\<'
    // ">"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__MORETHAN"); }  // u'\\>'
    // "=="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_42"); }  // u'\\=\\='
    // ">="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_43"); }  // u'\\>\\='
    // "<="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_44"); }  // u'\\<\\='
    // "<>"                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_45"); }  // u'\\<\\>'
    // "!="                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_46"); }  // u'\\!\\='
    // "is"                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__IS47"); }  // u'is'
    // "|"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__VBAR"); }  // u'\\|'
    // "^"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__CIRCUMFLEX"); }  // u'\\^'
    // "&"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__AMPERSAND"); }  // u'\\&'
    // "<<"                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_48"); }  // u'\\<\\<'
    // "+"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__PLUS"); }  // u'\\+'
    // "-"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__MINUS"); }  // u'\\-'
    // "/"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__SLASH"); }  // u'\\/'
    // "%"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__PERCENT"); }  // u'\\%'
    // "//"                                                         { *cursor = YYCURSOR; return Py_BuildValue("s", "__ANONSTR_49"); }  // u'\\/\\/'
    // "~"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__TILDE"); }  // u'\\~'
    // "["                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__LSQB"); }  // u'\\['
    // "]"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__RSQB"); }  // u'\\]'
    // "{"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__LBRACE"); }  // u'\\{'
    // "}"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__RBRACE"); }  // u'\\}'
    // "`"                                                          { *cursor = YYCURSOR; return Py_BuildValue("s", "__BACKQUOTE"); }  // u'\\`'
    // "class"                                                      { *cursor = YYCURSOR; return Py_BuildValue("s", "__CLASS50"); }  // u'class'
    // "yield"                                                      { *cursor = YYCURSOR; return Py_BuildValue("s", "__YIELD51"); }  // u'yield'

    ( "\r"? "\n" )+ ( " " | "\t" )* { *cursor = YYCURSOR; return NL; }
    "//" [^\n]+                 { *cursor = YYCURSOR; return COMMENT; }
    "/" [^/] ( "\\/" | "\\\\" | [^/\n] )* "/" [imslux]*  { *cursor = YYCURSOR; return REGEXP; }
    "\"" ( "\\\"" | "\\\\" | [^"\n] )* "\"" "i"?  { *cursor = YYCURSOR; return STRING; }
    "!"? [_?]? [a-z][_a-z0-9]*  { *cursor = YYCURSOR; return RULE; }
    "_"? [A-Z] [_A-Z0-9]*       { *cursor = YYCURSOR; return TOKEN; }
    [ \t]+                      { *cursor = YYCURSOR; return WS; }
    [0-9]+                      { *cursor = YYCURSOR; return NUMBER; }
    "%ignore"                   { *cursor = YYCURSOR; return IGNORE; }
    "%import"                   { *cursor = YYCURSOR; return IMPORT; }
    "->"                        { *cursor = YYCURSOR; return TO; }
    "."                         { *cursor = YYCURSOR; return DOT; }
    "["                         { *cursor = YYCURSOR; return LBRA; }
    "("                         { *cursor = YYCURSOR; return LPAR; }
    "|"                         { *cursor = YYCURSOR; return OR; }
    "]"                         { *cursor = YYCURSOR; return RBRA; }
    ")"                         { *cursor = YYCURSOR; return RPAR; }
    "~"                         { *cursor = YYCURSOR; return TILDE; }
    ":"                         { *cursor = YYCURSOR; return COLON; }
    [+*][?]?                    { *cursor = YYCURSOR; return OP; }
    "?" / [^a-z]                { *cursor = YYCURSOR; return OP; }

    *                           { *cursor = YYCURSOR; return Py_None; }

*/

#include "Python.h"

// On module init they'll get initialized with PyString for reuse
static const PyObject *NL;
static const PyObject *REGEXP;
static const PyObject *STRING;
static const PyObject *RULE;
static const PyObject *TOKEN;
static const PyObject *COMMENT;
static const PyObject *WS;
static const PyObject *NUMBER;
static const PyObject *IGNORE;
static const PyObject *IMPORT;
static const PyObject *OP;
static const PyObject *OR;
static const PyObject *TO;
static const PyObject *DOT;
static const PyObject *LBRA;
static const PyObject *LPAR;
static const PyObject *RBRA;
static const PyObject *RPAR;
static const PyObject *TILDE;
static const PyObject *COLON;



static const PyObject *
lex_bytes(const uint8_t **cursor) {
    const uint8_t *YYMARKER;
    const uint8_t *YYCTXMARKER;
    const uint8_t *YYCURSOR = *cursor;

/*!use:re2c

    re2c:define:YYCTYPE = uint8_t;

*/

}

static const PyObject *
lex_utf8(const uint8_t **cursor) {
    const uint8_t *YYMARKER;
    const uint8_t *YYCTXMARKER;
    const uint8_t *YYCURSOR = *cursor;

/*!use:re2c

    re2c:define:YYCTYPE = uint8_t;
    re2c:flags:utf-8 = 1;

*/

}

#if defined Py_UNICODE_WIDE || PY_MAJOR_VERSION >= 3

static const PyObject *
lex_ucs4(const Py_UNICODE **cursor) {
    const Py_UNICODE *YYMARKER;
    const Py_UNICODE *YYCTXMARKER;
    const Py_UNICODE *YYCURSOR = *cursor;

/*!use:re2c

    re2c:define:YYCTYPE = Py_UNICODE;
    re2c:flags:unicode = 1;

*/

}

#else

static const PyObject *
lex_ucs2(const Py_UNICODE **cursor) {
    const Py_UNICODE *YYMARKER;
    const Py_UNICODE *YYCTXMARKER;
    const Py_UNICODE *YYCURSOR = *cursor;

/*!use:re2c

    re2c:define:YYCTYPE = Py_UNICODE;
    re2c:flags:wide-chars = 1;

*/

}

#endif


static PyObject *
lex(PyObject *self, PyObject *args) {
    PyObject *ret = NULL;
    const PyObject *token;

    const uint8_t *stream = NULL;
    int length = 0;
    int ofs = 0;

    if (!PyArg_ParseTuple(args, "s#|i", &stream, &length, &ofs)) {
        goto except;
    }

    const uint8_t *cursor = stream + ofs;
    token = lex_bytes(&cursor);

    ret = Py_BuildValue("iO", cursor-stream, token);
    goto finally;

except:
    assert(PyErr_Occurred());
    Py_XDECREF(ret);
    ret = NULL;

finally:
    return ret;
}


static PyObject *
lexseq(PyObject *self, PyObject *args) {
    PyObject *ret = NULL;
    const PyObject *token;

    const uint8_t *stream = NULL;
    int length = 0;
    int ofs = 0;

    if (!PyArg_ParseTuple(args, "s#|i", &stream, &length, &ofs)) {
        goto except;
    }

    const uint8_t *cursor = stream + ofs;

    PyObject *list = PyList_New(0);

    while (cursor-stream < length) {
        token = lex_bytes(&cursor);
        PyList_Append(list, Py_BuildValue("iO", cursor-stream, token));

        if (token == Py_None) {
            break;
        }
    }

    ret = Py_BuildValue("O", list);
    goto finally;

except:
    assert(PyErr_Occurred());
    Py_XDECREF(ret);
    ret = NULL;

finally:
    return ret;
}


static PyMethodDef lexer_methods[] = {
    {"lex", (PyCFunction)lex, METH_VARARGS, NULL},
    {"lexseq", (PyCFunction)lexseq, METH_VARARGS, NULL},
    {NULL, NULL}
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "_lexer",
        NULL,
        sizeof(struct module_state),
        lexer_methods,
        NULL,
        NULL,
        NULL,
        NULL
};

#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_lexer(void)

#else
#define INITERROR return

void
init_lexer(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule("_lexer", lexer_methods);
#endif

    NL = Py_BuildValue("s", "NL");
    REGEXP = Py_BuildValue("s", "REGEXP");
    STRING = Py_BuildValue("s", "STRING");
    RULE = Py_BuildValue("s", "RULE");
    TOKEN = Py_BuildValue("s", "TOKEN");
    COMMENT = Py_BuildValue("s", "COMMENT");
    WS = Py_BuildValue("s", "WS");
    NUMBER = Py_BuildValue("s", "NUMBER");
    IGNORE = Py_BuildValue("s", "IGNORE");
    IMPORT = Py_BuildValue("s", "IMPORT");
    OP = Py_BuildValue("s", "OP");
    OR = Py_BuildValue("s", "OR");
    TO = Py_BuildValue("s", "TO");
    DOT = Py_BuildValue("s", "DOT");
    LBRA = Py_BuildValue("s", "LBRA");
    LPAR = Py_BuildValue("s", "LPAR");
    RBRA = Py_BuildValue("s", "RBRA");
    RPAR = Py_BuildValue("s", "RPAR");
    TILDE = Py_BuildValue("s", "TILDE");
    COLON = Py_BuildValue("s", "COLON");

    if (module == NULL)
        INITERROR;

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}