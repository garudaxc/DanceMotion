using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
public class MotionSimilarity
{
    public static readonly int NumSamplesPerBeat = 7;
    List<FrameData> frames_;
    List<float> cost_esti_;

    public class FrameData
    {
        public string name;
        public int numBeats;
        public float startTime;
        public float beatTime;
        public Quaternion[,] q;
    }

    public class MotionFrame
    {
        public float minCost;
        public int index0;
        public int beat0;
        public int index1;
        public int beat1;
    }

    public MotionSimilarity() {
    }

    public FrameData GetFrameData(int index) {
        return frames_[index];
    }

    public List<float> GetCostEstimate() {
        return cost_esti_;
    }

    public MotionFrame GetMinimunCostFrame() {
        int index = IndexOfMinimum(cost_esti_);
        var frame = MotionFrameByIndex(index);
        return frame;
    }

    public MotionFrame MotionFrameByIndex(int globalIndex) {
        int frameIndex = 0;
        int i = 0;
        int j = i + 1;
        bool run = true;
        for (; i < frames_.Count && run; i++) {
            j = i + 1;
            for (; j < frames_.Count; j++) {
                int f = frames_[i].numBeats * frames_[j].numBeats;
                if ((frameIndex + f) > globalIndex) {
                    run = false;
                    break;
                } else {
                    frameIndex += f;
                }
            }
        }

        int m = (globalIndex - frameIndex) / frames_[j].numBeats;
        int n = (globalIndex - frameIndex) % frames_[j].numBeats;

        var frame = new MotionFrame() {
            minCost = cost_esti_[globalIndex],
            index0 = i - 1,
            index1 = j,
            beat0 = m,
            beat1 = n,
        };

        return frame;
    }

    public List<FrameData> IndexMotionSeg() {
        var path = "Assets/DanceMotion/resource/";
        var dirs = Directory.GetDirectories(path);
        Array.Sort(dirs);

        List<FrameData> frameData = new List<FrameData>();

        int count = 0;
        foreach (var d in dirs) {
            var songName = d.Substring(path.Length);

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

            var frame = new FrameData() {
                name = songName,
                numBeats = numBeats,
                beatTime = beat,
                startTime = start,
            };

            frameData.Add(frame);

            count++;
            if (count > 3) {
                break;
            }
        }

        return frameData;
    }

    public void Do() {
        CalcMotionSimilarity();
    }

    void CalcMotionSimilarity() {
        frames_ = IndexMotionSeg();

        foreach (var frame in frames_) {
            var resName = string.Format("Assets/DanceMotion/resource/{0}/{0}.prefab", frame.name);

            Debug.Log("load " + resName);

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
            AnimationState state = animation["Take 001"];
            state.weight = 1.0f;
            state.enabled = true;

            float dt = frame.beatTime / (float)NumSamplesPerBeat;
            float invdt = 1.0f / dt;

            int numSamples = frame.numBeats * NumSamplesPerBeat;
            Debug.LogFormat("name {0} numSamples {1}", frame.name, numSamples);

            frame.q = new Quaternion[frame.numBeats * NumSamplesPerBeat, joints.Length];

            for (int i = 0; i < numSamples; i++) {
                float time = frame.startTime + dt * i;
                state.time = time;
                animation.Sample();

                for (int j = 0; j < joints.Length; j++) {
                    frame.q[i, j] = joints[j].localRotation;
                }
            }

            GameObject.DestroyImmediate(inst);
        }

        cost_esti_ = new List<float>();
        //var file = File.OpenWrite();
        StreamWriter sw = new StreamWriter("MotionCost.txt");
        for (int i = 0; i < frames_.Count; i++) {
            for (int j = i + 1; j < frames_.Count; j++) {
                var data0 = frames_[i];
                var data1 = frames_[j];
                //Debug.LogFormat("{0}, {1}, {2}, {3}, {4}", minCost, i, j, data0, data1);
                for (int m = 0; m < data0.numBeats; m++) {
                    for (int n = 0; n < data1.numBeats; n++) {
                        float cost = MotionSeqCost(data0, m, data1, n);
                        cost_esti_.Add(cost);

                        //string str = string.Format("{0}_{1},{2}_{3},{4}", data0.name, m, data1.name, n, cost);
                        //sw.WriteLine(str);
                    }
                }
            }
        }

        //Debug.LogFormat("{0}, {1}, {2}, {3}, {4}", minCost, f.index0, f.index1, f.beat0, f.beat1);
        //int ii = IndexOfMinimum(allCost);
        //Debug.LogFormat("min cost {0} global index {1} total {2}", allCost[ii], ii, allCost.Count);
        //var ff = MotionFrameByIndex(ii);
        //Debug.LogFormat("{0}, {1}, {2}, {3}, {4}", minCost, ff.index0, ff.index1, ff.beat0, ff.beat1);
        //allCost.Sort();
        //Debug.LogFormat("{0} {1}", allCost[0], allCost[allCost.Count - 1]);

        sw.Close();
        Debug.Log("Done!");
    }

    static int IndexOfMaximum<T>(IList<T> l) where T : IComparable {
        if (l.Count == 0) {
            return -1;
        }

        int index = 0;
        T maxinum = l[index];
        for (int i = 1; i < l.Count; i++) {
            if (l[i].CompareTo(maxinum) > 0) {
                index = i;
                maxinum = l[i];
            }
        }
        return index;
    }

    static int IndexOfMinimum<T>(IList<T> l) where T : IComparable {
        if (l.Count == 0) {
            return -1;
        }

        int index = 0;
        T minimum = l[index];
        for (int i = 1; i < l.Count; i++) {
            if (l[i].CompareTo(minimum) < 0) {
                index = i;
                minimum = l[i];
            }
        }
        return index;
    }


    public static int FindLargestAfter<T>(IList<T> l, int serialNum, T NegativeInfinity, T infinity) where T : IComparable {
        if (l.Count == 0) {
            return -1;
        }

        int index = -1;
        T serialMax = infinity;
        for (int i = 0; i < serialNum + 1; i++) {
            int currIndex = -1;
            T cmax = NegativeInfinity;
            for (int j = 0; j < l.Count; j++) {
                if (l[j].CompareTo(cmax) > 0 && l[j].CompareTo(serialMax) < 0) {
                    currIndex = j;
                    cmax = l[j];
                }
            }

            serialMax = cmax;
            index = currIndex;
        }

        return index;
    }


    public static int FindSmallestAfter<T>(IList<T> l, int serialNum, T NegativeInfinity, T infinity) where T : IComparable {
        if (l.Count == 0) {
            return -1;
        }

        int index = -1;
        T serialMin = NegativeInfinity;
        for (int i = 0; i < serialNum + 1; i++) {
            int currIndex = -1;
            T cmin = infinity;
            for (int j = 0; j < l.Count; j++) {
                if (l[j].CompareTo(cmin) < 0 && l[j].CompareTo(serialMin) > 0) {
                    currIndex = j;
                    cmin = l[j];
                }
            }

            serialMin = cmin;
            index = currIndex;
        }

        return index;
    }



    static float MotionSeqCost(FrameData d0, int seg0, FrameData d1, int seg1) {
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

        float cost = 0.0f;
        for (int i = 0; i < NumSamplesPerBeat; i++) {
            for (int j = 0; j < weights.Length; j++) {
                float omiga = Quaternion.Angle(
                    d0.q[seg0 * NumSamplesPerBeat + i, j],
                    d1.q[seg1 * NumSamplesPerBeat + i, j]);

                cost += Math.Abs(omiga) * weights[j];
            }
        }

        return cost;
    }

}
