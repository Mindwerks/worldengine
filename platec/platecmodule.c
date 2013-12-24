#include <Python.h>
#include "platecapi.hpp"


static PyObject * platec_create(PyObject *self, PyObject *args)
{
    long seed;
    if (!PyArg_ParseTuple(args, "l", &seed))
        return NULL; 
    srand(seed);
    /*size_t id = platec_api_create(10, 512, 0.65f, 2, 60, 0.02f,
                                  1000000, 0.33f);*/
    void *litho = platec_api_create(512,0.65f,60,0.02f,1000000, 0.33f, 2, 10);

    long pointer = (long)litho;
    return Py_BuildValue("l", pointer);
}

static PyObject * platec_step(PyObject *self, PyObject *args)
{
    void *litho;
    if (!PyArg_ParseTuple(args, "l", &litho))
        return NULL; 
    platec_api_step(litho);
    return Py_BuildValue("i", 0);
}

static PyObject * platec_destroy(PyObject *self, PyObject *args)
{

}

PyObject *makelist(float array[], size_t size) {
    PyObject *l = PyList_New(size);
    for (size_t i = 0; i != size; ++i) {
        PyList_SET_ITEM(l, i, Py_BuildValue("f",array[i]));
    }
    return l;
}


static PyObject * platec_get_heightmap(PyObject *self, PyObject *args)
{
    size_t id;
    void *litho;
    if (!PyArg_ParseTuple(args, "l", &litho))
        return NULL; 
    float *hm = platec_api_get_heightmap(litho);

    PyObject* res =  makelist(hm,512*512);
    Py_INCREF(res);
    return res;
}

static PyObject * platec_is_finished(PyObject *self, PyObject *args)
{
    size_t id;
    void *litho;
    if (!PyArg_ParseTuple(args, "l", &litho))
        return NULL; 
    PyObject* res = Py_BuildValue("b",platec_api_is_finished(litho));
    return res;
}


static PyMethodDef PlatecMethods[] = {
    {"create",  platec_create, METH_VARARGS,
     "Create."},
    {"get_heightmap",  platec_get_heightmap, METH_VARARGS,
     "Get heightmap."},
    {"step",  platec_step, METH_VARARGS,
     "Step."},     
    {"is_finished",  platec_is_finished, METH_VARARGS,
     "Finished?."},       
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initplatec(void)
{
    (void) Py_InitModule("platec", PlatecMethods);
//    import_array();
}
