using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEngine;
public class MotionSimilarity
{

    class FrameData
    {
        public string name;

        public int numBeats;

        public Quaternion[,] q;
    }

    public MotionSimilarity() {

    }

    public void Do() {
        LoadMotion();
    }

    void LoadMotion() {
        var path = "Assets/DanceMotion/resource/";

        var dirs = Directory.GetDirectories(path);

        List<FrameData> frameData = new List<FrameData>();

        foreach (var d in dirs) {
            var songName = d.Substring(path.Length);
            var resName = string.Format("{0}/{1}.prefab", d, songName);

            var res = (GameObject)AssetDatabase.LoadAssetAtPath(resName, typeof(GameObject));
            Debug.Log("load " + resName);
            var inst = GameObject.Instantiate(res);

            string[] jointName = new string[] {
                "Bip01 L Thigh",
                "Bip01 R Thigh",
                "Bip01 L Calf",
                "Bip01 R Calf",
                "Bip01 L UpperArm",
                "Bip01 R UpperArm",
                "Bip01 L Forearm",
                "Bip01 R Forearm",
            };

            var weights = new float[] {
                1.0000f,
                1.0000f,
                0.0901f,
                0.0901f,
                0.7884f,
                0.7884f,
                0.0247f,
                0.0247f,
            };

            Transform[] joints = new Transform[jointName.Length];

            for (int i = 0; i < jointName.Length; i++) {
                GameObject o = Utility.FindGameObjectByName_r(inst, jointName[i]);
                if (o == null) {
                    Debug.LogFormat("can not found gameobject {0}", jointName[i]);
                } else {
                    joints[i] = o.transform;
                }
            }
            
            Animation animation = inst.GetComponent<Animation>();
            var musicInfo = Utility.LoadMusicInfo(d);

            float bpm = musicInfo["bpm"];
            float enterTime = musicInfo["et"];
            float motionStart = musicInfo["start"];
            float motionEnd = musicInfo["end"];
            
            // 一拍中分6个window，window间50%重叠，每个window采样6次
            // 一拍共6 * 3.5=21个采样点
            float beat = 60.0f / bpm;

            float start = Math.Max(enterTime, motionStart);
            start = start - (start - enterTime) % beat + beat;
            float end = motionEnd - (motionEnd - enterTime) % beat;
            int numBeats = (int)((end - start) / beat);
            
            Debug.LogFormat("start {0} {1} {2} {3}", start, (start - enterTime) / beat, end, (end-enterTime) / beat);
            Debug.LogFormat("numbeats {0}", (end - start) / beat);
            float dt = beat / 21.0f;

            AnimationState state = animation["Take 001"];
            state.weight = 1.0f;
            state.enabled = true;
            
            float invdt = 1.0f / dt;

            FrameData data = new FrameData {
                name = songName,
                numBeats = numBeats,
                q = new Quaternion[numBeats * 7, joints.Length]
            };

            int numSamples = numBeats * 7;

            for (int i = 0; i < numSamples; i++) {
                float time = start + dt * i;
                state.time = time;
                animation.Sample();
                
                for (int j = 0; j < joints.Length; j++) {
                    data.q[i, j] = joints[j].localRotation;                    
                }
            }

            frameData.Add(data);

            GameObject.DestroyImmediate(inst);

            break;
        }
    }


    float SegmentSimilarity() {

        return 0.0f;
    }

    void CalcMotionSimilarity() {

    }
}
