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
lex_ascii(const char **cursor) {
    const char *YYMARKER;
    const char *YYCURSOR = *cursor;

    /*!re2c
    re2c:yyfill:enable = 0;
    re2c:indent:string = '    ';
    re2c:indent:top = 1;
    re2c:define:YYCTYPE = char;

    ( "\r"? "\n" )+ ( " " | "\t" )* { *cursor = YYCURSOR; return NL; }
    "/" [^/] ( "\\/" | "\\\\" | [^/\n] )* "/" [imslux]*  { *cursor = YYCURSOR; return REGEXP; }
    "\"" ( "\\\"" | "\\\\" | [^"\n] )* "\"" "i"?  { *cursor = YYCURSOR; return STRING; }
    "!"? [_?]? [a-z][_a-z0-9]*  { *cursor = YYCURSOR; return RULE; }
    "_"? [A-Z] [_A-Z0-9]*       { *cursor = YYCURSOR; return TOKEN; }
    "//" [^\n]+                 { *cursor = YYCURSOR; return COMMENT; }
    [ \t]+                      { *cursor = YYCURSOR; return WS; }
    [\d]+                       { *cursor = YYCURSOR; return NUMBER; }
    "%ignore"                   { *cursor = YYCURSOR; return IGNORE; }
    "%import"                   { *cursor = YYCURSOR; return IMPORT; }
    [+*][?]? | "?" [^a-z]?      { *cursor = YYCURSOR; return OP; }
    "->"                        { *cursor = YYCURSOR; return TO; }
    "."                         { *cursor = YYCURSOR; return DOT; }
    "["                         { *cursor = YYCURSOR; return LBRA; }
    "("                         { *cursor = YYCURSOR; return LPAR; }
    "|"                         { *cursor = YYCURSOR; return OR; }
    "]"                         { *cursor = YYCURSOR; return RBRA; }
    ")"                         { *cursor = YYCURSOR; return RPAR; }
    "~"                         { *cursor = YYCURSOR; return TILDE; }
    ":"                         { *cursor = YYCURSOR; return COLON; }
    [+*][?]? | "?" / [a-z]      { *cursor = YYCURSOR; return OP; }
    *                           { *cursor = YYCURSOR; return Py_None; }

    */
}


static PyObject *
lex(PyObject *self, PyObject *args) {
    PyObject *ret = NULL;
    const PyObject *token;

    const char *stream = NULL;
    int length = 0;
    int ofs = 0;

    if (!PyArg_ParseTuple(args, "s#|i", &stream, &length, &ofs)) {
        goto except;
    }

    const char *cursor = stream + ofs;
    token = lex_ascii(&cursor);

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

    const char *stream = NULL;
    int length = 0;
    int ofs = 0;

    if (!PyArg_ParseTuple(args, "s#|i", &stream, &length, &ofs)) {
        goto except;
    }

    const char *cursor = stream + ofs;

    PyObject *list = PyList_New(0);

    while (cursor-stream < length) {
        token = lex_ascii(&cursor);
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