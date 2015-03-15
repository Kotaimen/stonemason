# -*- encoding: utf-8 -*-

"""
    stonemason.util.postprocessing.magickcmd
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Run imagemagick convert command without using subprocess.
"""
import os

from cpython.version cimport PY_MAJOR_VERSION
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cpython.bytes cimport PyBytes_AsString

cdef extern from "wand/MagickWand.h":
    ctypedef struct ImageInfo:
        pass

    ctypedef bint MagickBooleanType

    ctypedef struct ExceptionInfo:
        pass

    ctypedef MagickBooleanType(*MagickCommand)(ImageInfo *, int, char **,
                                               char **, ExceptionInfo *)

    void MagickCoreGenesis(char *path,
                           MagickBooleanType establish_signal_handlers)
    void MagickCoreTerminus()

    ImageInfo *AcquireImageInfo()
    ExceptionInfo *AcquireExceptionInfo()
    ImageInfo *DestroyImageInfo(ImageInfo *image_info)
    ExceptionInfo *DestroyExceptionInfo(ExceptionInfo *exception_info)

    MagickBooleanType ConvertImageCommand(ImageInfo *image_info,
                                          int    argc,
                                          char ** argv,
                                          char ** metadata,
                                          ExceptionInfo *exception_info)

    MagickBooleanType MagickCommandGenesis(ImageInfo *image_info,
                                           MagickCommand command,
                                           int argc,
                                           char ** argv,
                                           char ** metadata,
                                           ExceptionInfo *exception_info)

    char *GetMagickVersion(size_t *version)

cdef char ** to_c_string_array(list str_list) except NULL:
    """Convert a python string list to char **"""
    cdef char ** ret = <char **> PyMem_Malloc(len(str_list) * sizeof(char *))
    for i in range(len(str_list)):
        ret[i] = PyBytes_AsString(str_list[i])
    return ret

def to_string(b):
    if PY_MAJOR_VERSION >= 3:
        return b.decode('ascii')
    else:
        return b

def version():
    cdef size_t v;
    cdef char *version_string = GetMagickVersion(&v)
    return to_string(version_string)

def convert(list args):
    cdef char *cwd
    cdef MagickBooleanType status
    cdef ImageInfo *image_info
    cdef ExceptionInfo *exception_info
    cdef int argc
    cdef char ** argv

    # prepend default convert arguments
    full_args = 'convert -quiet -limit thread 1'.split()
    full_args.extend(args)

    assert all(isinstance(a, str) for a in full_args)

    # python3 only allows convert bytes to c string
    if PY_MAJOR_VERSION >= 3:
        pycwd = os.getcwd().encode('ascii')
        cwd = pycwd
    else:
        pycwd = os.getcwd()
        cwd = pycwd

    if PY_MAJOR_VERSION >= 3:
        full_args = list(arg.encode('ascii') for arg in full_args)

    argc = len(full_args)
    argv = to_c_string_array(full_args)
    MagickCoreGenesis(cwd, False)

    image_info = AcquireImageInfo()
    exception_info = AcquireExceptionInfo()
    try:
        status = MagickCommandGenesis(image_info,
                                      ConvertImageCommand,
                                      argc,
                                      argv,
                                      NULL,
                                      exception_info)
    except Exception:
        return False
    else:
        # XXX: Find a way to capture stdout/stderr output
        return bool(status)
    finally:
        PyMem_Free(argv)
        DestroyExceptionInfo(exception_info)
        DestroyImageInfo(image_info)
        MagickCoreTerminus()
