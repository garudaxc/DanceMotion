using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

public class ExtractMotionFeatures : MonoBehaviour {

    Transform[] joints;
    Transform reference;
    float CurrentTime = 0.0f;
    string OutputPath;

    new AudioSource audio;
    
	// Use this for initialization
	void Start () {
        //Animation animation = GetComponent<Animation>();
        //AnimationState state = animation["Take 001"];
        //state.enabled = false;

        //Debug.Log("animation length " + state.length);

        audio = gameObject.GetComponent<AudioSource>();
    }

    void OnGUI() {
        var t = string.Format("{0:F2}", audio.time);
        GUI.Label(new Rect(0.0f, 0.0f, 100.0f, 100.0f), t);
    }

    static string FormatVector(Vector3 v) {
        string s = string.Format("{0:f7}, {1:f7}, {2:f7}", v.x, v.y, v.z);
        return s;
    }

    public void ExtractFeatures() {
        Animation animation = GetComponent<Animation>();
        //foreach(AnimationState state in animation) {
        //    Debug.Log("animation state " + state.name);
        //}

        AnimationState state = animation["Take 001"];
        //Debug.Log("time " + state.time);
        
        state.weight = 1.0f;
        state.enabled = true;

        //string s = FormatVector(joints[0].localPosition);
        //Debug.Log("local pos " + s);
        //s = FormatVector(joints[0].localEulerAngles);
        //Debug.Log("localEulerAngles " + s);
        //s = FormatVector(joints[0].position);
        //Debug.Log("position " + s);
        //s = FormatVector(joints[0].eulerAngles);
        //Debug.Log("eulerAngles " + s);

        float dt = 0.0333333f;

        Quaternion[] prevRot = new Quaternion[joints.Length];
        // init rotation to first frame
        state.time = 0.0f;
        animation.Sample();
        for (int i = 0; i < joints.Length; i++) {
            prevRot[i] = joints[i].localRotation;
        }

        var featureData = new List<float>();
        int numSamples = (int)(state.length / dt);
        
        for (int i = 0; i < numSamples; i++) {
            float time = dt * i;
            state.time = time;
            animation.Sample();

            featureData.Add(time);
            Vector3 refPos = reference.position;
            for (int j = 0; j < joints.Length; j++) {
                float dis = (joints[j].position - refPos).magnitude;
                Quaternion q = joints[j].localRotation;
                float omiga = Quaternion.Angle(q, prevRot[j]);
                prevRot[j] = q;

                featureData.Add(dis);
                featureData.Add(omiga);
            }
        }

        Debug.LogFormat("feature data {0} frames {1} joints {2} floats", numSamples, joints.Length, numSamples * joints.Length * 2);

        FileStream fs = new FileStream(OutputPath, FileMode.Create, FileAccess.Write);
        BinaryWriter bw = new BinaryWriter(fs);

        bw.Write(numSamples);
        foreach (var d in featureData) {
            bw.Write(d);
        }

        bw.Close();
        fs.Close();

        Debug.LogFormat("write file {0}", OutputPath);
    }
}
