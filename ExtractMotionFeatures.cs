using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

public class ExtractMotionFeatures : MonoBehaviour
{

    Transform[] joints;
    Transform reference;

    new AudioSource audio;
    public float StartTime = 0.0f;
    public float BeatTime = 1.0f;

    Animation anim_;
    AnimationState state_;

    // Use this for initialization
    void Start() {
        //Animation animation = GetComponent<Animation>();
        //AnimationState state = animation["Take 001"];
        //state.enabled = false;

        //Debug.Log("animation length " + state.length);

        //audio = gameObject.GetComponent<AudioSource>();
        //Animation animation = GetComponent<Animation>();
        //AnimationState state = animation["Take 001"];

        //audio.time = StartTime;
        //state.time = StartTime;
    }

    public void Init() {
        anim_ = GetComponent<Animation>();
        anim_.Stop();

        state_ = anim_["Take 001"];
        state_.time = StartTime;

        // 播两秒
        float speed = BeatTime / 2.0f;
        state_.speed = speed;
        anim_.Play();
    }

    void Update() {
        if (state_ != null) {
            if (state_.time > (StartTime + BeatTime)) {
                anim_.Stop();
            }
        }
    }

    void OnGUI() {
        if (audio != null) {
            var t = string.Format("{0:F2}", audio.time);
            GUI.Label(new Rect(0.0f, 0.0f, 100.0f, 100.0f), t);
        }
    }

    static string FormatVector(Vector3 v) {
        string s = string.Format("{0:f7}, {1:f7}, {2:f7}", v.x, v.y, v.z);
        return s;
    }

}
