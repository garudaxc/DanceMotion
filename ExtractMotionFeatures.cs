using UnityEngine;
using System.Collections;

public class ExtractMotionFeatures : MonoBehaviour {

    public Transform[] joints;
    public Transform reference;
    public float CurrentTime = 0.0f;
    
	// Use this for initialization
	void Start () {
        Animation animation = GetComponent<Animation>();
        AnimationState state = animation["Take 001"];
        state.enabled = false;

        Debug.Log("animation length " + state.length);
    }
	
	// Update is called once per frame
	void Update () {
	
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

        state.time = this.CurrentTime;
        state.weight = 1.0f;
        state.enabled = true;

        animation.Sample();

        state.enabled = false;

        string s = FormatVector(joints[0].localPosition);
        Debug.Log("local pos " + s);
        s = FormatVector(joints[0].localEulerAngles);
        Debug.Log("localEulerAngles " + s);
        s = FormatVector(joints[0].position);
        Debug.Log("position " + s);
        s = FormatVector(joints[0].eulerAngles);
        Debug.Log("eulerAngles " + s);
    }
}
