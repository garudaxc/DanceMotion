using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;


public class Logger
{
    public static void Info(string fmt, params System.Object[] args)
    {
        Debug.LogFormat(fmt, args);
    }

    public static void Error(string fmt, params System.Object[] args)
    {
        Debug.LogErrorFormat(fmt, args);
    }

}

