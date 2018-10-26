using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class Utility
{

    public static Dictionary<string, float> LoadMusicInfo(string path) {
        string filename = Path.Combine(path, "info.txt");
        if (!File.Exists(filename)) {
            Debug.LogErrorFormat("can not find file {0}", filename);
            return null;
        }

        string[] lines = File.ReadAllLines(filename);

        Dictionary<string, float> dic = new Dictionary<string, float>();

        foreach (var l in lines) {
            string[] s = l.Split(new char[] { '=' });
            if (s != null) {
                float val = float.Parse(s[1]);
                dic.Add(s[0], val);
            }
        }

        return dic;
    }


    public static GameObject FindGameObjectByName_r(GameObject go, string name) {
        if (go.name.Equals(name)) {
            return go;
        }

        foreach (Transform child in go.transform) {
            var found = FindGameObjectByName_r(child.gameObject, name);
            if (found != null) {
                return found;
            }
        }

        return null;
    }
}
