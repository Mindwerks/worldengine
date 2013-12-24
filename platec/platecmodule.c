#include <Python.h>
#include "platecapi.hpp"


static PyObject * platec_create(PyObject *self, PyObject *args)
{
    unsigned int seed;
    unsigned int map_side;
    float sea_level;
    unsigned int erosion_period;
    float folding_ratio;
    unsigned int aggr_overlap_abs;
    float aggr_overlap_rel;
    unsigned int cycle_count;
    unsigned int num_plates;
    if (!PyArg_ParseTuple(args, "IIfIfIfII", &seed, &map_side, &sea_level, &erosion_period,
            &folding_ratio, &aggr_overlap_abs, &aggr_overlap_rel,
            &cycle_count, &num_plates))
        return NULL; 
    srand(seed);

    void *litho = platec_api_create(map_side, sea_level, erosion_period,
            folding_ratio, aggr_overlap_abs, aggr_overlap_rel,
            cycle_count, num_plates);

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
    void *litho;
    if (!PyArg_ParseTuple(args, "l", &litho))
        return NULL; 
    platec_api_destroy(litho);
    return Py_BuildValue("i", 0);
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
     "Create initial plates configuration."},
    {"destroy",  platec_destroy, METH_VARARGS,
     "Release the data for the simulation."},
    {"get_heightmap",  platec_get_heightmap, METH_VARARGS,
     "Get current heightmap."},
    {"step", platec_step, METH_VARARGS,
     "Perform next step of the simulation."},     
    {"is_finished",  platec_is_finished, METH_VARARGS,
     "Is the simulation finished?"},       
    {NULL, NULL, 0, NULL} /* Sentinel */
};

PyMODINIT_FUNC
initplatec(void)
{
    (void) Py_InitModule("platec", PlatecMethods);
}
